# Generated by Django 3.2 on 2023-01-12 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_rename_unit_of_measurement_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IngredientCount',
            new_name='IngredientAmount',
        ),
        migrations.RenameField(
            model_name='ingredientamount',
            old_name='count',
            new_name='amount',
        ),
    ]