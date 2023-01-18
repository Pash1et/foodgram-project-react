# Generated by Django 3.2 on 2023-01-12 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230112_0928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit_of_measurement',
            field=models.CharField(max_length=100, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time',
            field=models.PositiveIntegerField(default=1, verbose_name='Время приготовлени мин.'),
        ),
    ]
