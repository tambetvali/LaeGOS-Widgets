from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import uuid

from login.login_config import (
    MONGO_URI,
    DB_NAME,
    USERS_COLLECTION,
    SESSIONS_COLLECTION,
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

users_col = db[USERS_COLLECTION]
sessions_col = db[SESSIONS_COLLECTION]


def _check_connection():
    try:
        client.admin.command("ping")
        return True
    except errors.PyMongoError:
        return False


def get_user_by_email(email: str):
    try:
        if not _check_connection():
            return {"error": "database_down"}
        return users_col.find_one({"email": email})
    except errors.PyMongoError:
        return {"error": "database_down"}


def create_user(email: str, name: str, picture: str):
    try:
        if not _check_connection():
            return {"error": "database_down"}
        user = {
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
        }
        users_col.insert_one(user)
        return user
    except errors.PyMongoError:
        return {"error": "database_down"}


def update_last_login(email: str):
    try:
        if not _check_connection():
            return {"error": "database_down"}
        users_col.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except errors.PyMongoError:
        return {"error": "database_down"}


def create_session(email: str):
    try:
        if not _check_connection():
            return {"error": "database_down"}
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "email": email,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=7),
        }
        sessions_col.insert_one(session)
        return session_id
    except errors.PyMongoError:
        return {"error": "database_down"}


def get_session(session_id: str):
    try:
        if not _check_connection():
            return {"error": "database_down"}
        return sessions_col.find_one({"session_id": session_id})
    except errors.PyMongoError:
        return {"error": "database_down"}
