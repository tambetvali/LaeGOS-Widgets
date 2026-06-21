from flask import session
from github_app import get_user_metadata, update_user_metadata


def is_logged_in():
    return "user" in session and "github_token" in session


def get_current_user():
    return session.get("user")


def _get_registry_container():
    """
    Returns (registry_dict, logged_in_bool).

    - If logged in: use session["registry"]
    - If logged out: use session["anon_registry"]
    """
    if is_logged_in():
        reg = session.get("registry", {})
        session["registry"] = reg
        return reg, True

    # Anonymous registry
    reg = session.get("anon_registry", {})
    session["anon_registry"] = reg
    return reg, False


def get_registry_value(key):
    registry, _ = _get_registry_container()
    return registry.get(key)


def set_registry_value(key, value):
    registry, logged_in = _get_registry_container()
    registry[key] = value

    if logged_in:
        # Save to session
        session["registry"] = registry

        # Persist to GitHub metadata using OAuth token
        oauth_token = session.get("github_token")
        username = session.get("user")

        if oauth_token and username:
            update_user_metadata(oauth_token, username, registry)

    else:
        # Anonymous registry
        session["anon_registry"] = registry

    return True
