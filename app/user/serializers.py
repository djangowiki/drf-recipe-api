""" Serializers for the User APi """
from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        """Declare the model and fields for the serializer"""

        model = get_user_model()
        fields = ["email", "name", "password"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}
        # This create method is only called after the validation for the serializer is successful.

        def create(self, validated_data):
            """Overide the default create method for the serializer, so we can use our own create_user method that has encryption for user password. So here, we are just creating a user with encrypted password."""
            user = get_user_model().objects.create_user(**validated_data)
            return user
