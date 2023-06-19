from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    FollowSerializer,
    FoodgramUserSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    PreviewRecipeSerializer,
    TagSerializer,
)
from api.services import get_user_shopping_cart
from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        sub = Follow.objects.filter(user=user, author=author)

        if request.method == "DELETE":
            if sub.exists():
                sub.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "You are not subscribed to this author"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            if sub.exists():
                return Response(
                    {"errors": "You are already subscribed to this author"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                follow.author,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        serializer = FollowSerializer(
            self.paginate_queryset(User.objects.filter(following__user=user)),
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated,),
        serializer_class=FoodgramUserSerializer,
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (IsOwnerOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetRecipeSerializer
        return PostRecipeSerializer

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.__add(FavoriteRecipes, request.user, pk)
        return self.__delete(FavoriteRecipes, request.user, pk)

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.__add(ShoppingCart, request.user, pk)
        return self.__delete(ShoppingCart, request.user, pk)

    def __add(self, model, user, recipe_id):
        if model.objects.filter(user=user, recipe__id=recipe_id).exists():
            return Response(
                {"errors": "already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=recipe_id)
        model.objects.create(user=user, recipe=recipe)
        serializer = PreviewRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def __delete(self, model, user, recipe_id):
        obj = model.objects.filter(user=user, recipe__id=recipe_id)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_list = get_user_shopping_cart(request.user)
        response = HttpResponse(
            shopping_list,
            content_type="text.txt; charset=utf-8",
        )
        file_name = f"{request.user.username}_shopping_list.txt"
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
