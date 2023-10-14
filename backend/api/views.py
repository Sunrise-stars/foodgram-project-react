from carts.models import Cart
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from subscriptions.models import Subscription
from users.models import User

from .filters import IngredientFilter, RecipeFilter
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        AllowAny,
    ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        AllowAny,
    ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        ReadOnlyAndEditAuthor,
    ]
    pagination_class = Pagination
    queryset = Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return EditRecipeSerializer


class FavoriteRecipeView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_serializer_class(self):
        return FavoriteAndCartSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if not Favorite.objects.filter(user=user, recipe=instance).exists():
            favorite = Favorite.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Рецепт уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(user=user, recipe=instance).exists():
            Favorite.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Рецепт еще не был добавлен в избранное.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CartRecipeView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_serializer_class(self):
        return FavoriteAndCartSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if not Cart.objects.filter(user=user, recipe=instance).exists():
            favorite = Cart.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Рецепт уже добавлен в корзину.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Cart.objects.filter(user=user, recipe=instance).exists():
            Cart.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Рецепт еще не был добавлен в корзину.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubscriptionsView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = Pagination

    def get_serializer_class(self):
        return SubscriptionSerializer

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


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = (
        RecipeIngredient.objects.filter(recipe__cart_by__user=request.user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
    )
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/txt')
    response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
    return response
