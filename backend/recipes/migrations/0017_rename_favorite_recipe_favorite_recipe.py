# Generated by Django 3.2 on 2023-01-31 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20230130_1049'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorite',
            old_name='favorite_recipe',
            new_name='recipe',
        ),
    ]
