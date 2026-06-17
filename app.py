from flask import Flask, render_template, session
from login.routes import login_bp

app = Flask(
    __name__,
    template_folder="templates",
)

# Required for session cookies
app.secret_key = "sdf98sdf98sdf98sdf98sdf98sdf98"

# Add drafts folder
app.jinja_loader.searchpath.append("drafts")

# Register login blueprint
app.register_blueprint(login_bp)


@app.context_processor
def inject_current_user():
    """
    Make current_user available in all templates.
    This is the MongoDB OAuth profile stored in session["user"].
    """
    return {"current_user": session.get("user")}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)
