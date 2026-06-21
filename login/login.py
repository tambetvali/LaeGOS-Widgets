from flask import Blueprint, redirect, request, session, url_for, jsonify, render_template
import requests
import os

login_bp = Blueprint("login", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]

METADATA_NAMESPACE = "LaeGOS"
GITHUB_API = "https://api.github.com"


def _get_token():
    return session.get("github_token")


def _load_registry_from_github():
    token = _get_token()
    if not token:
        return {}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
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

    session["github_token"] = access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    user = requests.get(f"{GITHUB_API}/user", headers=headers).json()
    emails = requests.get(f"{GITHUB_API}/user/emails", headers=headers).json()
    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    # Base user info
    session["user"] = {
        "email": primary_email,
        "name": user.get("name"),
        "picture": user.get("avatar_url"),
        "username": user.get("login"),
        "id": user.get("id"),
        "registry": {},
    }

    # Load registry from GitHub metadata
    registry = _load_registry_from_github()
    if not registry:
        registry = {"SYSTEM.DAYNIGHTMODE": "Night"}
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
    return render_template("profile.html", user=user)


# -----------------------------
# LOGOUT
# -----------------------------
@login_bp.route("/logout")
def logout():
    session.pop("github_token", None)
    session.pop("user", None)
    session.pop("anon_registry", None)
    return redirect("/")


# -----------------------------
# DAY/NIGHT MODE TOGGLE
# -----------------------------
@login_bp.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    user = session.get("user")
    if user and "registry" in user:
        mode = user["registry"].get("SYSTEM.DAYNIGHTMODE", "Night")
        user["registry"]["SYSTEM.DAYNIGHTMODE"] = "Day" if mode == "Night" else "Night"
        session["user"] = user
    else:
        # Anonymous registry in session
        reg = session.get("anon_registry", {})
        mode = reg.get("SYSTEM.DAYNIGHTMODE", "Night")
        reg["SYSTEM.DAYNIGHTMODE"] = "Day" if mode == "Night" else "Night"
        session["anon_registry"] = reg

    return "OK"
