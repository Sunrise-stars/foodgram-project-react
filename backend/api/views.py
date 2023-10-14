from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveDestroyAPIView, ListCreateAPIView
from rest_framework.decorators import action, api_view

from .filters import RecipeFilter, IngredientFilter
from .pagination import Pagination
from .permissions import ReadOnlyAndEditAuthor
from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer, EditRecipeSerializer,
                          FavoriteAndCartSerializer)
from recipes.models import (Tag, Ingredient, Recipe)
from favorites.models import Favorite
from carts.models import Cart
from recipes.models import RecipeIngredient


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyAndEditAuthor, ]
    pagination_class = Pagination
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return EditRecipeSerializer


class FavoriteRecipeView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        return FavoriteAndCartSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if not Favorite.objects.filter(
           user=user, recipe=instance).exists():
            favorite = Favorite.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Рецепт уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(
           user=user, recipe=instance).exists():
            Favorite.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Рецепт еще не был добавлен в избранное.'},status=status.HTTP_400_BAD_REQUEST)

class CartRecipeView(RetrieveDestroyAPIView, ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        return FavoriteAndCartSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if not Cart.objects.filter(
           user=user, recipe=instance).exists():
            favorite = Cart.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Рецепт уже добавлен в корзину.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Cart.objects.filter(
           user=user, recipe=instance).exists():
            Cart.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Рецепт еще не был добавлен в корзину.'},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response