from django.db import models
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart_by', verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user} добавил(а) {self.recipe} в карзину'