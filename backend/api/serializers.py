from base64 import b64decode

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from djoser.serializers import (UserCreateSerializer, UserSerializer,
                                ValidationError)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (ImageField, ModelSerializer,
                                        PrimaryKeyRelatedField)
from users.models import Follow

User = get_user_model()


class UsersCreateSerializer(UserCreateSerializer):
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


class UserSerializer(UserSerializer):
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
        # return user.subscriptions.filter(author=obj).exists()
        return Follow.objects.filter(user=user, author=object.id).exists()


class RecipeFollowSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]
        read_only_fields = "__all__"


class FollowSerializer(UserSerializer):
    recipes = RecipeFollowSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
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
        fields = [
            "id",
            "name",
            "measurement_unit",
        ]


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="photo." + ext)
        return super().to_internal_value(data)


class GetRecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
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


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class AddIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source=Ingredient,
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            "id",
            "amount",
        ]


class PostRecipeSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    @transaction.atomic
    def set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredients=ingredient,
                amount=amount,
            )
            for ingredient, amount in ingredients.values()
        )

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return GetRecipeSerializer(instance, context=context).data
