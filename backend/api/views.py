from django.shortcuts import get_object_or_404
from .serializers import (FavoriteCreateSerializer, FavoriteSerializer,
                          ShoppingCartCreateSerializer, ShoppingCartSerializer,
                          UserSerializer, IngredientSerializer,
                          TagSerializer, RecipeListSerializer,
                          SubscribeListSerializer)
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from users.models import User, Follow
from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class IngridientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        return Ingredient.objects.filter(
            name__istartswith=self.request.GET['name']
        )


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        slug = self.request.query_params.getlist('tags')
        if self.request.query_params.get('is_favorited') is not None:
            recipe = Favorite.objects.filter(user=user).values(
                'favorite_recipe'
            )
            queryset = queryset.filter(id__in=recipe)
        return queryset.filter(tag__slug__in=slug)


class SubscribeListViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeListSerializer
    queryset = Follow.objects.all()


class FavoriteListViewSet(views.APIView):
    serializer_class = FavoriteSerializer
    pagination_class = None

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        serializer = FavoriteCreateSerializer(
            data={
                'recipe_id': pk, 'user_id': user.id
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        favorite = get_object_or_404(
            Favorite, user=user, favorite_recipe=recipe
        )
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        favorite = get_object_or_404(
            Favorite, user=user, favorite_recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartListView(views.APIView):
    serializer_class = ShoppingCartSerializer
    pagination_class = None

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        serializer = ShoppingCartCreateSerializer(
            data={
                'recipe_id': pk, 'user_id': user.id
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        shoppingcart = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        serializer = ShoppingCartSerializer(shoppingcart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        shoppingcart = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        shoppingcart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
