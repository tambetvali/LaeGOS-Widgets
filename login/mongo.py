import os
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB = os.environ.get("MONGODB_DB", "laegos")

_client = MongoClient(MONGODB_URI)
_db = _client[MONGODB_DB]

users_col = _db["users"]
settings_col = _db["settings"]
data_col = _db["data"]


def get_user_by_email(email):
    return users_col.find_one({"email": email})


def get_user_by_id(user_id):
    if not user_id:
        return None
    try:
        return users_col.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def create_user(email):
    user = {
        "email": email,
        "format": "LaeGOS",
    }
    result = users_col.insert_one(user)
    user["_id"] = result.inserted_id

    from .defaults import DEFAULT_SETTINGS
    for key, value in DEFAULT_SETTINGS.items():
        settings_col.insert_one({
            "user_id": user["_id"],
            "key": key,
            "value": value,
        })

    return user


def get_user_settings(user_id):
    return {
        s["key"]: s["value"]
        for s in settings_col.find({"user_id": ObjectId(user_id)})
    }


def reset_user_data(user_id):
    oid = ObjectId(user_id)
    settings_col.delete_many({"user_id": oid})
    data_col.delete_many({"user_id": oid})

    from .defaults import DEFAULT_SETTINGS
    for key, value in DEFAULT_SETTINGS.items():
        settings_col.insert_one({
            "user_id": oid,
            "key": key,
            "value": value,
        })


def get_user_storage_usage_bytes(user_id):
    oid = ObjectId(user_id)
    settings_count = settings_col.count_documents({"user_id": oid})
    data_count = data_col.count_documents({"user_id": oid})
    return (settings_count + data_count) * 512
