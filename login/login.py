from flask import Blueprint, redirect, request, session, url_for, jsonify
import requests
import os

login_bp = Blueprint("login", __name__)

GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]


# ---------------------------------------------------------
# 1. LOGIN → Redirect user to GitHub OAuth
# ---------------------------------------------------------
@login_bp.route("/login")
def login():
    # Generate absolute callback URL
    callback_url = url_for("login.github_callback", _external=True)
    print("DEBUG: Using callback_url =", callback_url)

    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        "&scope=read:user user:email"
        f"&redirect_uri={callback_url}"
    )

    print("DEBUG: Redirecting to GitHub auth URL =", github_auth_url)
    return redirect(github_auth_url)


# ---------------------------------------------------------
# 2. CALLBACK → GitHub redirects here with ?code=
# ---------------------------------------------------------
@login_bp.route("/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Missing ?code= parameter", 400

    callback_url = url_for("login.github_callback", _external=True)
    print("DEBUG: Callback hit with code =", code)
    print("DEBUG: Using callback_url =", callback_url)

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": callback_url,
    }

    print("DEBUG: Sending token exchange request to GitHub…")
    token_response = requests.post(token_url, headers=headers, data=data)
    print("DEBUG: Raw token response =", token_response.text)

    # Safe JSON parsing
    try:
        token_json = token_response.json()
    except Exception as e:
        print("ERROR: Failed to parse JSON:", e)
        return "GitHub returned non‑JSON response", 500

    # GitHub error (e.g., bad_verification_code)
    if "error" in token_json:
        print("ERROR: GitHub OAuth error:", token_json)
        return jsonify(token_json), 400

    access_token = token_json.get("access_token")
    if not access_token:
        print("ERROR: No access_token in GitHub response")
        return "GitHub did not return an access token", 500

    print("DEBUG: Received access_token =", access_token[:6] + "…")
    session["github_token"] = access_token

    return redirect(url_for("login.profile"))


# ---------------------------------------------------------
# 3. PROFILE → Fetch GitHub user info
# ---------------------------------------------------------
@login_bp.route("/profile")
def profile():
    token = session.get("github_token")
    if not token:
        print("DEBUG: No token in session → redirecting to login")
        return redirect(url_for("login.login"))

    headers = {"Authorization": f"Bearer {token}"}

    print("DEBUG: Fetching GitHub user info…")
    user = requests.get("https://api.github.com/user", headers=headers).json()
    emails = requests.get("https://api.github.com/user/emails", headers=headers).json()

    primary_email = next((e["email"] for e in emails if e.get("primary")), None)

    print("DEBUG: User =", user)
    print("DEBUG: Emails =", emails)

    return jsonify({
        "username": user.get("login"),
        "id": user.get("id"),
        "email": primary_email,
    })
