# Generated by Django 3.2 on 2023-01-12 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230112_2002'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit_of_measurement',
            new_name='measurement_unit',
        ),
    ]
