from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from carts.models import Cart
from django.db import transaction
from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from subscriptions.models import Subscription
from users.models import User


class SubscriptionUtils:
    @staticmethod
    def check_subscription(user, author):
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=user, author=author
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return SubscriptionUtils.check_subscription(user, obj)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class EditRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class EditRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = EditRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        tags = data.get('tags', [])
        cooking_time = data.get('cooking_time', 0)

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Должен быть выбран хотя бы один ингредиент!'}
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Должен быть выбран хотя бы один тег!'}
            )

        ingredient_ids = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_amount = float(ingredient['amount'])

            if ingredient_amount <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": [
                            {},
                            {
                                "amount": [
                                    '''Количество ингредиента
                                    должно быть больше 0!'''
                                ]
                            },
                        ]
                    }
                )

            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    {
                        "ingredients": [
                            {},
                            {
                                "amount": [
                                    'Ингредиенты должны быть уникальными!'
                                ]
                            },
                        ]
                    }
                )

            ingredient_ids.add(ingredient_id)

        if cooking_time < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть больше 1!'}
            )

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user

        with transaction.atomic():
            recipe = Recipe.objects.create(author=author, **validated_data)
            self._create_ingredients(recipe, ingredients_data)
            recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        with transaction.atomic():
            RecipeIngredient.objects.filter(recipe=instance).delete()
            super().update(instance, validated_data)
            self._create_ingredients(instance, ingredients_data)

        return instance

    def _create_ingredients(self, recipe, ingredients_data):
        ingredients_to_create = [
            RecipeIngredient(
                ingredient_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        ]

        RecipeIngredient.objects.bulk_create(ingredients_to_create)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            not (request is None or request.user.is_anonymous)
            and Favorite.objects.filter(
                user=request.user, recipe_id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            not (request is None or request.user.is_anonymous)
            and Cart.objects.filter(
                user=request.user, recipe_id=obj.id
            ).exists()
        )


class FavoriteAndCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            Recipe.objects.filter(author=obj.author)[: int(limit)]
            if limit
            else Recipe.objects.filter(author=obj.author)
        )
        return FavoriteAndCartSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        return SubscriptionUtils.check_subscription(
            self.context.get('request').user, obj.author
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
