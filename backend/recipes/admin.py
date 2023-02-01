from django.contrib import admin
from django.utils.html import format_html

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class IngredientAmountInLine(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'image_tag',)
    list_filter = ('tags',)
    search_fields = ('author__username', 'name',)
    inlines = (IngredientAmountInLine, TagRecipeInLine,)

    def image_tag(self, obj):
        return format_html(f'<img src="{obj.image.url}"'
                           f'style="width: 45px; height:45px;" />')
    image_tag.short_description = 'Изображение'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
