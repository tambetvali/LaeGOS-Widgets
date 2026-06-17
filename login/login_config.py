import os

# Flask session secret
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "dev-secret-key")

# Google OAuth credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# MongoDB connection string
# Example: mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_URI = os.environ.get("MONGO_URI", "")

# Database names
DB_NAME = "laegos"
USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "sessions"
