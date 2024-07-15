# Import necessary libraries
from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

import json
from os import environ as env  # Access environment variables
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv  # Load environment variables from .env file
from functools import wraps
import jsonify

# Define path to the .env file (optional)
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)  # Load environment variables if .env file exists

# Create Flask application instance
app = Flask(__name__)

# Configure OAuth client
oauth = OAuth(app)
app.secret_key = env.get("APP_SECRET_KEY")  # Set secret key for session management
app.debug = True  # Enable debug mode for development (disable in production)

# Configure Auth0 provider
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",  # Request user profile and email information
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Configure session type
app.config["SESSION-TYPE"] = "filesystem"  # Use filesystem for session storage


# Custom exception class for Auth errors
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Home route
@app.route("/")
def home():
    print('hello home')
    return render_template("home.html")  # Render the home page template


# Login route initiates Auth0 authorization flow
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)  # Redirect after authorization
    )


# Callback route handles authorization response from Auth0
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()  # Exchange authorization code for tokens
    session["user"] = token  # Store token in session (improve security later)
    return redirect("/dashboard")  # Redirect to dashboard


# Logout route clears session and redirects to Auth0 logout endpoint
@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),  # Redirect back to home after logout
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# Decorator to protect routes requiring authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*arg, **kwargs):
        print(session)  # Print session data for debugging (remove in production)
        if "profile" not in str(session):  # Check if user profile is in session
            return redirect("/")  # Redirect to home if not authenticated
        return f(*arg, **kwargs)

    return decorated


# Dashboard route, requires authentication
@app.route("/dashboard")
@requires_auth
def dashboard():
    return render_template(
        "dashboard.html",
        session=session.get("user"),  # Pass user data to template (improve security later)
        pretty=json.dumps(session.get("user"), indent=4),  # Pretty-printed user data for display
    )

@app.route("/settings")
@requires_auth
def settings():
    # Get the user information from the session
    user_info = session.get('user', {})
    nickname = user_info.get('userinfo', {}).get('nickname')  # Access nickname from nested dictionary

    # Render the template and pass the nickname
    return render_template(
        "settings.html",
        nickname=nickname,
        user_info=user_info 
    )

# Run the application (host set to 0.0.0.0 for external access)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
