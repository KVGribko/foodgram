from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Название", max_length=200, unique=True)
    color = models.CharField("Цвет", max_length=7, unique=True)
    slug = models.SlugField("slug", max_length=200, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=200, unique=True)
    measurement_unit = models.CharField("Ед. изм", max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
    )
    name = models.CharField("Название", max_length=200)
    image = models.ImageField("Картинка", upload_to="recipe_images/")
    text = models.TextField("Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингридиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Ингридиент",
    )
    amount = models.PositiveIntegerField(
        "Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Ингридиенты рецепта"
        verbose_name_plural = "Ингридиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recipe",
                    "ingredient",
                ],
                name="unique_ingredient_in_recipe",
            )
        ]


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_favorite",
        verbose_name="Избранный рецепт",
    )

    class Meta:
        verbose_name = "Избранные рецепты пользователя"
        verbose_name_plural = "Избранные рецепты пользователя"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "recipe",
                ],
                name="unique_favorite",
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина пользователя"
        verbose_name_plural = "Корзина пользователя"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "recipe",
                ],
                name="unique_recipe_in_cart",
            ),
        ]
