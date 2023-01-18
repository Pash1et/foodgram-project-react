from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.models import User, Follow
from recipes.models import (Recipe, Ingredient, Tag, TagRecipe,
                            IngredientAmount, Favorite, ShoppingCart)
from drf_extra_fields.fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
        required=False
        )
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
        required=False
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user.id
        recipe = obj.id
        return Favorite.objects.filter(
            user=user, favorite_recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user.id
        recipe = obj.id
        return ShoppingCart.objects.filter(
            user=user, recipe=recipe
            ).exists()


class SubscribeListSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='favorite_recipe.id')
    name = serializers.ReadOnlyField(source='favorite_recipe.name')
    image = Base64ImageField(read_only=True, source='favorite_recipe.image')
    cooking_time = serializers.ReadOnlyField(
        source='favorite_recipe.cooking_time'
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteCreateSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField(source='favorite_recipe.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = Favorite
        fields = ('recipe_id', 'user_id')

    def create(self, validated_data):
        recipe = get_object_or_404(
            Recipe,
            pk=validated_data.get('favorite_recipe').get('id')
        )
        user = validated_data.get('user')
        return Favorite.objects.create(user=user, favorite_recipe=recipe)

    def validate(self, attrs):
        if Favorite.objects.filter(
            user=attrs.get('user').get('id'),
            favorite_recipe=attrs.get('favorite_recipe').get('id')
        ):
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        return super().validate(attrs)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(read_only=True, source='recipe.image')
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time',)


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField(source='recipe.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = ShoppingCart
        fields = ('recipe_id', 'user_id')

    def create(self, validated_data):
        recipe = get_object_or_404(
            Recipe,
            pk=validated_data.get('recipe').get('id')
        )
        user = validated_data.get('user')
        return ShoppingCart.objects.create(
            user=user, recipe=recipe
        )

    def validate(self, attrs):
        if ShoppingCart.objects.filter(
            user=attrs.get('user').get('id'),
            recipe=attrs.get('recipe').get('id')
        ):
            raise serializers.ValidationError(
                'Уже в корзине'
            )
        return super().validate(attrs)
