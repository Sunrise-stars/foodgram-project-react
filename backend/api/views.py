from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import TagSerializer, IngredientSerializer
from recipes.models import Tag
from recipes.models import Ingredient


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
