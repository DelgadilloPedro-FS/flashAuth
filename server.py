from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from functools import wraps
import jsonify

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
app = Flask(__name__)
oauth = OAuth(app)
app.secret_key = env.get("APP_SECRET_KEY")
app.debug = True

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


app.config["SESSION-TYPE"] = "filesystem"


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.route("/home")
def home():
    print('hello home')
    return render_template("home.html")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*arg, **kwargs):
        print(session)
        if "profile" not in str(session):
            return redirect("/home")
        return f(*arg, **kwargs)

    return decorated


@app.route("/dashboard")
@requires_auth
def dashboard():
    return render_template(
        "dashboard.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
