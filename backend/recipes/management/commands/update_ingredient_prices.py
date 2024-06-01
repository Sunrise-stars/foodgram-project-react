import random
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Update ingredient prices'

    def handle(self, *args, **kwargs):
        ingredients = Ingredient.objects.all()
        for ingredient in ingredients:
            ingredient.price_per_100g = random.uniform(80, 350)
            ingredient.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated ingredient prices'))
