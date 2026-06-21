from flask import Blueprint, redirect, request, session, render_template
import requests
import os
from github_gist import load_registry, save_registry

login_bp = Blueprint("login_bp", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


@login_bp.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=read:user,gist"
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
    github_user = user_res.json()
    username = github_user.get("login")

    if not username:
        return "GitHub user fetch failed", 400

    # store user + token + full profile
    session["user"] = username
    session["github_token"] = access_token
    session["github_user"] = github_user

    # load or create registry Gist
    gist_id, registry = load_registry(access_token)
    session["gist_id"] = gist_id
    session["registry"] = registry

    return redirect("/")


@login_bp.route("/logout")
def logout():
    anon = session.get("anon_registry", {})
    session.clear()
    session["anon_registry"] = anon
    return redirect("/")


@login_bp.route("/profile")
def profile():
    github_user = session.get("github_user", {})
    return render_template("profile.html", github_user=github_user)
