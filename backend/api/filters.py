from django_filters import rest_framework as filter
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filter.FilterSet):
    name = filter.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filter.FilterSet):
    author = filter.CharFilter()
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name='slug',
    )
    is_favorited = filter.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filter.BooleanFilter(method='get_is_in_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def get_is_in_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart_by__user=self.request.user)
        return queryset
