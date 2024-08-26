import secrets
import string
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.authentication import CustomJWTAuthentication
from core.serializers import CustomTokenSerializer
from core.views import log_user_activity
from core.utils import (
    users_collection,
    password_token_collection,
    reset_password_email,
)


def generate_token(length=50):
    # Define the characters to use: letters (uppercase + lowercase) and digits
    characters = string.ascii_letters + string.digits
    # Generate a secure random token
    token = "".join(secrets.choice(characters) for _ in range(length))

    return token


class CustomLoginView(APIView):
    """Views for 1.1 and 1.2 for Login purpose"""

    def post(self, request, *args, **kwargs):
        # Use the custom serializer to validate and authenticate the user
        serializer = CustomTokenSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Call the logout method from the CustomJWTAuthentication class
        auth_class = CustomJWTAuthentication()
        logout_response = auth_class.logout(request)
        return Response(logout_response, status=status.HTTP_200_OK)


class UserForgetPasswordView(APIView):
    def post(self, request):
        action = "Chaning password Request"
        email = request.data.get("email")
        if email is None or email == "":
            return Response(
                {"message": "Email field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = users_collection.find_one({"email": email})
        if not user:
            return Response(
                {"error": "No User found with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )
        token = generate_token()
        print(token)
        token = generate_token()

        # Save token and associated data in the password_token_collection
        password_token_collection.insert_one(
            {
                "email": email,
                "token": token,
                "created_at": datetime.utcnow(),  # Use UTC to avoid timezone issues
            }
        )

        # Send response with the full reset link
        reset_link = f"http://localhost:8000/api/v1/account/password/recover/{token}/"
        reset_password_email(email, reset_link)
        log_user_activity(email, action, "success")
        return Response(
            {
                "message": "Link has been sent to you mail and It's valid for 10 mins",
                "reset_link": reset_link,
            },
            status=status.HTTP_200_OK,
        )


class UserSetPasswordView(APIView):
    def post(self, request, token):
        action = "password reset"
        # Find the token in the database
        if len(token) != 50:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the new password from the request
        new_password = request.data.get("password")
        if not new_password:
            return Response(
                {"message": "Password field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token_entry = password_token_collection.find_one({"token": token})

        if not token_entry:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the token is expired (more than 10 minutes old)
        token_creation_time = token_entry["created_at"]
        if datetime.utcnow() > token_creation_time + timedelta(minutes=10):
            message = {"error": "Token has expired. Please try again."}
            log_user_activity(token_entry.get("email"), action, "fail", message)
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = make_password(new_password)

        # Update the user's password in the users collection using the email from the token entry
        users_collection.update_one(
            {"email": token_entry["email"]}, {"$set": {"password": hashed_password}}
        )
        log_user_activity(token_entry.get("email"), action, "success")
        # Optionally, you may want to delete the token after it's been used
        password_token_collection.delete_one({"token": token})

        return Response(
            {"message": "Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
