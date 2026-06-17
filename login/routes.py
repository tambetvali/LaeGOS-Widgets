from flask import Blueprint, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth

from login.login_config import (
    SESSION_SECRET_KEY,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)

from login.mongo import (
    get_user_by_email,
    create_user,
    update_last_login,
    create_session,
)

login_bp = Blueprint("login", __name__)
oauth = OAuth()

# Register Google OAuth
google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    client_kwargs={"scope": "openid email profile"},
)


@login_bp.record_once
def init_oauth(setup_state):
    app = setup_state.app
    app.secret_key = SESSION_SECRET_KEY
    oauth.init_app(app)


# ----------------------------
# /login/ (POST from your form)
# ----------------------------
@login_bp.route("/login/", methods=["POST"])
def login_page():
    email = request.form.get("email")
    name = request.form.get("name", "")
    picture = request.form.get("picture", "")

    existing = get_user_by_email(email)

    if not existing:
        create_user(email, name, picture)
    else:
        update_last_login(email)

    session_id = create_session(email)
    session["session_id"] = session_id

    return redirect("/")
