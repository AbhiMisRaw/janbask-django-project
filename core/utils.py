from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from django.core.mail import EmailMessage
from django.conf import settings
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
password_token_collection = db.password_tokens



def send_email_to_user(user):
    subject = "Account Creation Confirmation "
    first_name = user.get("name").split()[0]
    message = f"Hello {first_name} You'r account has been created. The credential for your account is : {user}"
    from_email = settings.EMAIL_HOST
    recipient_list = [user.get("email")]
    print("Sending Mail for user  : ", user)
    # send_mail(subject, message, from_email, recipient_list)
    email = EmailMessage(subject, message, from_email, recipient_list)
    x = email.send(fail_silently=True)
    print(f" {email}  {x}")
    print("Mail Sent")
