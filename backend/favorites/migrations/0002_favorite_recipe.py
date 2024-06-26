# Generated by Django 3.2.3 on 2023-10-14 16:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        ('favorites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorited_by',
                to='recipes.recipe',
                verbose_name='Рецепт',
            ),
        ),
    ]
