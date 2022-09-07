import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer
from .models import Tag, Ingredient, Recipe, RecipeIngredients, \
        Favorite, ShoppingCart

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Основной сериализатор для рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shoppingcart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'name',
                  'author',
                  'ingredients',
                  'image',
                  'cooking_time',
                  'text',
                  'is_favorite',
                  'is_in_shoppingcart',
                  )

    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj,
                                       user=request.user).exists()

    def get_is_in_shoppingcart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=request.user).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Cериализатор для краткого отображения рецепта"""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class AddIngredientsToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта"""
    ingredients = AddIngredientsToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False, allow_null=True)
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'name',
                  'author',
                  'ingredients',
                  'image',
                  'cooking_time',
                  'text',
                  )

    def validate_ingredients(self, ingredients):
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше нуля'
                )
        return ingredients

    @staticmethod
    def validate_cooking_time(value):
        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше нуля'
            )
        return value

    @staticmethod
    def add_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if RecipeIngredients.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            RecipeIngredients.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        RecipeIngredients.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = ShortRecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}).data
        return data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorite.objects.filter(user=user,
                                   recipe__id=recipe_id).exists():
            raise ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingCart.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            raise ValidationError(
                'Этот рецепт уже есть в списке покупок'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe,
            context=context
        ).data
