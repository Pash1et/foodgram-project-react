from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def validate_tags(self, data):
        tags = data
        if not tags:
            raise serializers.ValidationError('Нужно выбрать минимум 1 тег')
        tags_list = []
        for cur_tag in tags:
            if cur_tag in tags_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным'
                )
            tags_list.append(cur_tag)
        return tags_list

    def validate_cooking_time(self, data):
        cocking_time = data
        if cocking_time < 1:
            raise serializers.ValidationError(
                'Время готовки не может быть < 1 мин')
        return cocking_time

    def validate_ingredients(self, data):
        ingredients = data
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно выбрать минимум 1 ингридиент'
            )
        ingredients_list = []
        for cur_ingr in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=cur_ingr['ingredient']['id']
            )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны'
                )
            if int(cur_ingr['amount'] <= 0):
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть > 0'
                )
            ingredients_list.append(cur_ingr)
        return ingredients_list

    @staticmethod
    def create_ingredient(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            cur_ingr = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            amount = ingredient['amount']
            ingredient_list.append(
                IngredientAmount(recipe=recipe,
                                 ingredient=cur_ingr,
                                 amount=amount)
            )
        IngredientAmount.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredientamount_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientamount_set')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.pk).update(**validated_data)
        recipe = get_object_or_404(Recipe, id=instance.pk)
        recipe.tags.remove()
        IngredientAmount.objects.filter(recipe=instance.pk).delete()
        TagRecipe.objects.filter(recipe=instance.pk).delete()
        recipe.tags.set(tags)
        self.create_ingredient(ingredients, recipe)
        return recipe


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
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
            user=user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user.id
        recipe = obj.id
        return ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).exists()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    author_id = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = ('user_id', 'author_id')

    def create(self, validated_data):
        user = validated_data.get('user')
        author = get_object_or_404(
            User,
            pk=validated_data.get('author').get('id')
        )
        return Follow.objects.create(user=user, author=author)

    def validate(self, attrs):
        if Follow.objects.filter(
            author=attrs.get('author').get('id'),
            user=attrs.get('user').get('id')
        ):
            raise serializers.ValidationError(
                'Подписка уже есть'
            )
        return super().validate(attrs)


class SubscribeListSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        user = obj.user
        author = obj.author
        return Follow.objects.filter(user=user, author=author).exists()

    def get_recipes(self, obj):
        author = obj.author
        recipe = Recipe.objects.filter(author=author)
        return RecipeSerializer(recipe, many=True).data

    def get_recipes_count(self, obj):
        author = obj.author
        return Recipe.objects.filter(author=author).count()


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(read_only=True, source='recipe.image')
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteCreateSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField(source='recipe.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = Favorite
        fields = ('recipe_id', 'user_id')

    def create(self, validated_data):
        recipe = get_object_or_404(
            Recipe,
            pk=validated_data.get('recipe').get('id')
        )
        user = validated_data.get('user')
        return Favorite.objects.create(user=user, recipe=recipe)

    def validate(self, attrs):
        if Favorite.objects.filter(
            user=attrs.get('user').get('id'),
            recipe=attrs.get('recipe').get('id')
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
