# Импорты из стандартной библиотеки Python
from django.urls import include, path

# Импорты связанных сторонних библиотек
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter

# Импорты, зависящие от локального приложения или модуля
from .views import (
    CartRecipeView,
    FavoriteRecipeView,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionsView,
    TagViewSet,
    download_shopping_cart,
)


router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart',
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteRecipeView.as_view(),
        name='favorite_recipe',
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        CartRecipeView.as_view(),
        name='shopping_cart',
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscriptionsView.as_view(),
        name='subscribe',
    ),
    path(
        'users/subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions',
    ),
    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_create'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
