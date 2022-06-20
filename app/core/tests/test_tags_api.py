""" Test for tags API """
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core import models
from recipe import serializers

TAGS_URL = reverse("recipe:tag-list")


def tag_detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@example.com", password="testpass123"):
    """Create and return a user."""
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


def setUp(self):
    self.client = APIClient()


class PublicTagsAPITests(TestCase):
    """Test unauthenticated tags API tests."""

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests authenticated tags API tests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieveing a list of tags"""
        models.Tag.objects.create(user=self.user, name="Vegan")
        models.Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = models.Tag.objects.all().order_by("-name")
        serializer = serializers.TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags are limited to authenticated user."""
        user2 = create_user(email="test2@gmail.com")
        models.Tag.objects.create(user=user2, name="Fruity")
        tag = models.Tag.objects.create(user=self.user, name="Beef")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = models.Tag.objects.create(user=self.user, name="After Dinner")

        payload = {"name": "Dessert"}

        url = tag_detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = models.Tag.objects.create(user=self.user, name="Vegetable")

        url = tag_detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tag = models.Tag.objects.filter(user=self.user).exists()
        self.assertFalse(tag)

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to a recipe"""
        tag1 = models.Tag.objects.create(user=self.user, name="Juicy")
        tag2 = models.Tag.objects.create(user=self.user, name="Sweet")

        recipe = models.Recipe.objects.create(
            title="Rice Water", time_minutes=40, price=Decimal("9.0"), user=self.user
        )

        models.Recipe.objects.create(
            title="Yam Porridge", time_minutes=40, price=Decimal("3.5"), user=self.user
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = serializers.TagSerializer(tag1)
        serializer2 = serializers.TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list"""
        tag = models.Tag.objects.create(user=self.user, name="Breakfast")
        models.Tag.objects.create(user=self.user, name="Dinner")

        recipe1 = models.Recipe.objects.create(
            title="Afang Soup", price=Decimal("2.00"), time_minutes=40, user=self.user
        )
        recipe2 = models.Recipe.objects.create(
            title="Vegetable Soup",
            price=Decimal("4.00"),
            time_minutes=50,
            user=self.user,
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
