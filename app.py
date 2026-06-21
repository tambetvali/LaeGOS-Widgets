from flask import Flask, jsonify
from login.login import login_bp
from login.driver import get_registry_value, set_registry_value, is_logged_in

app = Flask(__name__)
app.secret_key = "change-this"

app.register_blueprint(login_bp)


@app.route("/")
def index():
    # Your main UI here
    return "LaeGOS running"


@app.route("/api/registry")
def api_registry():
    if is_logged_in():
        return jsonify(session.get("registry", {}))
    return jsonify(session.get("anon_registry", {"SYSTEM.DAYNIGHTMODE": "Night"}))


@app.route("/api/set_daynight/<mode>")
def api_set_daynight(mode):
    set_registry_value("SYSTEM.DAYNIGHTMODE", mode)
    return {"status": "ok", "mode": mode}


if __name__ == "__main__":
    app.run(debug=True)
