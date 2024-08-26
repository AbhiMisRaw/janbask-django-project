# views.py


from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from bson import ObjectId

from core.authentication import CustomJWTAuthentication
from .models import UserActivityModel
from .serializers import UserSerializer, CustomTokenSerializer
from .permissions import UserPermission, AdminPermission
from .utils import (
    users_collection,
    roles_collection,
    activity_collection,
    password_token_collection,
    send_email_to_user,
)

# Testing View for sending email
# @api_view(["GET"])
# def send_mail(request):
#     user = {
#         "name": "Avhi",
#         "email": "sumitmm9506555798@gmail.com",
#         "password": "123456",
#     }
#     send_email_to_user(user)
#     return Response({"message": "OK"}, status=200)


def log_user_activity(email, action, status, details=None):
    activity = UserActivityModel(
        user_email=email,
        action=action,
        status=status,
        details=details or {},
    )
    activity_collection.insert_one(activity.dict())


class UserCreateView(APIView):
    """Creating a user"""

    permission_classes = [IsAuthenticated, UserPermission]

    def get(self, request):
        action = "reading users"
        users = users_collection.find()
        user_list = list(users)

        # Serializing the list of users
        serializer = UserSerializer(user_list, many=True)

        log_user_activity(request.user.email, action, "success")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        action = "Added a User"
        # Create an instance of the serializer with the request data
        serializer = UserSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            # Save the user data if valid
            user_data = serializer.save()
            user = {
                "name": request.data.get("full_name"),
                "email": request.data.get("email"),
                "password": request.data.get("password"),
            }

            # Sending the email
            send_email_to_user(user)
            user.pop("password")
            log_user_activity(request.user.email, action, "success", user)
            return Response(
                serializer.to_representation(user_data), status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    """View for Updating and retrieve a user"""

    permission_classes = [IsAuthenticated, UserPermission]

    def get(self, request, user_id):
        action = "Fetch a user"
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            message = {"error": "Invalid user_id format"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            message = {"error": "User not found"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(instance=user_instance)
        log_user_activity(request.user.email, action, "success")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        action = "Updating a user"
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            message = {"error": "Invalid user_id format"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            message = {"error": "User not found"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        # Create an instance of the serializer with the request data and partial=True
        serializer = UserSerializer(
            instance=user_instance, data=request.data, partial=True
        )

        if serializer.is_valid():
            updated_user = serializer.save()
            log_user_activity(request.user.email, action, "success")
            return Response(
                serializer.to_representation(updated_user), status=status.HTTP_200_OK
            )
        else:
            log_user_activity(request.user.email, action, "failed", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(APIView):
    """View for 3.3 deactivating the User"""

    permission_classes = [IsAuthenticated, UserPermission]

    def patch(self, request, user_id):
        action = "Deactivating a user"
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            message = {"error": "Invalid user_id format"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            message = {"error": "User not found"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        payload = {"is_active": False}
        # Update the user document in MongoDB
        result = users_collection.update_one({"_id": object_id}, {"$set": payload})
        # print(result.modified_count)
        if result.modified_count > 0:
            message = f"User with {user_instance.get('full_name')} is deactivated"
            log_user_activity(request.user.email, action, "success", message)
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            message = {"error": "Failed to deactivate user"}
            log_user_activity(request.user.email, action, "failed", message)
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserActivityView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request, user_id):
        action = "Getting activities of a User"
        try:
            user_id = ObjectId(user_id)
        except Exception:
            message = {"error": "Please provide correct user id"}
            log_user_activity(request.user.email, action, "fail", message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        user = users_collection.find_one({"_id": user_id})
        if not user:
            message = {"error": "No user found"}
            log_user_activity(request.user.email, action, "fail", message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        activities = list(activity_collection.find({"user_email": user.get("email")}))

        log_user_activity(request.user.email, action, "success")
        for activity in activities:
            activity["_id"] = str(activity["_id"])  # Convert ObjectId to string

        return Response(activities, status=status.HTTP_200_OK)


class UserRoleView(APIView):
    """View for following requirements
    4.2 Assigning a role to user
    4.4 fetching the permission of a User
    """

    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self, user_id):
        user = users_collection.find_one({"_id": ObjectId(user_id)})  # Find role by ID
        return user

    def get(self, request, user_id):
        action = "Fetching Role and Permission of a user"
        user = self.get_object(user_id)
        if user is None:
            log_user_activity(request.user.email, action, "failed")
            return Response(status=status.HTTP_404_NOT_FOUND)
        log_user_activity(request.user.email, action, "success")
        if user.get("role") is None:
            return Response(
                {"message": "No Role assigned to this User"},
                status=status.HTTP_201_CREATED,
            )
        role = roles_collection.find_one({"_id": ObjectId(user.get("role"))})
        response = {"name": user.get("full_name")}
        response["email"] = user.get("email")
        response["role_name"] = role.get("name")
        response["permissions"] = role.get("permissions")
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        action = "Assigning a role to user"
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            message = {"error": "Please provide a valid user id"}
            log_user_activity(request.user.email, action, "fail", message)
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_name = request.data.get("role_name")
        if not role_name:
            message = {"error": "Role name is required"}
            log_user_activity(request.user.email, action, "fail", message)
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_object = roles_collection.find_one({"name": role_name})
        if not role_object:
            message = {"error": "Role not found"}
            log_user_activity(request.user.email, action, "fail", message)
            return Response(
                message,
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update the user's role
        users_collection.update_one(
            {"_id": user_object_id}, {"$set": {"role": role_object.get("_id")}}
        )
        serializer = UserSerializer(self.get_object(user_id))
        log_user_activity(request.user.email, action, "success", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
