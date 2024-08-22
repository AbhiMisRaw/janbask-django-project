from rest_framework import serializers
from bson import ObjectId
from core.utils import roles_collection 

class RoleSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True) 
    name = serializers.CharField(min_length=3, max_length=50)
    permissions = serializers.ListField(child=serializers.CharField())

    def create(self, validated_data):
        # Insert the validated data into the MongoDB collection
        result = roles_collection.insert_one(validated_data)
        # Retrieve the inserted document with the new _id
        validated_data["_id"] = result.inserted_id
        validated_data["id"] = str(validated_data["_id"])  # Convert ObjectId to string
        return validated_data

    def update(self, instance, validated_data):
        # Update the instance with the new data
        roles_collection.update_one({"_id": ObjectId(instance["_id"])}, {"$set": validated_data})
        validated_data['_id'] = instance['_id']  # Keep the existing _id
        validated_data['id'] = str(validated_data['_id'])  # Convert ObjectId to string
        return validated_data
