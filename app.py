from flask import Flask, render_template, session
from login.routes import login_bp
from login.mongo import get_user_by_id

app = Flask(
    __name__,
    template_folder="templates",
)

# Required for session cookies
app.secret_key = "CHANGE_THIS_TO_RANDOM_SECRET"

# Add drafts folder
app.jinja_loader.searchpath.append("drafts")

# Register login blueprint
app.register_blueprint(login_bp)


@app.context_processor
def inject_current_user():
    """Make current_user available in all templates."""
    user_id = session.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    return {"current_user": user}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    return render_template(filename)
