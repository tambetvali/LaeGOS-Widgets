from flask import Blueprint, redirect, request, session, render_template
import requests
import os
from github_gist import load_registry

login_bp = Blueprint("login_bp", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


@login_bp.route("/login")
def login():
    return redirect(
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=read:user,user:email,gist"
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

    # Fetch GitHub user profile
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    github_user = user_res.json()

    # Fetch email if missing
    if not github_user.get("email"):
        email_res = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        emails = email_res.json()
        primary = next((e["email"] for e in emails if e.get("primary")), None)
        github_user["email"] = primary

    # Store raw GitHub JSON
    session["github_user"] = github_user
    session["user"] = github_user.get("login")
    session["github_token"] = access_token

    # Load or create registry Gist
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


@login_bp.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    # Get current registry
    reg = session.get("registry") or session.get("anon_registry") or {}

    current = reg.get("SYSTEM.DAYNIGHTMODE", "Night")
    new_mode = "Day" if current == "Night" else "Night"

    # Update registry
    reg["SYSTEM.DAYNIGHTMODE"] = new_mode

    # Save to session
    if "user" in session:
        session["registry"] = reg
        # Save to Gist
        from github_gist import save_registry
        save_registry(session["github_token"], session["gist_id"], reg)
    else:
        session["anon_registry"] = reg

    return {"status": "ok", "mode": new_mode}


@login_bp.route("/profile")
def profile():
    github_user = session.get("github_user")

    if github_user:
        user = {
            "username": github_user.get("login"),
            "email": github_user.get("email"),
            "name": github_user.get("name"),
            "picture": github_user.get("avatar_url"),
        }
    else:
        user = None

    return render_template("profile.html", user=user)
