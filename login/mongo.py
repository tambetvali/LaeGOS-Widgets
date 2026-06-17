from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid

from login_config import (
    MONGO_URI,
    DB_NAME,
    USERS_COLLECTION,
    SESSIONS_COLLECTION,
)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db[USERS_COLLECTION]
sessions = db[SESSIONS_COLLECTION]


def get_user_by_email(email: str):
    return users.find_one({"email": email})


def create_user(email: str, name: str, picture: str):
    user = {
        "email": email,
        "name": name,
        "picture": picture,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }
    users.insert_one(user)
    return user


def update_last_login(email: str):
    users.update_one(
        {"email": email},
        {"$set": {"last_login": datetime.utcnow()}}
    )


def create_session(email: str):
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "email": email,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=7),
    }
    sessions.insert_one(session)
    return session_id


def get_session(session_id: str):
    return sessions.find_one({"session_id": session_id})
