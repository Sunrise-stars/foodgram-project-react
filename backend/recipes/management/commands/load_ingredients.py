import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Загрузка ингридентов из файла'

    def handle(self, *args, **options):
        filename = 'data/ingredients.csv'

        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            for row in reader:
                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Создано: {ingredient}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Уже есть: {ingredient}')
                    )
