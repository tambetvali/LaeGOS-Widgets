import os
import requests

GITHUB_API = "https://api.github.com"
METADATA_NAMESPACE = "LaeGOS"


# ---------------------------
#  READ METADATA (OAuth only)
# ---------------------------
def get_user_metadata(oauth_token, username):
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.get(f"{GITHUB_API}/users/{username}/metadata", headers=headers)

    if resp.status_code != 200:
        return {}

    return resp.json().get(METADATA_NAMESPACE, {})


# ---------------------------
#  WRITE METADATA (OAuth only)
# ---------------------------
def update_user_metadata(oauth_token, username, registry):
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/vnd.github+json",
    }

    payload = {METADATA_NAMESPACE: registry}

    requests.patch(
        f"{GITHUB_API}/users/{username}/metadata",
        headers=headers,
        json=payload,
    )
