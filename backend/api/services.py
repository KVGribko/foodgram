from django.db.models import F, Sum

from recipes.models import Ingredient


def get_user_shopping_cart(user):
    ingredients = Ingredient.objects.filter(
        recipe__recipe__shopping_cart__user=user
    ).values(
        "name",
        unit=F("measurement_unit"),
    ).annotate(amount=Sum("recipe__amount"))
    shopping_list = [
        f"{ingredient['name']}: {ingredient['amount']} {ingredient['unit']}"
        for ingredient in ingredients
    ]
    return "\n".join(shopping_list)
