import os
import time
import jwt
import requests

GITHUB_API = "https://api.github.com"

GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")


# ---------------------------
#  JWT FOR GITHUB APP
# ---------------------------
def _get_app_jwt():
    """
    Create a JWT for the GitHub App using its private key.
    """
    if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
        raise RuntimeError("GITHUB_APP_ID or GITHUB_APP_PRIVATE_KEY not configured")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 9 * 60,
        "iss": GITHUB_APP_ID,
    }

    token = jwt.encode(
        payload,
        GITHUB_APP_PRIVATE_KEY,
        algorithm="RS256",
    )

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


# ---------------------------
#  INSTALLATION ID
# ---------------------------
def get_installation_id_for_user(username):
    """
    Using the GitHub App JWT, list installations and find the one
    that belongs to this user.
    """
    app_jwt = _get_app_jwt()

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.get(f"{GITHUB_API}/app/installations", headers=headers)
    if resp.status_code != 200:
        return None

    installations = resp.json() or []

    for inst in installations:
        account = inst.get("account", {})
        if account.get("login") == username:
            return inst.get("id")

    return None


# ---------------------------
#  INSTALLATION TOKEN
# ---------------------------
def get_installation_token_for_user(installation_id):
    """
    Given an installation ID, obtain an installation access token.
    """
    app_jwt = _get_app_jwt()

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }

    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    resp = requests.post(url, headers=headers, json={})

    if resp.status_code != 201:
        return None

    return resp.json().get("token")


# ---------------------------
#  READ METADATA
# ---------------------------
def get_user_metadata(installation_token, username):
    """
    Read GitHub user metadata for this user.
    """
    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.get(f"{GITHUB_API}/users/{username}/metadata", headers=headers)

    if resp.status_code != 200:
        return {}

    return resp.json().get("LaeGOS", {})


# ---------------------------
#  WRITE METADATA
# ---------------------------
def update_user_metadata(installation_token, username, registry):
    """
    Write registry dict into GitHub user metadata under the LaeGOS namespace.
    """
    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {"LaeGOS": registry}

    requests.patch(
        f"{GITHUB_API}/users/{username}/metadata",
        headers=headers,
        json=payload,
    )
