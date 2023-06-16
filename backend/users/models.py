from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "login",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": "A user with the same name already exists",
        },
    )
    first_name = models.CharField("First name", max_length=150, blank=True)
    last_name = models.CharField("Last name", max_length=150, blank=True)
    email = models.EmailField(
        "email",
        max_length=254,
        unique=True,
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"],
                name="unique_following",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="cant_subscribe_to_yourself",
            ),
        ]
