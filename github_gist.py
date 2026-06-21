import requests
import json

GITHUB_API = "https://api.github.com"
GIST_FILENAME = "LaeGOS Registry.json"
GIST_DESCRIPTION = "LaeGOS registry storage"


def _auth_headers(oauth_token):
    return {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/vnd.github+json",
    }


def find_registry_gist(oauth_token):
    """
    Find the user's LaeGOS Registry Gist.
    Returns (gist_id, content_dict) or (None, None) if not found.
    """
    headers = _auth_headers(oauth_token)
    resp = requests.get(f"{GITHUB_API}/gists", headers=headers)

    if resp.status_code != 200:
        return None, None

    for gist in resp.json():
        files = gist.get("files", {})
        for fname, fmeta in files.items():
            if fname == GIST_FILENAME:
                raw_url = fmeta.get("raw_url")
                if not raw_url:
                    continue
                raw_resp = requests.get(raw_url, headers=headers)
                if raw_resp.status_code != 200:
                    return gist.get("id"), {}
                try:
                    data = raw_resp.json()
                except Exception:
                    data = {}
                return gist.get("id"), data

    return None, None


def create_registry_gist(oauth_token, initial_registry):
    """
    Create a new LaeGOS Registry Gist with initial_registry.
    Returns (gist_id, initial_registry).
    """
    headers = _auth_headers(oauth_token)
    payload = {
        "description": GIST_DESCRIPTION,
        "public": False,
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(initial_registry, indent=2, sort_keys=True)
            }
        },
    }
    resp = requests.post(f"{GITHUB_API}/gists", headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        return None, initial_registry

    gist_id = resp.json().get("id")
    return gist_id, initial_registry


def load_registry(oauth_token):
    """
    Load registry from user's Gist.
    If not found, create a new one with default registry.
    Returns (gist_id, registry_dict).
    """
    default_registry = {"SYSTEM.DAYNIGHTMODE": "Night"}

    gist_id, registry = find_registry_gist(oauth_token)
    if gist_id is None:
        gist_id, registry = create_registry_gist(oauth_token, default_registry)

    if registry is None:
        registry = default_registry

    return gist_id, registry


def save_registry(oauth_token, gist_id, registry):
    """
    Save registry to existing Gist.
    """
    headers = _auth_headers(oauth_token)
    payload = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(registry, indent=2, sort_keys=True)
            }
        }
    }
    requests.patch(f"{GITHUB_API}/gists/{gist_id}", headers=headers, json=payload)
