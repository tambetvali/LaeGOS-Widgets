from flask import Blueprint, render_template
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
import os

login_bp = Blueprint("login", __name__)

@login_bp.route("/login/")
def login_test():
    uri = os.environ.get("MONGO_URI")
    message = None

    if not uri:
        message = "ERROR: MONGO_URI is not set in environment."
        return render_template("login.html", message=message)

    try:
        client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        message = "SUCCESS: Connected to MongoDB Atlas!"
    except PyMongoError as e:
        message = f"ERROR: {str(e)}"

    return render_template("login.html", message=message)
