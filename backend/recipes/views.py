from django.http import HttpResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from weasyprint import HTML

from foodgram.pagination import FoodgramPaginator
from .filters import IngredientFilter, RecipeFilter
from .models import (Ingredient, Recipe, Tag)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from .serializers import AddRecipeSerializer, IngredientSerializer, \
        RecipeSerializer, ShortRecipeSerializer, TagSerializer
from .utils import get_list_ingredients


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_classes = {
        'retrieve': ShortRecipeSerializer,
        'list': ShortRecipeSerializer,
    }
    default_serializer_class = AddRecipeSerializer
    permission_classes = (IsAuthorOrAdmin,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = FoodgramPaginator

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action,
                                           self.default_serializer_class)

    def favorite_shoppingcart_post_delete(self, related_manager):
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        related_manager.create(recipe=recipe)
        serializer = RecipeSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def favorite(self, request, pk=None):
        return self.favorite_shoppingcart_post_delete(
            request.user.favorite
        )

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def shoppingcart(self, request, pk=None):
        return self.favorite_shoppingcart_post_delete(
            request.user.shoppingcart_user
        )

    @action(detail=False)
    def download_shoppingcart(self, request):
        ingredients = get_list_ingredients(request.user)
        template = render_to_string('recipes/pdf_template.html',
                                    {'ingredients': ingredients})
        html = HTML(string=template)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
