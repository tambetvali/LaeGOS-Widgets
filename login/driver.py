from flask import session

def is_logged_in():
    return "user" in session

def get_current_user():
    return session.get("user")

def get_user_email():
    user = session.get("user")
    return user.get("email") if user else None

def get_user_metadata():
    user = session.get("user")
    if not user:
        return None
    return {
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
        "username": user.get("username"),
    }
