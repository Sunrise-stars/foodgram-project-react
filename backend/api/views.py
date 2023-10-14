from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveDestroyAPIView, ListCreateAPIView

from .filters import RecipeFilter, IngredientFilter
from .pagination import Pagination
from .permissions import ReadOnlyAndEditAuthor
from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer, EditRecipeSerializer,
                          FavoriteSerializer)
from recipes.models import (Tag, Ingredient, Recipe)
from favorites.models import Favorite


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
    lookup_url_kwarg = 'recipe_id'

    def get_serializer_class(self):
        return FavoriteSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
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
        recipe_id = kwargs.get('recipe_id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if Favorite.objects.filter(
           user=user, recipe=instance).exists():
            Favorite.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
