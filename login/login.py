from flask import Blueprint, redirect, request, session
import requests
import os
from github_app import (
    get_user_metadata,
    update_user_metadata
)

login_bp = Blueprint("login_bp", __name__)

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")


# ---------------------------
#  LOGIN START
# ---------------------------
@login_bp.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user"
    )


# ---------------------------
#  GITHUB CALLBACK
# ---------------------------
@login_bp.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for OAuth token
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        },
    )

    token_json = token_res.json()
    access_token = token_json.get("access_token")

    if not access_token:
        return "GitHub OAuth failed", 400

    # Get user info
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user = user_res.json()
    username = user.get("login")

    if not username:
        return "GitHub user fetch failed", 400

    # Store user and OAuth token in session
    session["user"] = username
    session["github_token"] = access_token

    # Load metadata using OAuth token directly
    metadata = get_user_metadata(access_token, username)

    # If metadata empty, fallback to anon registry
    if not metadata:
        metadata = session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"})

    # Save registry into session
    session["registry"] = metadata

    return redirect("/")


# ---------------------------
#  LOGOUT
# ---------------------------
@login_bp.route("/logout")
def logout():
    anon = session.get("anon_registry", {})
    session.clear()
    session["anon_registry"] = anon
    return redirect("/")


# ---------------------------
#  SAVE REGISTRY
# ---------------------------
@login_bp.route("/save_registry", methods=["POST"])
def save_registry():
    if "user" not in session:
        session["anon_registry"] = request.json
        return {"status": "saved-anon"}

    username = session["user"]
    oauth_token = session["github_token"]

    update_user_metadata(oauth_token, username, request.json)
    session["registry"] = request.json

    return {"status": "saved-github"}
