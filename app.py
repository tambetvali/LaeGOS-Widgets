from flask import Flask, render_template
from login.login import login_bp

app = Flask(
    __name__,
    template_folder="templates",      # your normal templates
)

# Add an additional folder for drafts
app.jinja_loader.searchpath.append("drafts")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/drafts/<path:filename>")
def drafts(filename):
    # This will look for the file inside the "drafts" folder
    return render_template(filename)
