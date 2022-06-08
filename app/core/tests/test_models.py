from django.contrib.auth import get_user_model
from django.test import TestCase


class TestModel(TestCase):
    """Test Model"""

    def test_create_user_with_email_successful(self):
        """Test for successful user registration with email"""
        email = "test@example.com"
        password = "changepassword123"

        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.COM", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without email raises a value error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample123")

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            "test@example", "Ikenna", "changepass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
