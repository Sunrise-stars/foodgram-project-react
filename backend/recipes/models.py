from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(unique=True, max_length=200, verbose_name='Slug')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование')
    measurement_unit = models.CharField(max_length=200, verbose_name='Единица измерения')

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор')
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='static/recipe/', verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(verbose_name='Время приготовления')
    tags = models.ManyToManyField(Tag, related_name='recipes', verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты')

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} {self.ingredient.measurement_unit})"