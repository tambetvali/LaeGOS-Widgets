from flask import Blueprint, redirect, request, session, url_for, jsonify, render_template
import requests
import os

from github_app import get_installation_token_for_user

login_bp = Blueprint("login", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]

METADATA_NAMESPACE = "LaeGOS"
GITHUB_API = "https://api.github.com"


def _get_oauth_token():
    return session.get("github_token")


def _get_app_installation_token():
    oauth_token = _get_oauth_token()
    if not oauth_token:
        return None
    return get_installation_token_for_user(oauth_token)


def _load_registry_from_github():
    """
    Load registry dict from GitHub user metadata under our namespace,
    using the GitHub App installation token.
    """
    app_token = _get_app_installation_token()
    if not app_token:
        return {}

    headers = {
        "Authorization": f"Bearer {app_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API}/user/metadata", headers=headers)
    if resp.status_code != 200:
        return {}

    data = resp.json() or {}
    return data.get(METADATA_NAMESPACE, {}) or {}


# -----------------------------
# LOGIN
# -----------------------------
@login_bp.route("/login")
def login():
    callback_url = url_for("login.github_callback", _external=True)
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        "&scope=read:user user:email"
        f"&redirect_uri={callback_url}"
    )
    return redirect(github_auth_url)


# -----------------------------
# CALLBACK
# -----------------------------
@login_bp.route("/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Missing ?code=", 400

    callback_url = url_for("login.github_callback", _external=True)

    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": callback_url,
        },
    )

    token_json = token_resp.json()
    if "error" in token_json:
        return jsonify(token_json), 400

    access_token = token_json.get("access_token")
    if not access_token:
        return "No access token", 500

    # Store OAuth token (for user identity + to derive installation token)
    session["github_token"] = access_token
    headers = {"Authorization": f"Bearer {access_token}",
               "Accept": "application/vnd.github+json"}

    # Basic user info
    user = requests.get(f"{GITHUB_API}/user", headers=headers).json()
    emails = requests.get(f"{GITHUB_API}/user/emails", headers=headers).json()
    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    session["user"] = {
        "email": primary_email,
        "name": user.get("name"),
        "picture": user.get("avatar_url"),
        "username": user.get("login"),
        "id": user.get("id"),
        "registry": {},
    }

    # Load registry from GitHub metadata via App
    registry = _load_registry_from_github()

    # If metadata is truly empty, fall back to per-computer defaults (if any)
    if registry == {}:
        registry = session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"})

    session["user"]["registry"] = registry

    return redirect(url_for("login.profile"))


# -----------------------------
# PROFILE PAGE
# -----------------------------
@login_bp.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login"))

    mode = user.get("registry", {}).get("SYSTEM.DAYNIGHTMODE", "Night")
    return render_template("profile.html", user=user, current_mode=mode)


# -----------------------------
# LOGOUT
# -----------------------------
@login_bp.route("/logout")
def logout():
    # Keep anon_registry so per-computer defaults are restored
    session.pop("github_token", None)
    session.pop("user", None)
    return redirect("/")


# -----------------------------
# DAY/NIGHT MODE TOGGLE
# -----------------------------
@login_bp.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    user = session.get("user")
    if user and "registry" in user:
        mode = user["registry"].get("SYSTEM.DAYNIGHTMODE", "Night")
        new_mode = "Day" if mode == "Night" else "Night"
        user["registry"]["SYSTEM.DAYNIGHTMODE"] = new_mode
        session["user"] = user

        # Persist via App metadata
        app_token = _get_app_installation_token()
        if app_token:
            headers = {
                "Authorization": f"Bearer {app_token}",
                "Accept": "application/vnd.github+json",
            }
            payload = {METADATA_NAMESPACE: user["registry"]}
            try:
                requests.patch(f"{GITHUB_API}/user/metadata", headers=headers, json=payload)
            except Exception:
                pass
    else:
        reg = session.get("anon_registry", {})
        mode = reg.get("SYSTEM.DAYNIGHTMODE", "Night")
        reg["SYSTEM.DAYNIGHTMODE"] = "Day" if mode == "Night" else "Night"
        session["anon_registry"] = reg

    return "OK"
