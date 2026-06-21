from flask import Blueprint, redirect, request, session, url_for, jsonify, render_template
import requests
import os

login_bp = Blueprint("login", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


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
    session["github_token"] = access_token

    headers = {"Authorization": f"Bearer {access_token}"}

    user = requests.get("https://api.github.com/user", headers=headers).json()
    emails = requests.get("https://api.github.com/user/emails", headers=headers).json()
    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    session["user"] = {
        "email": primary_email,
        "name": user.get("name"),
        "picture": user.get("avatar_url"),
        "username": user.get("login"),
        "id": user.get("id"),
        "registry": {"SYSTEM.DAYNIGHTMODE": "Night"},
    }

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
    return redirect("/")


# -----------------------------
# DAY/NIGHT MODE TOGGLE
# -----------------------------
@login_bp.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    user = session.get("user")
    if not user:
        return "Not logged in", 403

    mode = user["registry"].get("SYSTEM.DAYNIGHTMODE", "Night")
    user["registry"]["SYSTEM.DAYNIGHTMODE"] = "Day" if mode == "Night" else "Night"
    session["user"] = user

    return "OK"
