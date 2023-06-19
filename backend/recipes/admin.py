from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    FavoriteRecipes,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        exclude = "id"
        import_id_fields = ["name"]


@admin.register(Ingredient)
class ImportIngredientsAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ["name", "measurement_unit"]
    search_fields = ["name"]
    list_filter = ["name"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "count_in_favorites"]
    list_filter = ["name", "author", "tags"]
    search_fields = ["name", "author__username", "tags__name"]
    readonly_fields = ["count_in_favorites"]
    fields = [
        ("name", "author"),
        "image",
        "text",
        "tags",
        "cooking_time",
        "count_in_favorites",
    ]
    inlines = [IngredientInline]

    def count_in_favorites(self, obj):
        return obj.in_favorite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "slug"]
