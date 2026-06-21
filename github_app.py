import os
import time
import jwt
import requests

GITHUB_API = "https://api.github.com"

GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")


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
    # PyJWT >= 2 returns str, older returns bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def _get_installation_id_for_user(oauth_token):
    """
    Using the user's OAuth token, find the installation of this App
    for that user.
    """
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API}/user/installations", headers=headers)
    if resp.status_code != 200:
        return None

    data = resp.json() or {}
    installations = data.get("installations", [])
    if not installations:
        return None

    # If multiple, pick the first; usually there is one per user/org context
    return installations[0].get("id")


def get_installation_token_for_user(oauth_token):
    """
    Given a user's OAuth token, obtain an installation access token
    for this GitHub App, scoped to that user.
    """
    installation_id = _get_installation_id_for_user(oauth_token)
    if not installation_id:
        return None

    app_jwt = _get_app_jwt()
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }
    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    resp = requests.post(url, headers=headers, json={})
    if resp.status_code != 201:
        return None

    data = resp.json() or {}
    return data.get("token")
