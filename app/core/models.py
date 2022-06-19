"""
Database Models
"""
import uuid
import os
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.conf import settings
from django.db import models


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]  # extracting the extension from the filename
    filename = f"{uuid.uuid4()}{ext}"  # creating our own filename and appending the precious extension to the end.
    return os.path.join("uploads", "recipe", filename)  # os agnostic code.


class CustomUserManager(BaseUserManager):
    """Use to manage the custom user model"""

    def create_user(self, email, password=None, **extra_fields):
        """Create a user"""
        if not email:
            raise ValueError("Please provide a valid email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """Create a super user"""
        user = self.create_user(email=email, name=name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Creates a custom user model."""

    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    # Change login to email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


class Recipe(models.Model):
    """Create a recipe object"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(
        null=True, upload_to=recipe_image_file_path
    )  # making a reference to our function recipe upload image file path.

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient Model for Recipe"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Minimalistic Way of Doing This.
# class UserManager(BaseUserManager):
#     """Manages User Model"""

#     def create_user(self, email, password=None, **extra_fields):
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user


# class User(AbstractBaseUser, PermissionsMixin):
#     """User model"""

#     email = models.EmailField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = UserManager()

#     USERNAME_FIELD = "email"

#     def __str__(self):
#         return self.email
