from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# to handle the registeration of the user, serialization is needed. 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        # this will create user and handle password handling automatically 
        user = User.objects.create_user(**validated_data)
        return user