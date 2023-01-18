from django.urls import path, include
from rest_framework import routers
from .views import (ShoppingCartListView, UserViewSet, TagViewSet,
                    IngridientViewSet, RecipeViewSet,
                    FavoriteListViewSet)


app_name = 'api'
router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/favorite/', FavoriteListViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartListView.as_view()),
    path('', include(router.urls)),
]
