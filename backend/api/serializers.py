from base64 import b64decode

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer,
    ValidationError,
)
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    ImageField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
)

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow

User = get_user_model()


class UsersCreateSerializerForDjoser(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, username):
        if username == "me":
            raise ValidationError("Using 'me' as a username is not allowed")
        return username


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, object):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=object.id).exists()


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="photo." + ext)
        return super().to_internal_value(data)


class PreviewRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class FollowSerializer(FoodgramUserSerializer):
    recipes = PreviewRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + [
            "recipes",
            "recipes_count",
        ]

    def get_recipes_count(self, object):
        return object.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class GetRecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )

    def get_is_favorited(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=recipe).exists()


class AddIngredientSerializer(Serializer):
    id = IntegerField()
    amount = IntegerField(min_value=1)


class PostRecipeSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def validate_ingredients(self, ingredients):
        if len(ingredients) == 0:
            raise ValidationError("Ingredients cannot be empty")

        # for i, ingredient in enumerate(ingredients):
        #     for j in range(i + 1, len(ingredients)):
        #         if ingredient["id"] == ingredients[j]["id"]:
        #             s = f"Ingredients cannot be repeated. {ingredient['id']} vs {ingredients[j]['id']}!"
        #             raise ValidationError(s)

        for ingredient in ingredients:
            if ingredient["amount"] <= 0:
                raise ValidationError(
                    "The number of ingredients must be greater than 0"
                )
        return ingredients

    def validate_tags(self, tags):
        if len(tags) == 0:
            raise ValidationError("Tags cannot be empty")

        for i, tag in enumerate(tags):
            for j in range(i + 1, len(tags)):
                if tag["id"] == tags[j]["id"]:
                    raise ValidationError("Tags cannot be repeated")
        return tags

    def validate_cooking_time(self, time):
        if time <= 0:
            raise ValidationError("Cooking time must be greater than 0")
        return time

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.__set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.__set_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    @transaction.atomic
    def __set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient["id"]),
                amount=ingredient["amount"],
            )
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return GetRecipeSerializer(instance, context=context).data
