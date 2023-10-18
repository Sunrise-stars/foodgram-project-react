from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


class AddRemoveFromListMixin:
    def create(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if not self.list_model.objects.filter(
           user=user, recipe=instance).exists():
            favorite = self.list_model.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': self.error_exists_message},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)
        user = request.user

        if self.list_model.objects.filter(
                user=user, recipe=instance).exists():
            self.list_model.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': self.error_not_exists_message}, status=status.HTTP_400_BAD_REQUEST)
