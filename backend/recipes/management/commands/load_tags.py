import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag

class Command(BaseCommand):
    help = 'Загрузка тегов из файла'

    def handle(self, *args, **options):
        filename = 'data/tags.csv'

        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            for row in reader:
                name, color, slug = row
                tag, created = Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug,
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Создано: {tag}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Уже есть: {tag}'))
