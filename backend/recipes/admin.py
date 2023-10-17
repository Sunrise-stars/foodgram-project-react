from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_author',
        'name',
        'text',
        'cooking_time',
        'get_tags',
        'get_ingredients',
        'get_favorite_count',
    )
    search_fields = (
        'name',
        'cooking_time',
        'author__email',
        'ingredients__name',
    )
    list_filter = ('tags',)
    inlines = (RecipeIngredientAdmin,)
    empty_value_display = '- Нет записей-'

    @admin.display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        tag_names = obj.tags.values_list('name', flat=True)
        return ', '.join(tag_names)

    @admin.display(description=' Ингредиенты ')
    def get_ingredients(self, obj):
        return '\n '.join(
            [
                f'{item["ingredient__name"]} - {item["amount"]}'
                f' {item["ingredient__measurement_unit"]}.'
                for item in obj.recipe_ingredients.values(
                    'ingredient__name',
                    'amount',
                    'ingredient__measurement_unit',
                )
            ]
        )

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorited_by.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    empty_value_display = '- Нет записей-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
        'measurement_unit',
    )
    empty_value_display = '- Нет записей-'
