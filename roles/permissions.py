from rest_framework.permissions import BasePermission
from core.utils import roles_collection
from bson import ObjectId


class RolePermission(BasePermission):
    """
    Custom permission to allow or deny access based on user roles and the HTTP method being used.
    """

    # Map HTTP methods to permissions
    method_permission_map = {
        "GET": "read_role",
        "POST": "write_role",
        "PUT": "write_role",
        "PATCH": "write_role",
    }

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user or not user.is_authenticated:
            return False

        # Retrieve the user's role from MongoDB
        role_id = user.role
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
