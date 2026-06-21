from flask import session
from github_gist import save_registry


def is_logged_in():
    return "user" in session


def get_current_user():
    return session.get("user")


def get_registry_value(key):
    # Unified registry access: logged-in OR anonymous
    if "user" in session:
        reg = session.get("registry", {})
    else:
        reg = session.get("anon_registry", {})
    return reg.get(key)


def set_registry_value(key, value):
    # Unified registry write
    if "user" in session:
        reg = session.get("registry", {})
        reg[key] = value
        session["registry"] = reg

        access_token = session.get("github_token")
        gist_id = session.get("gist_id")
        if access_token and gist_id:
            save_registry(access_token, gist_id, reg)

    else:
        reg = session.get("anon_registry", {})
        reg[key] = value
        session["anon_registry"] = reg

    return True
