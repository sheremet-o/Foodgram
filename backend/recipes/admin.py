from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredients, \
        Favorite, ShoppingCart


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ['name']
    ordering = ['name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ['name']
    ordering = ['name']


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = ('id',
                   'recipe',
                   'ingredient',
                   )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'in_favorite',
    )
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('in_favorite',)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
