import os
import requests
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime

def apology(message, code=400):
    """Render message as an apology to user"""
    return render_template("apology.html", message=message), code


def escape(s):
    """
    Escape special characters.

    https://github.com/jacebrowning/memegen#special-characters
    """
    for old, new in [
        ("-", "--"),
        (" ", "-"),
        ("_", "__"),
        ("?", "~q"),
        ("%", "~p"),
        ("#", "~h"),
        ("/", "~s"),
        ('"', "''"),
    ]:
        s = s.replace(old, new)
    return s


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_bible_verse(reference):
    """Look up Bible verrse by reference (e.g., John 3:16)."""
    url = f"https://api.scripture.api.bible/v1/bibles/{API_KEY}/verses/{reference}"

    headers = {
        'api-key': API_KEY
    }
    try:
        # Make a GET request to the Scripture API with headers containing the API key
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP error responses

        # Parse the JSON response
        verse_data = response.json()
        return {
            "reference": verse_data.get("data", {}).get("reference" , "N/A"),
            "verse": verse_data.get("data", {}).get("text", "No verse found.")
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

