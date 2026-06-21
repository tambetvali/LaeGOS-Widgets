from flask import session
import requests

GITHUB_API = "https://api.github.com"
METADATA_NAMESPACE = "LaeGOS"


def _get_token():
    return session.get("github_token")


def _get_registry_container():
    user = session.get("user")
    if user:
        user.setdefault("registry", {})
        return user["registry"], True
    reg = session.get("anon_registry", {})
    session["anon_registry"] = reg
    return reg, False


def _sync_registry_to_github(registry):
    token = _get_token()
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    payload = {METADATA_NAMESPACE: registry}
    try:
        requests.patch(f"{GITHUB_API}/user/metadata", headers=headers, json=payload)
    except Exception:
        pass


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
        user = session.get("user")
        user["registry"] = registry
        session["user"] = user
        _sync_registry_to_github(registry)
    else:
        session["anon_registry"] = registry
    return True
