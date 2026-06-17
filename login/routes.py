# login/routes.py
from flask import Blueprint, redirect, request, session, url_for, render_template
import requests
import os

login_bp = Blueprint("login", __name__, url_prefix="/login")

# Environment variables (set these in PythonAnywhere)
APP_ID = os.environ.get("MONGO_APP_ID")
OAUTH_PROVIDER = "oauth2-google"   # or oauth2-github, oauth2-apple, etc.
REDIRECT_URI = os.environ.get("MONGO_REDIRECT_URI")  # e.g. https://laegna.pythonanywhere.com/login/callback

# MongoDB OAuth endpoints
BASE_URL = f"https://services.cloud.mongodb.com/api/client/v2.0/app/{APP_ID}"
LOGIN_URL = f"{BASE_URL}/auth/providers/{OAUTH_PROVIDER}/login"
PROFILE_URL = f"{BASE_URL}/auth/profile"


@login_bp.route("/")
def login_redirect():
    """
    This page does not show UI.
    It immediately redirects the user to MongoDB OAuth login.
    """
    return redirect(f"{LOGIN_URL}?redirect={REDIRECT_URI}")


@login_bp.route("/callback")
def login_callback():
    """
    MongoDB redirects back here with ?access_token=...
    We store the token and fetch the user profile.
    """
    access_token = request.args.get("access_token")

    if not access_token:
        return "Login failed: no access token returned.", 400

    # Store token in session
    session["access_token"] = access_token

    # Fetch user profile from MongoDB
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(PROFILE_URL, headers=headers).json()

    # Store minimal user info in session
    session["user"] = {
        "email": profile.get("email"),
        "name": profile.get("name"),
        "picture": profile.get("picture"),
        "id": profile.get("user_id"),
    }

    return redirect(url_for("home"))
