""" Test for Recipe API """
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from recipe import serializers
from core import models

import tempfile
import os
from PIL import Image

RECIPE_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    """Create and return a recipe detail url"""
    # Instead of hardcoding the url, we use a function to pass in the recipe id
    return reverse("recipe:recipe-detail", args=[recipe_id])


# Create a helper function that allows us to generate an image url to the upload endpoint.
def image_upload_url(recipe_id):
    """Create and return an image upload url."""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


# Create a helper function in our test for creating a recipe
def create_recipe(user, **params):
    defaults = {
        "title": "Recipe Title",
        "time_minutes": 22,
        "description": "Sample description",
        "price": Decimal("5.5"),
        "link": "http://www.localhost:5000/recipe/how-to-cook-rice",
    }
    defaults.update(
        params
    )  # create the recipe with defaults or the dictionary provided in the params.

    recipe = models.Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password="testpass123")
        # self.user = get_user_model().objects.create_user(
        #     "test@example.com", "testpass123"
        # )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.all().order_by(
            "-id"
        )  # we got the recipe and pass it to the serializers
        serializer = serializers.RecipeSerializer(
            recipes, many=True
        )  # we need this serializer inorder to compare the recipes in the database with the one we are expected to get from the serializers.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipe is limited to authenticiated user"""
        # other_user = get_user_model().objects.create_user(
        #     "otheruser@example.com", "password123"
        # )
        other_user = create_user(email="otheruser@example.com", password="password123")
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = serializers.RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)

        serializer = serializers.RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    # We are creating a recipe using our api and testing it for real not using our hardcoded examples up there.
    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            "title": "Test recipe",
            "description": "Information about recipe",
            "time_minutes": 30,
            "price": Decimal("4.5"),
        }
        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # recipe = models.Recipe.objects.get(id=res.data["id"])

        # for key, value in payload.items():
        #     self.assertEqual(getattr(recipe, key), value)
        # self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        originalLink = "http://example.com/recipe/pdf"
        recipe = create_recipe(title="Sample Recipe", link=originalLink, user=self.user)

        payload = {"title": "Updated Recipe Name"}
        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, originalLink)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe"""
        recipe = create_recipe(
            title="Recipe title", link="https://example.com/recipe/pdf", user=self.user
        )

        payload = {
            "title": "New updated recipe title",
            "description": "Recipe description",
            "price": Decimal("2.55"),
            "time_minutes": 30,
            "link": "https://www.example.com/update",
        }

        url = recipe_detail_url(recipe.id)

        res = self.client.put(url, payload)

        # assersstions.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_returns_error(self):
        """Test updating recipe user returns an error"""
        new_user = create_user(email="newuser@example.com", password="newpass123")
        recipe = create_recipe(user=self.user)
        # print(self.user)
        # print(new_user)
        # print(recipe)
        payload = {"user": new_user.id}
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe is successful"""
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test deleting other users recipe returns an error"""
        new_user = create_user(email="new_user@example.com", password="password123")
        recipe = create_recipe(user=new_user)
        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(models.Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tag"""
        payload = {
            "title": "Student food for dinner",
            "time_minutes": 40,
            "price": Decimal("10.5"),
            "tags": [{"name": "Dessert"}, {"name": "Dinner"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = models.Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating recipe with existing tags"""
        tag_indian = models.Tag.objects.create(user=self.user, name="Indian")

        payload = {
            "title": "Indian Food",
            "time_minutes": 60,
            "price": Decimal("4.50"),
            "description": "Info details",
            "tags": [{"name": "Indian"}, {"name": "Breakfast22"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")
        # print(RECIPE_URL, payload, res.status_code)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = models.Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        # The actual testing or unique testing here.
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_recipe_update(self):
        """Test creating a new tag on recipe update"""
        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"name": "bread"}]}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Fix errror when you uncomment code.
        new_tag = models.Tag.objects.get(user=self.user, name="bread")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = models.Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = models.Tag.objects.create(user=self.user, name="lunch")
        # the payload is used to change our breakfast tag.
        payload = {"tags": [{"name": "lunch"}]}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing recipe tags"""
        tag = models.Tag.objects.create(user=self.user, name="dinner")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        # We achieve this by passing an empty list to the tags and sending it to the API as a patch request.
        url = recipe_detail_url(recipe.id)
        payload = {"tags": []}

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients"""
        payload = {
            "title": "Banga Soup",
            "price": Decimal("4.50"),
            "time_minutes": 50,
            "ingredients": [{"name": "Akwu"}, {"name": "Maggi"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(len(res.data), 1)
        recipes = models.Recipe.objects.filter(user=self.user)
        self.assertEqual(len(recipes), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a recipe with existing ingredient"""
        ingredient = models.Ingredient.objects.create(user=self.user, name="Lemon")

        payload = {
            "title": "Nigerian Soup",
            "time_minutes": 40,
            "price": Decimal("5.50"),
            "ingredients": [{"name": "Lemon"}, {"name": "Oil"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = models.Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe"""
        recipe = create_recipe(user=self.user)

        payload = {"ingredients": [{"name": "Egwusi"}]}

        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = models.Ingredient.objects.get(user=self.user, name="Egwusi")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        """All we are doing in this test is removing the pepper and replacing it with chilli"""
        ingredient1 = models.Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)

        recipe.ingredients.add(ingredient1)

        ingredient2 = models.Ingredient.objects.create(user=self.user, name="Chilli")

        payload = {"ingredients": [{"name": "Chilli"}]}

        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing recipe ingredients."""
        ingredient = models.Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}

        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags"""
        recipe1 = create_recipe(user=self.user, title="Thai Vegetable Curry")
        recipe2 = create_recipe(user=self.user, title="Nsara Soup with beef")
        tag1 = models.Tag.objects.create(user=self.user, name="Vegan")
        tag2 = models.Tag.objects.create(user=self.user, name="Vegeterian")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = create_recipe(user=self.user, title="Fish and chips")

        params = {"tags": f"{tag1.id}, {tag2.id}"}

        res = self.client.get(RECIPE_URL, params)

        serializerRecipe1 = serializers.RecipeSerializer(recipe1)
        sertializerRecipe2 = serializers.RecipeSerializer(recipe2)
        serializerRecipe3 = serializers.RecipeSerializer(recipe3)

        self.assertIn(serializerRecipe1.data, res.data)
        self.assertIn(sertializerRecipe2.data, res.data)
        self.assertNotIn(serializerRecipe3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients."""
        recipe1 = create_recipe(user=self.user, title="Beans Water")
        recipe2 = create_recipe(user=self.user, title="Rice Water Milk")
        recipe3 = create_recipe(user=self.user, title="Yam Porridge")

        ingredient1 = models.Ingredient.objects.create(user=self.user, name="Oil")
        ingredient2 = models.Ingredient.objects.create(user=self.user, name="Maggi")

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        params = {"ingredients": f"{ingredient1.id}, {ingredient2.id}"}

        res = self.client.get(RECIPE_URL, params)

        serializerRecipe1 = serializers.RecipeSerializer(recipe1)
        serializerRecipe2 = serializers.RecipeSerializer(recipe2)
        serializerRecipe3 = serializers.RecipeSerializer(recipe3)

        self.assertIn(serializerRecipe1.data, res.data)
        self.assertIn(serializerRecipe2.data, res.data)
        self.assertNotIn(serializerRecipe3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for Image Upload API"""

    # Runs before the test.
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123"
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    # Runs after the test.
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        # Python Helper function that allows you to create a temporary file.
        # We are using this name temporary to create a temporary image file
        # in jpeg we can use to test our endpoint.
        with tempfile.NamedTemporaryFile(suffix=".jpg") as img_file:
            img = Image.new(
                "RGB", (10, 10)
            )  # creates a simple blank image file. THis is actually stored in memory.
            img.save(
                img_file, format="JPEG"
            )  # we are then saving this to the temporary file that we created.
            img_file.seek(0)  # go back to the beginning of the file so we can upload.
            payload = {"image": img_file}  # paylod to be uploaded.
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {"image": "notanimage"}

        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
