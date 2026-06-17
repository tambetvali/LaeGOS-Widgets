import os

SESSION_SECRET_KEY = "dev-secret-key"

GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""

# Read MongoDB URI from environment variable
MONGO_URI = os.environ.get("MONGO_URI")

DB_NAME = "laegos"
USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "sessions"
