from flask import session
from github_app import (
    get_installation_id,
    get_installation_token,
    save_registry
)


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
        username = session["user"]
        installation_id = get_installation_id(username)
        installation_token = get_installation_token(installation_id)
        save_registry(installation_token, username, reg)

    return True
