from flask import Flask, render_template, jsonify, session
from login.login import login_bp
from login.driver import (
    get_current_user,
    get_registry_value,
    set_registry_value,
    is_logged_in,
)

import os, secrets

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Dev settings
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["TRAP_HTTP_EXCEPTIONS"] = True
app.config["TRAP_BAD_REQUEST_ERRORS"] = True

# /auth prefix
app.register_blueprint(login_bp, url_prefix="/auth")

# drafts folder
app.jinja_loader.searchpath.append("drafts")


@app.context_processor
def inject_user():
    github_user = session.get("github_user")
    mode = get_registry_value("SYSTEM.DAYNIGHTMODE")

    if github_user:
        user = {
            "username": github_user.get("login"),
            "email": github_user.get("email"),
            "name": github_user.get("name"),
            "picture": github_user.get("avatar_url"),
        }
    else:
        user = None

    return {
        "user": user,
        "current_user": user,
        "github_user": github_user,
        "current_mode": mode,
    }


@app.route("/")
def home():
    print("ANON REGISTRY:", session.get("anon_registry"))
    return render_template("index.html")


@app.route("/api/registry")
def api_registry():
    if is_logged_in():
        return jsonify(session.get("registry", {}))
    return jsonify(session.get("anon_registry", {}))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/os/")
def os_root():
    return render_template("laegos/laegos.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)


if __name__ == "__main__":
    app.run(debug=True)
