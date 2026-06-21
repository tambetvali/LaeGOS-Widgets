from flask import session
import requests

GITHUB_API = "https://api.github.com"
METADATA_NAMESPACE = "LaeGOS"


def _get_token():
    return session.get("github_token")


def _sync_registry_to_github(registry):
    """
    Persist the registry dict into GitHub user metadata under our namespace.
    Silent on failure; session still holds the correct values.
    """
    token = _get_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    payload = {METADATA_NAMESPACE: registry}

    try:
        requests.patch(f"{GITHUB_API}/user/metadata", headers=headers, json=payload)
    except Exception:
        # We don't break UX if GitHub metadata write fails
        pass


def _get_registry_container():
    """
    Returns (registry_dict, logged_in_bool).

    - If user is logged in, use session["user"]["registry"].
    - If not, use session["anon_registry"] as per-computer defaults.
    """
    user = session.get("user")
    if user:
        user.setdefault("registry", {})
        return user["registry"], True

    # Anonymous registry (per-computer defaults)
    reg = session.get("anon_registry", {})
    session["anon_registry"] = reg
    return reg, False


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
        # Update session user registry
        user = session.get("user")
        user["registry"] = registry
        session["user"] = user

        # Persist to GitHub metadata
        _sync_registry_to_github(registry)
    else:
        # Anonymous per-computer registry
        session["anon_registry"] = registry

    return True
