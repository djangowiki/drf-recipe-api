"""Test for ingredients API"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status

from core import models
from recipe import serializers


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def ingredient_detail_url(ingredient_id):
    """Create and return ingredient detail url"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="test@example.com", password="testpass123"):
    """Create and returns an API user"""
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


class PublicIngredientsAPITests(TestCase):
    """Tests unauthenticated ingredient API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_ingredients(self):
        """Tests auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Tests authenticated ingredient API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        models.Ingredient.objects.create(user=self.user, name="Egwusi")
        models.Ingredient.objects.create(user=self.user, name="Bitter Leaf")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = models.Ingredient.objects.all()
        serializer = serializers.IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user_2 = create_user(email="testuser2@example.com", password="testpass1234")
        models.Ingredient.objects.create(user=user_2, name="Ogbono")
        ingredient = models.Ingredient.objects.create(user=self.user, name="Pepper")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient API"""
        ingredient = models.Ingredient.objects.create(user=self.user, name="Ogiri")

        payload = {"name": "Ugba"}

        url = ingredient_detail_url(ingredient.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        # self.assertEqual(ingredient.name, payload.name) so this was wrong afterall.
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting an ingredient from the API"""
        ingredient = models.Ingredient.objects.create(user=self.user, name="Akwu")

        url = ingredient_detail_url(ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingrdients = models.Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingrdients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        ingredient1 = models.Ingredient.objects.create(user=self.user, name="Oil")
        ingredient2 = models.Ingredient.objects.create(user=self.user, name="Maggi")

        recipe = models.Recipe.objects.create(
            title="Egwusi Soup", time_minutes=40, price=Decimal("5.50"), user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        ingredientSerializer1 = serializers.IngredientSerializer(ingredient1)
        ingredientSerializer2 = serializers.IngredientSerializer(ingredient2)

        self.assertIn(ingredientSerializer1.data, res.data)
        self.assertNotIn(ingredientSerializer2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        ingredient = models.Ingredient.objects.create(user=self.user, name="Eggs")

        models.Ingredient.objects.create(user=self.user, name="Chicken")

        recipe1 = models.Recipe.objects.create(
            title="Egg Chicken Soup",
            time_minutes=30,
            price=Decimal("8.00"),
            user=self.user,
        )
        recipe2 = models.Recipe.objects.create(
            title="Chicken Pepper Soup",
            time_minutes=20,
            price=Decimal("9.50"),
            user=self.user,
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
