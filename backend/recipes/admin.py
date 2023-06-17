from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        exclude = ('id')
        import_id_fields = ["name"]


@admin.register(Ingredient)
class ImportIngredientsAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ["name", "measurement_unit"]
    search_fields = ["name"]
    list_filter = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "slug"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "display_tags", "favorite"]
    list_filter = ["name", "author", "tags"]
    search_fields = ["name"]
    readonly_fields = ["favorite"]
    fields = [
        "image",
        ("name", "author"),
        "text",
        ("tags", "cooking_time"),
        "favorite",
    ]

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = "Теги"

    def favorite(self, obj):
        return obj.in_favorite.count()

    favorite.short_description = "Раз в избранном"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")
