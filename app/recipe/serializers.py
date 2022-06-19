""" Serializers for the Recipe APIs"""
from rest_framework import serializers

from core import models


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = models.Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = models.Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""

    # This is a nested serializer. And by default it is readonly
    # We are using many=True, to show that it is going to be a list.
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = models.Recipe
        fields = ["title", "link", "time_minutes", "price", "tags", "ingredients"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # this is to ensure that each tag that is being created is assigned a user.
        auth_user = self.context["request"].user
        # this is the thing that loops through the tags, it gets them if it sees them or it creates them if it doesnt see them.
        for tag in tags:
            tag_obj, created = models.Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed"""
        """The _before the method name indicated that this method is supposed to be used internally only."""
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, created = models.Ingredient.objects.get_or_create(
                user=auth_user, **ingredient
            )
            recipe.ingredients.add(
                ingredient_obj
            )  # we are adding the new ingredient or retrived ingredient to the recipe object for the ingredient

    # Overwrite the create function to create a recipe with tags that would
    # have otherwise be read only.

    def create(self, validated_data):
        """Create a recipe"""
        # remove tags from validated data and if it doesnt exist default to empty list.
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        """The main reason we are removing the tags is because, if we just pass it in to the recipe like that, it wont work, because it is not in the Recipe model. It is expected to be saved as a related field to the recipe object."""
        recipe = models.Recipe.objects.create(**validated_data)
        # Get the authenticated user.
        # We use this to get the authenticated user in the serializer. The self.context is passed by the view to the serializer.
        # auth_user = self.context["request"].user
        # Now we are looping through all the tags we poped and stored in
        # name = tag['name]
        # for tag in tags:
        #     tag_obj, created = models.Tag.objects.get_or_create(user=auth_user, **tag)
        #     recipe.tags.add(tag_obj)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    # We are creating a separate serializer because uploading images, we dont need the extra fields that is part of the recipe. Again, it is best practice to build an api with one type of data. Not different. That's an API with form data and multipart data which is image. This makes our api data structures clean, and easy to use and understandable.

    class Meta:
        model = models.Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}
