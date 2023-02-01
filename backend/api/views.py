from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.methods import custom_delete, custom_post
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
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
    permission_classes = (IsAuthenticated,)


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
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorOrAdmin,)

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return RecipeSerializer
        return RecipeListSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        if self.request.query_params.get('tags') is not None:
            slug = self.request.query_params.getlist('tags')
            queryset = queryset.filter(tag__slug__in=slug)

        if self.request.query_params.get('is_favorited') is not None:
            recipe = Favorite.objects.filter(user=user).values(
                'recipe'
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
        name = 'recipe__ingredientamount__ingredient__name'
        unit = 'recipe__ingredientamount__ingredient__measurement_unit'
        amount = 'recipe__ingredientamount__amount'
        ingredients = user.shoppingcart.select_related('recipe').values(
            name, unit
        ).annotate(Sum(amount))
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient[name]} - '
                f'{ingredient["recipe__ingredientamount__amount__sum"]} '
                f'{ingredient[unit]}'
                f'\n'
            )
        response = HttpResponse(shopping_list,
                                content_type="text/plain,charset=utf8")
        return response


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
        return custom_post(self, request, pk, FavoriteCreateSerializer)

    def delete(self, request, pk):
        return custom_delete(self, request, pk, Favorite)


class ShoppingCartListView(views.APIView):
    serializer_class = ShoppingCartSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        return custom_post(self, request, pk, ShoppingCartCreateSerializer)

    def delete(self, request, pk):
        return custom_delete(self, request, pk, ShoppingCart)
