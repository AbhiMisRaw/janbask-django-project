from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from .permissions import RolePermission
from .serializers import RoleSerializer
from core.utils import roles_collection


class RoleList(APIView):
    """Handles GET and POST requests for RoleModel"""
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        roles = list(roles_collection.find({}))  # Retrieve all roles from the database
        for role in roles:
            role["id"] = str(
                role["_id"]
            )  # Convert ObjectId to string for JSON serialization
            role.pop("_id")
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role_data = serializer.save()  # Use serializer's create method
            role_data.pop("_id")  # Remove _id as it's already mapped to id
            return Response(role_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleDetail(APIView):
    """Handles GET and PUT requests for a specific RoleModel"""
    permission_classes = [IsAuthenticated, RolePermission]

    def get_object(self, pk):
        try:
            object_id = ObjectId(pk)
        except Exception:
            return None

        role = roles_collection.find_one({"_id": object_id})  # Find role by ID
        if role:
            role["_id"] = str(
                role["_id"]
            )  # Convert ObjectId to string for JSON serialization
            role.pop("_id")
        return role

    def get(self, request, pk):
        role = self.get_object(pk)
        if role is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        role = self.get_object(pk)
        if role is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            updated_role = serializer.validated_data
            roles_collection.update_one(
                {"_id": ObjectId(pk)}, {"$set": updated_role}
            )  # Update the role
            updated_role["_id"] = pk  # Keep the existing ID
            return Response(updated_role)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
