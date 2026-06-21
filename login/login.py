from flask import Blueprint, redirect, request, session
import requests
import os
from github_app import (
    get_installation_id,
    get_installation_token,
    load_registry,
    save_registry
)

login_bp = Blueprint("login_bp", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


@login_bp.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user"
    )


@login_bp.route("/callback")
def callback():
    code = request.args.get("code")

    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        },
    )

    access_token = token_res.json().get("access_token")
    if not access_token:
        return "GitHub OAuth failed", 400

    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    username = user_res.json().get("login")
    if not username:
        return "GitHub user fetch failed", 400

    session["user"] = username

    installation_id = get_installation_id(username)
    if not installation_id:
        return "Please authorize the LaeGOS GitHub App", 400

    installation_token = get_installation_token(installation_id)
    if not installation_token:
        return "Failed to get installation token", 400

    registry = load_registry(installation_token, username)
    if not registry:
        registry = session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"})

    session["registry"] = registry

    return redirect("/")


@login_bp.route("/logout")
def logout():
    anon = session.get("anon_registry", {})
    session.clear()
    session["anon_registry"] = anon
    return redirect("/")


@login_bp.route("/save_registry", methods=["POST"])
def save_registry_route():
    if "user" not in session:
        session["anon_registry"] = request.json
        return {"status": "saved-anon"}

    username = session["user"]
    installation_id = get_installation_id(username)
    installation_token = get_installation_token(installation_id)

    save_registry(installation_token, username, request.json)
    session["registry"] = request.json

    return {"status": "saved-github"}
