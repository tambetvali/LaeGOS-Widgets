from flask import Flask, render_template
from login.login import login_bp
from login.driver import get_current_user

import os, secrets

app = Flask(
    __name__,
    template_folder="templates",
)

# Dev settings
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["TRAP_HTTP_EXCEPTIONS"] = True
app.config["TRAP_BAD_REQUEST_ERRORS"] = True

app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Register login blueprint
app.register_blueprint(login_bp, url_prefix="/auth")

# Add drafts folder
app.jinja_loader.searchpath.append("drafts")

# Inject current_user into templates
@app.context_processor
def inject_user():
    return {"current_user": get_current_user()}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)
