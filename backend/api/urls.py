from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteListViewSet, IngridientViewSet, RecipeViewSet,
                    ShoppingCartListView, SubscribeListViewSet,
                    SubscribeViewSet, TagViewSet)

app_name = 'api'
router = DefaultRouter()

router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/subscriptions/',
         SubscribeListViewSet.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', SubscribeViewSet.as_view()),
    path('recipes/<int:pk>/favorite/', FavoriteListViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartListView.as_view()),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
