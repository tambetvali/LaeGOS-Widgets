from flask import Blueprint, redirect, request, session, url_for, jsonify
import requests
import os

login_bp = Blueprint("login", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


# -------------------------
# 1. LOGIN → GitHub
# -------------------------
@login_bp.route("/login")
def login():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        "&scope=read:user user:email"
        f"&redirect_uri={url_for('login.github_callback', _external=True)}"
    )
    return redirect(github_auth_url)


# -------------------------
# 2. CALLBACK → Exchange code for token
# -------------------------
@login_bp.route("/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Missing ?code= parameter", 400

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": url_for("login.github_callback", _external=True),
    }

    token_response = requests.post(token_url, headers=headers, data=data)
    token_json = token_response.json()

    if "error" in token_json:
        return jsonify(token_json), 400

    access_token = token_json.get("access_token")
    if not access_token:
        return "GitHub did not return an access token", 500

    session["github_token"] = access_token

    return redirect(url_for("login.profile"))


# -------------------------
# 3. PROFILE → Fetch user info
# -------------------------
@login_bp.route("/profile")
def profile():
    token = session.get("github_token")
    if not token:
        return redirect(url_for("login.login"))

    headers = {"Authorization": f"Bearer {token}"}

    user = requests.get("https://api.github.com/user", headers=headers).json()
    emails = requests.get("https://api.github.com/user/emails", headers=headers).json()

    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    return jsonify({
        "username": user.get("login"),
        "id": user.get("id"),
        "email": primary_email,
    })
