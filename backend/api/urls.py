from django.contrib import admin
from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet, IngredientViewSet, RecipeViewSet, FavoriteRecipeView)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeView.as_view(), name='favorite_recipe'),
    path('recipes/<int:recipe_id>/shopping_cart/', FavoriteRecipeView.as_view(), name='shopping_cart'),
    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_create'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
