from djoser.views import UserViewSet as DjoserViewSet
from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from carts.models import Cart
from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from subscriptions.models import Subscription
from users.models import User
from .filters import IngredientFilter, RecipeFilter
from .mixins import AddRemoveFromListMixin
from .pagination import Pagination
from .permissions import ReadOnlyAndEditAuthor
from .serializers import (
    EditRecipeSerializer,
    FavoriteAndCartSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
import logging

logger = logging.getLogger(__name__)

class UserViewSet(DjoserViewSet):
    permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyAndEditAuthor]
    pagination_class = Pagination
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return EditRecipeSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    try:
        user = request.user
        if user.is_anonymous:
            return HttpResponse("Error: User is not authenticated", content_type='text/plain')

        recipes = (
            Recipe.objects.filter(cart_by__user=user)
            .prefetch_related('recipe_ingredients__ingredient')
            .distinct()
        )

        ingredient_list = "Список покупок:\n"
        total_cost = 0

        for recipe in recipes:
            ingredient_list += f"\nРецепт: {recipe.name}\n"
            recipe_total_cost = 0
            ingredients = (
                RecipeIngredient.objects.filter(recipe=recipe)
                .select_related('ingredient')
                .values(
                    'ingredient__name', 
                    'ingredient__measurement_unit',
                    'ingredient__price_per_100g',
                    'amount'
                )
            )
            for i in ingredients:
                name = i['ingredient__name']
                measurement_unit = i['ingredient__measurement_unit']
                total_amount = i['amount']
                price_per_100g = i.get('ingredient__price_per_100g')

                if price_per_100g is not None:
                    total_price = (price_per_100g / 100) * total_amount
                    recipe_total_cost += total_price
                    ingredient_list += (
                        f'{name} - {total_amount} {measurement_unit}, '
                        f'{total_price:.2f} руб. (Цена за 100г - {price_per_100g} руб.)\n'
                    )
                else:
                    ingredient_list += f'{name} - {total_amount} {measurement_unit}, N/A\n'

            total_cost += recipe_total_cost
            ingredient_list += f'Общая стоимость рецепта: {recipe_total_cost:.2f} руб.\n'

        ingredient_list += f'\nОбщая стоимость всех покупок: {total_cost:.2f} руб.'

        response = HttpResponse(ingredient_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", content_type='text/plain')


class FavoriteRecipeView(
    AddRemoveFromListMixin, RetrieveDestroyAPIView, ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]
    list_model = Favorite
    error_exists_message = 'Рецепт уже добавлен в избранное.'
    error_not_exists_message = 'Рецепт еще не был добавлен в избранное.'

    def get_serializer_class(self):
        return FavoriteAndCartSerializer


class CartRecipeView(
    AddRemoveFromListMixin, RetrieveDestroyAPIView, ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]
    list_model = Cart
    error_exists_message = 'Рецепт уже добавлен в корзину.'
    error_not_exists_message = 'Рецепт еще не был добавлен в корзину.'

    def get_serializer_class(self):
        return FavoriteAndCartSerializer


class SubscriptionsView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    serializer_class = SubscriptionSerializer

    def get(self, request):
        user = request.user
        queryset = Subscription.objects.filter(subscriber=user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        author_id = kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        user = request.user

        if user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Subscription.objects.filter(
            subscriber=user, author=author
        ).exists():
            subscription = Subscription.objects.create(
                subscriber=user, author=author
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {'detail': 'Подписка уже существует.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        author_id = kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        user = request.user

        if Subscription.objects.filter(
            subscriber=user, author=author
        ).exists():
            Subscription.objects.filter(
                subscriber=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Подписка уже была удалена.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
