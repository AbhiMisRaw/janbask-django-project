# authentication.py
from datetime import datetime
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from bson import ObjectId
from core.models import UserModel
from .utils import users_collection, token_blacklist


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise InvalidToken("Token contained no recognizable user identification")
        print(validated_token)
        # Convert the user_id string to a MongoDB ObjectId
        try:
            object_id = ObjectId(user_id)
        except Exception as e:
            raise AuthenticationFailed("Invalid user ID format")
        user_data = users_collection.find_one({"_id": object_id})
        if not user_data:
            raise AuthenticationFailed("User not found")

        if "_id" in user_data:
            user_data["_id"] = str(user_data["_id"])
        user = UserModel(**user_data)
        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return user

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Check if the token is blacklisted
        if token_blacklist.find_one({"token": raw_token}):
            raise AuthenticationFailed("You are Log-out, Login Again")

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def logout(self, request):
        # Get the token from the Authorization header
        raw_token = self.get_raw_token(self.get_header(request))
        if not raw_token:
            raise AuthenticationFailed("No token provided")

        # Blacklist the token
        token_blacklist.insert_one(
            {"token": raw_token, "blacklisted_on": datetime.utcnow()}
        )

        # Remove the user object from the request
        request.user = None

        return {"message": "Successfully logged out"}
        
