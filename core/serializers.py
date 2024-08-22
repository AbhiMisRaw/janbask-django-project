# serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password, check_password

from .models import UserModel
from .utils import users_collection, roles_collection

# from .models import RoleModel


# function to get user data from MongoDB
def get_user_from_mongodb(email: str) -> UserModel:
    user_data = users_collection.find_one({"email": email})

    if user_data:
        # Ensure _id is included
        # print(f" User fdata from Mogo {user_data}")
        user_data["_id"] = str(user_data.get("_id"))
        user_data["role"] = str(user_data.get("role"))
        print(f" User fdata from Mogo {user_data}")
        return UserModel(**user_data)
    else:
        raise ValueError("No user found")


class UserSerializer(serializers.Serializer):
    """Serializers for creating user"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=100, required=False)
    is_active = serializers.BooleanField(default=True)
    role = serializers.CharField(required=False, allow_null=True)

    def validate_email(self, value):
        # Check if the email already exists in the database
        if users_collection.find_one({"email": value}):
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_role(self, value):
        # If a role is provided, check that it exists in the roles collection
        if value and not roles_collection.find_one({"name": value}):
            raise serializers.ValidationError("Role does not exist")
        return value

    def create(self, validated_data):
        # Encrypting the password
        validated_data["password"] = make_password(validated_data["password"])

        # Validate and insert the data using Pydantic
        user = UserModel(**validated_data)
        result = users_collection.insert_one(user.dict())

        # Add MongoDB _id to the response
        validated_data["_id"] = str(result.inserted_id)

        return validated_data

    def update(self, instance, validated_data):
        # Update only the fields provided in validated_data
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        if "role" in validated_data:
            role_id = roles_collection.find_one({"name": validated_data["role"]})
            validated_data["role"] = role_id

        instance.update(validated_data)
        users_collection.update_one({"_id": instance["_id"]}, {"$set": validated_data})
        return instance

    def to_representation(self, instance):
        role_name = str(instance.get("role", ""))
        return {
            "id": str(instance.get("_id", "")),
            "email": instance["email"],
            "full_name": instance.get("full_name", ""),
            "is_active": instance.get("is_active", True),
            "role": role_name,
        }


class CustomTokenSerializer(serializers.Serializer):
    """Serializer for obtaining JWT Token"""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise AuthenticationFailed("Email and password are required")

        try:
            print(email)
            user = get_user_from_mongodb(email)
            print(f"USER : {user}")
        except ValueError:
            raise AuthenticationFailed("No user found with this email")
        print(user)

        # Check if the password is correct
        if not check_password(password, user.password):
            raise AuthenticationFailed("Incorrect password")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        # Create refresh and access tokens manually
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "refresh": str(refresh),
            "access": str(access),
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
        }
