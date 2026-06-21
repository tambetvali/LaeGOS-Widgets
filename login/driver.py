from flask import session
import requests

from github_app import get_installation_token_for_user

GITHUB_API = "https://api.github.com"
METADATA_NAMESPACE = "LaeGOS"


# ---------------------------
#  INTERNAL HELPERS
# ---------------------------

def _get_installation_token():
    username = session.get("user")
    if not username:
        return None
    return get_installation_token_for_user(username)


def _sync_registry_to_github(registry):
    """
    Persist the registry dict into GitHub user metadata under our namespace.
    """
    token = _get_installation_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {METADATA_NAMESPACE: registry}

    try:
        requests.patch(f"{GITHUB_API}/user/metadata", headers=headers, json=payload)
    except Exception:
        pass  # Never break UX


def _get_registry_container():
    """
    Returns (registry_dict, logged_in_bool).

    - If logged in: use session["registry"]
    - If logged out: use session["anon_registry"]
    """
    if "user" in session:
        reg = session.get("registry", {})
        session["registry"] = reg
        return reg, True

    # Anonymous registry
    reg = session.get("anon_registry", {})
    session["anon_registry"] = reg
    return reg, False


# ---------------------------
#  PUBLIC API
# ---------------------------

def is_logged_in():
    return "user" in session


def get_current_user():
    return session.get("user")


def get_registry_value(key):
    registry, _ = _get_registry_container()
    return registry.get(key)


def set_registry_value(key, value):
    registry, logged_in = _get_registry_container()
    registry[key] = value

    if logged_in:
        # Save to session
        session["registry"] = registry
        # Persist to GitHub metadata
        _sync_registry_to_github(registry)
    else:
        # Anonymous registry
        session["anon_registry"] = registry

    return True
