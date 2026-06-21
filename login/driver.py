from flask import session
from github_gist import save_registry


def is_logged_in():
    return "user" in session


def get_current_user():
    return session.get("user")


def get_registry_value(key):
    reg = session.get("registry", {})
    return reg.get(key)


def set_registry_value(key, value):
    reg = session.get("registry", {})
    reg[key] = value
    session["registry"] = reg

    if "user" in session:
        access_token = session.get("github_token")
        gist_id = session.get("gist_id")
        if access_token and gist_id:
            save_registry(access_token, gist_id, reg)

    return True
