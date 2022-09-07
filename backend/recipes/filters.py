from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )
