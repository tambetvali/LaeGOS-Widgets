from flask import Flask, render_template
from login.login import login_bp

app = Flask(
    __name__,
    template_folder="templates",
)

# This is rather dev than prod system.
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["TRAP_HTTP_EXCEPTIONS"] = True
app.config["TRAP_BAD_REQUEST_ERRORS"] = True

# Register the login blueprint
app.register_blueprint(login_bp, url_prefix="/auth")

# Add an additional folder for drafts
app.jinja_loader.searchpath.append("drafts")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)
