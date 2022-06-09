""" User API Views """
from rest_framework import generics
from user import serializers


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = serializers.UserSerializer
