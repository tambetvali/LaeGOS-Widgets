from flask import session

def is_logged_in():
    return "user" in session

def get_current_user():
    return session.get("user")

def get_registry_value(key):
    user = session.get("user")
    if not user:
        return None
    return user.get("registry", {}).get(key)

def set_registry_value(key, value):
    user = session.get("user")
    if not user:
        return False
    user.setdefault("registry", {})[key] = value
    session["user"] = user
    return True
