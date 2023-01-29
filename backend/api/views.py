from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User

from .permissions import IsAuthorOrAdmin
from .serializers import (FavoriteCreateSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartCreateSerializer,
                          ShoppingCartSerializer, SubscribeCreateSerializer,
                          SubscribeListSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class IngridientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrAdmin,)

    def get_queryset(self):
        return Ingredient.objects.filter(
            name__istartswith=self.request.GET['name']
        )


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (IsAuthorOrAdmin,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorOrAdmin,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        if self.request.query_params.get('is_favorited') is not None:
            recipe = Favorite.objects.filter(user=user).values(
                'favorite_recipe'
            )
            queryset = queryset.filter(id__in=recipe)

        if self.request.query_params.get('is_in_shopping_cart') is not None:
            recipe = ShoppingCart.objects.filter(user=user).values('recipe')
            queryset = queryset.filter(id__in=recipe)

        if self.request.query_params.get('author') is not None:
            pk = self.request.query_params.get('author')
            queryset = queryset.filter(author=pk)

        return queryset

    @action(detail=False,
            permission_classes=(IsAuthenticated,),
            methods=['get'])
    def download_shopping_cart(self, request):
        shopping_list = []
        user = request.user
        shoppingcart = ShoppingCart.objects.filter(user=user).values(
            'recipe'
        )
        recipe = Recipe.objects.filter(id__in=shoppingcart).values(
            'ingredients'
        )
        ingredients = Ingredient.objects.filter(id__in=recipe)
        for ingredient in ingredients:
            amount = IngredientAmount.objects.filter(
                ingredient=ingredient,
                recipe__in=shoppingcart
            ).values_list('amount').aggregate(total_amount=Sum('amount'))
            shopping_list.append(f'{ingredient.name} - '
                                 f'{amount["total_amount"]} '
                                 f'{ingredient.measurement_unit} \n')
        response = HttpResponse(shopping_list,
                                content_type="text/plain,charset=utf8")
        return response

    def create(self, request):
        request = request.data.copy()
        request['tags'] = [{"id": id} for id in request['tags']]
        serializer = RecipeSerializer(data=request)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):
        pk = kwargs.get('pk')
        instance = get_object_or_404(Recipe, pk=pk)
        request = request.data.copy()
        request['tags'] = [{"id": id} for id in request['tags']]
        serializer = RecipeSerializer(instance, data=request, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        serializer = SubscribeCreateSerializer(
            data={'user_id': user.id, 'author_id': author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        follow = get_object_or_404(
            Follow,
            user=user,
            author=author
        )
        serializer = SubscribeListSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        follow = get_object_or_404(
            Follow,
            user=user,
            author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = user.follower.all()
        if self.request.query_params.get('recipes_limit') is not None:
            recipes_limit = self.request.query_params.get('recipes_limit')
            queryset = queryset[:int(recipes_limit)]
        return queryset


class FavoriteListViewSet(views.APIView):
    serializer_class = FavoriteSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

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
