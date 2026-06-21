from flask import Flask, render_template, jsonify, session
from login.login import login_bp
from login.driver import (
    get_current_user,
    get_registry_value,
    set_registry_value,
    is_logged_in,
)

import os, secrets

# Create Flask app with templates folder
app = Flask(__name__, template_folder="templates")

# Secret key
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Dev settings
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["TRAP_HTTP_EXCEPTIONS"] = True
app.config["TRAP_BAD_REQUEST_ERRORS"] = True

# Register login blueprint WITH /auth prefix (your original choice)
app.register_blueprint(login_bp, url_prefix="/auth")

# Add drafts folder
app.jinja_loader.searchpath.append("drafts")


@app.context_processor
def inject_user():
    user = get_current_user()
    mode = get_registry_value("SYSTEM.DAYNIGHTMODE") or "Night"

    # Restore your full user object for profile page
    github_user = session.get("github_user", {})

    return {
        "current_user": user,
        "current_mode": mode,
        "github_user": github_user,   # <-- profile page fix
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/registry")
def api_registry():
    if is_logged_in():
        return jsonify(session.get("registry", {}))
    return jsonify(session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"}))


@app.route("/api/set_daynight/<mode>")
def api_set_daynight(mode):
    set_registry_value("SYSTEM.DAYNIGHTMODE", mode)
    return {"status": "ok", "mode": mode}


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)


if __name__ == "__main__":
    app.run(debug=True)
