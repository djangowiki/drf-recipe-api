""" Tests for the user API """
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
# user is the app, and the create is the link.
# It returns the full url path into our project.

# Create a helper function to createour test users


def create_user(**params):
    """Creates and returns a user"""
    return get_user_model().objects.create_user(**params)


# The unauthenticated user tests.
class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    # Setup the APIClient
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(
            email=payload["email"]
        )  # check that the user is registered in the database with the correct email
        self.assertTrue(
            user.check_password(payload["password"])
        )  # check the user is registered with the correct paasword.
        self.assertNotIn(
            "password", res.data
        )  # ensures we are not returning the password to the user.

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars"""
        payload = {"email": "test@example.com", "password": "te", "name": "Test Name"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )  # making sure the user doesn't get created in the database.
        self.assertFalse(user_exists)
