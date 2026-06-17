from flask import Blueprint, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth

from login_config import (
    SESSION_SECRET_KEY,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)

from mongo import (
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
# /login
# ----------------------------
@login_bp.route("/login")
def login():
    redirect_uri = url_for("login.callback", _external=True)
    return google.authorize_redirect(redirect_uri)


# ----------------------------
# /login/callback
# ----------------------------
@login_bp.route("/login/callback")
def callback():
    token = google.authorize_access_token()
    userinfo = google.parse_id_token(token)

    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    user = get_user_by_email(email)

    if not user:
        create_user(email, name, picture)
    else:
        update_last_login(email)

    session_id = create_session(email)
    session["session_id"] = session_id

    return redirect("/")
