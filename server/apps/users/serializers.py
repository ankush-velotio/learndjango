from rest_framework import serializers
from users import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "name", "email", "password"]
        # Hide the password. Don't return the password in the response
        extra_kwargs = {"password": {"write_only": True}}

    # hash the password
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Todo
        fields = "__all__"

    def create(self, validated_data):
        editors = validated_data.pop("editors")
        instance = self.Meta.model(**validated_data)
        instance.owner = self.context.get("owner")
        instance.created_by = self.context.get("created_by")
        instance.save()
        instance.editors.set(editors)
        return instance
