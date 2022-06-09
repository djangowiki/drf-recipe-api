""" User API URL Mappings """
from django.urls import path
from user import views

app_name = "user"  # this is for our reverse url in our test.

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
]
