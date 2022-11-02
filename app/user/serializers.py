""" Serializers for the User APi """
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        """Declare the model and fields for the serializer"""

        model = get_user_model()
        fields = ["email", "name", "password"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}
        # This create method is only called after the validation for the serializer is successful.

        def create(self, validated_data):
            """Overide the default create method for the serializer,
             so we can use our own create_user method that has encryption for user password. 
             So here, we are just creating a user with encrypted password."""
            user = get_user_model().objects.create_user(**validated_data)
            return user

        # Override the default update method for the user serializer to avoid saving the password in plain text.
        def update(self, instance, validated_data):
            """Update and returns user."""
            password = validated_data.pop("password", None)
            user = super().update(
                instance, validated_data
            )  # use the method in the model to do the update for us.
            if password:
                user.set_password(password)
                user.save()
            return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the auth token"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs
