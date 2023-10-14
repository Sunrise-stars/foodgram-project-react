from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient)
from users.models import User
from favorites.models import Favorite

from carts.models import Cart


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class EditRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class EditRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = EditRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'ingredients','tags','image','name','text','cooking_time']

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        tags = data.get('tags', [])
        cooking_time = data.get('cooking_time', 0)

        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Должен быть выбран хотя бы один ингредиент!'
            })

        if not tags:
            raise serializers.ValidationError({
                'tags': 'Должен быть выбран хотя бы один тег!'
            })

        ingredient_ids = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными!'
                })
            ingredient_ids.add(ingredient_id)

        if cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 1!'
            })

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user

        recipe = Recipe.objects.create(author=author, **validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                recipe=recipe,
                amount=ingredient_data['amount']
            )

        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()

        for ingredient_data in validated_data.pop('ingredients'):
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                recipe=instance,
                amount=ingredient_data['amount']
            )

        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))

        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')

        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return not (request is None or request.user.is_anonymous) and Favorite.objects.filter(user=request.user,
                                                                                              recipe_id=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return not (request is None or request.user.is_anonymous) and Cart.objects.filter(user=request.user,
                                                                                          recipe_id=obj).exists()
