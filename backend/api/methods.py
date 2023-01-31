from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def custom_post(self, request, pk, serializer):
    user = request.user
    serializer = serializer(data={'recipe_id': pk, 'user_id': user.id})
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

def custom_delete(self, request, pk, model):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    model = get_object_or_404(model, user=user, recipe=recipe)
    model.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
