"""Test for ingredients API"""
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
