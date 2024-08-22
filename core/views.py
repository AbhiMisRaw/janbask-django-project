# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from bson import ObjectId

from core.authentication import CustomJWTAuthentication
from .serializers import UserSerializer, CustomTokenSerializer
from .permissions import UserPermission, AdminPermission
from .utils import users_collection, roles_collection, activity_collection


class UserCreateView(APIView):
    """Creating a user"""

    permission_classes = [IsAuthenticated, UserPermission]

    def get(self, request):
        users = users_collection.find()
        user_list = list(users)
        print(f"Authenticate user : {request.user}")
        # Serializing the list of users
        serializer = UserSerializer(user_list, many=True)
        # Sending an email to user.
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Create an instance of the serializer with the request data
        serializer = UserSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            # Save the user data if valid
            user_data = serializer.save()
            return Response(
                serializer.to_representation(user_data), status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    """View for Updating and retrieve a user"""

    permission_classes = [IsAuthenticated, UserPermission]

    def get(self, request, user_id):
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            return Response(
                {"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(instance=user_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            return Response(
                {"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create an instance of the serializer with the request data and partial=True
        serializer = UserSerializer(
            instance=user_instance, data=request.data, partial=True
        )

        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(
                serializer.to_representation(updated_user), status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(APIView):
    """View for 3.3 deactivating the User"""

    def patch(self, request, user_id):
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            return Response(
                {"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the user document from the collection
        user_instance = users_collection.find_one({"_id": object_id})

        if not user_instance:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        payload = {"is_active": False}
        # Update the user document in MongoDB
        result = users_collection.update_one({"_id": object_id}, {"$set": payload})
        # print(result.modified_count)
        if result.modified_count > 0:
            message = f"User with {user_instance.get('full_name')} is deactivated"
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to deactivate user"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
        user = self.get_object(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
        print(response)
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            return Response(
                {"message": "Please provide a valid user id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_name = request.data.get("role_name")
        if not role_name:
            return Response(
                {"message": "Role name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_object = roles_collection.find_one({"name": role_name})
        if not role_object:
            return Response(
                {"message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        print(role_object)
        # Update the user's role
        users_collection.update_one(
            {"_id": user_object_id}, {"$set": {"role": role_object.get("_id")}}
        )

        serializer = UserSerializer(self.get_object(user_id))
        return Response(serializer.data, status=status.HTTP_200_OK)


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
