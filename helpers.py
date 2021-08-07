import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Set specific extensions for form images
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def imagetobinary(filename):
    # Convert digital data to binary format
    with open(f"static/{filename}", 'rb') as file:
        blobData = file.read()
    return blobData


def binarytoimage(data, filename):
    # Convert binary data to proper format and write it on folder
    with open(filename, 'wb') as file:
        file.write(data)


def bdt(value):
    """Format value as BDT."""
    return f"৳{value:,.2f}"


def retrieveimage():
    if request.method == "POST":
        data = db.execute("SELECT image FROM donations WHERE user_id = ?", session['user_id'])
        data = data[0]['image']
        don_id = db.execute("SELECT don_id FROM donations WHERE user_id = ?", session['user_id'])
        don_id = don_id[0]['don_id']
        path = "static/" + str(don_id) + ".jpg"
        binarytoimage(data, path)
        return redirect("/")
    else:
        return render_template("cash.html")
