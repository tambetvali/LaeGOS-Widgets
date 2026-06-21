from flask import Blueprint, redirect, request, session, url_for
import requests
import json
from github_app import (
    get_user_metadata,
    update_user_metadata
)
import os

login_bp = Blueprint("login_bp", __name__)

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")


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

    # Store user in session
    session["user"] = username

    # Get installation ID
    installation_id = get_installation_id_for_user(username)
    if not installation_id:
        return "GitHub App is not installed for this user", 400

    # Get installation token
    installation_token = get_installation_token_for_user(installation_id)
    if not installation_token:
        return "Failed to get installation token", 400

    # Load metadata
    metadata = get_user_metadata(installation_token, username)

    # If metadata empty, fallback to anon registry
    if not metadata:
        metadata = session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"})

    # Save registry into session
    session["registry"] = metadata

    return redirect("/")


# ---------------------------
#  LOGOUT (FIXED)
# ---------------------------
@login_bp.route("/logout")
def logout():
    # Preserve anonymous registry
    anon = session.get("anon_registry", {})

    # Clear everything
    session.clear()

    # Restore anonymous registry
    session["anon_registry"] = anon

    return redirect("/")


# ---------------------------
#  SAVE REGISTRY TO GITHUB
# ---------------------------
@login_bp.route("/save_registry", methods=["POST"])
def save_registry():
    if "user" not in session:
        # Save to anon registry
        session["anon_registry"] = request.json
        return {"status": "saved-anon"}

    username = session["user"]

    installation_id = get_installation_id_for_user(username)
    installation_token = get_installation_token_for_user(installation_id)

    update_user_metadata(installation_token, username, request.json)

    session["registry"] = request.json

    return {"status": "saved-github"}
