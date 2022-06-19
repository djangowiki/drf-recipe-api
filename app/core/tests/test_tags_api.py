""" Test for tags API """
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
