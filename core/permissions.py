from rest_framework.permissions import BasePermission
from .utils import roles_collection
from bson import ObjectId


class UserPermission(BasePermission):
    """
    Custom permission to allow or deny access based on user roles and the HTTP method being used.
    """

    # Map HTTP methods to permissions
    method_permission_map = {
        "GET": "read_user",
        "POST": "write_user",
        "PUT": "write_user",
        "PATCH": "write_user",
    }

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user or not user.is_authenticated:
            return False

        # Retrieve the user's role from MongoDB
        role_id = user.role
        print(user)
        if role_id is None or role_id == "None":
            print("No role is assigned")
            return False
        role = roles_collection.find_one({"_id": ObjectId(role_id)})

        if not role:
            return False  # If the role doesn't exist, deny access

        # Determine the required permission based on the request method
        required_permission = self.method_permission_map.get(request.method)

        # Check if the role includes the required permission
        if required_permission and required_permission in role.get("permissions", []):
            return True

        return False


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user or not user.is_authenticated:
            return False

        # Retrieve the user's role from MongoDB
        role_id = user.role
        print(user)
        if role_id is None or role_id == "None":
            print("No role is assigned")
            return False
        role = roles_collection.find_one({"_id": ObjectId(role_id)})

        if not role:
            return False

        if role.get("name") == "Admin":
            return True

        return False
