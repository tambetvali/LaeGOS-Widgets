# login/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .mongo import (
    get_user_by_email,
    create_user,
    get_user_by_id,
    get_user_settings,
    set_user_setting,
    reset_user_data,
    get_user_storage_usage_bytes,
)

login_bp = Blueprint("login", __name__, url_prefix="/login")


def _current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


@login_bp.route("/", methods=["GET", "POST"])
def login_page():
    user = _current_user()

    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email", "").strip()

        # Logout / switch user
        if action == "logout":
            session.pop("user_id", None)
            flash("Logged out.")
            return redirect(url_for("login.login_page"))

        # Reset own database
        if action == "reset" and user:
            reset_user_data(str(user["_id"]))
            flash("Your LaeGOS data has been reset.")
            return redirect(url_for("login.login_page"))

        # Login or register
        if action in ("login", "register"):
            if not email:
                flash("Email is required.")
                return redirect(url_for("login.login_page"))

            existing = get_user_by_email(email)

            if action == "login":
                if not existing:
                    flash("User not found. You can register a new one.")
                    return redirect(url_for("login.login_page"))
                session["user_id"] = str(existing["_id"])
                flash("Logged in.")
                return redirect(url_for("login.login_page"))

            if action == "register":
                if existing:
                    # Existing user: treat as login after confirmation
                    session["user_id"] = str(existing["_id"])
                    flash("User already existed; logged in.")
                    return redirect(url_for("login.login_page"))
                new_user = create_user(email)
                session["user_id"] = str(new_user["_id"])
                flash("New user created and logged in.")
                return redirect(url_for("login.login_page"))

    # GET: show login UI
    user = _current_user()
    usage_info = None
    settings = None

    if user:
        usage_bytes = get_user_storage_usage_bytes(str(user["_id"]))
        usage_mb = usage_bytes / (1024 * 1024)
        # You can later compute percentage if you define a quota
        usage_info = {
            "bytes": usage_bytes,
            "mb": round(usage_mb, 2),
        }
        settings = get_user_settings(str(user["_id"]))

    return render_template(
        "login.html",
        user=user,
        usage=usage_info,
        settings=settings,
    )
