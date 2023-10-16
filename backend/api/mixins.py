from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from .models import Recipe  

class AddRemoveFromListMixin:
    def perform_action(
        self,
        request,
        instance,
        list_model,
        list_name,
        error_message,
        *args,
        **kwargs,
    ):
        user = request.user
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)

        if not list_model.objects.filter(user=user, recipe=instance).exists():
            item = list_model.objects.create(user=user, recipe=instance)
            serializer = self.get_serializer(item.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {'detail': error_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        recipe_id = kwargs.get('id')
        instance = get_object_or_404(Recipe, id=recipe_id)

        if self.list_model.objects.filter(user=user, recipe=instance).exists():
            self.list_model.objects.filter(user=user, recipe=instance).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'detail': 'Рецепт еще не был добавлен в {}.'.format(
                    self.list_name
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
