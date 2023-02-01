# Generated by Django 3.2 on 2023-02-01 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_rename_favorite_recipe_favorite_recipe'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_fav_recipe',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_fav_recipe'),
        ),
    ]