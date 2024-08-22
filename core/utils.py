from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# uri = "mongodb+srv://django-ms:Kl8gRlfg98KPlu1l@cluster0.eeg4cws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(os.getenv("MONGODB_URL"))

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.my_database
users_collection = db.users
roles_collection = db.roles
token_blacklist = db.token_blacklist
activity_collection = db.activities
