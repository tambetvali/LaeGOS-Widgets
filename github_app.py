import os
import time
import jwt
import requests

GITHUB_API = "https://api.github.com"
NAMESPACE = "LaeGOS"

APP_ID = os.environ["GITHUB_APP_ID"]
PRIVATE_KEY = os.environ["GITHUB_APP_PRIVATE_KEY"]


def _get_app_jwt():
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 9 * 60,
        "iss": APP_ID,
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return token.decode() if isinstance(token, bytes) else token


def get_installation_id(username):
    jwt_token = _get_app_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API}/app/installations", headers=headers)
    for inst in resp.json():
        if inst["account"]["login"] == username:
            return inst["id"]
    return None


def get_installation_token(installation_id):
    jwt_token = _get_app_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(
        f"{GITHUB_API}/app/installations/{installation_id}/access_tokens",
        headers=headers,
        json={}
    )
    return resp.json().get("token")


def load_registry(installation_token, username):
    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API}/users/{username}/metadata", headers=headers)
    return resp.json().get(NAMESPACE, {})


def save_registry(installation_token, username, registry):
    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {NAMESPACE: registry}
    requests.patch(
        f"{GITHUB_API}/users/{username}/metadata",
        headers=headers,
        json=payload
    )
