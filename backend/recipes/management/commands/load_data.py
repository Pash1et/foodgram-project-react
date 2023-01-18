import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        os.chdir(os.path.join(settings.BASE_DIR, 'data'))
        for file in os.listdir("."):
            with open(file, 'r', encoding='utf-8') as f:
                serialized_ingredients = json.load(f)
            for ingr in serialized_ingredients:
                ingredient, created = Ingredient.objects.update_or_create(
                    name=ingr['name'],
                    measurement_unit=ingr['measurement_unit'],
                    defaults={'name': ingr['name'], }
                )
