import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, allowed_file, imagetobinary, binarytoimage, bdt

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Designate upload folder for form images
UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["bdt"] = bdt

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///manage.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    """Record event expenses"""
    if request.method == "POST":
        if request.form.get(date) and request.form.get(event) and request.form.get(expense) and request.form.get(qty) and request.form.get(cost):
            date = request.form.get(date)
            event = request.form.get(event)
            expense = request.form.get(expenses)
            qty = int(request.form.get(qty))
            cost = float(request.form.get(cost))
            amount = qty * cost
            db.execute('INSERT INTO expenses ()')
        else:
            return redirect("/")
    else:
        return render_template("record.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("id"):
            return apology("No match")
        else:
            fid = str(request.form.get("id"))

            data = db.execute('SELECT "Member_ID" FROM members WHERE "Member_ID" = ?', fid)
            if len(data) != 0:
                mid = db.execute('SELECT * FROM members WHERE "Member_ID" = ?', fid)
                return render_template("memberinfo.html", mid=mid[0])
            else:
                return apology("No match")
    else:
        rows = db.execute('SELECT "Full_Name","School","Member_ID" FROM members')
        return render_template("members.html", rows=rows)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Check if any username was entered
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide username")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Check if username already exists
        if len(rows) != 0:
            return apology("Sorry, the username is already taken")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Sorry, your passswords didn't match")
        else:
            phash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=16)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), phash)
        # Redirect user to index
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        flash('Registered!')
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/donors", methods=["GET", "POST"])
@login_required
def donors():
    if request.method == "POST":
        # Declare variables for each form data entered
        name = request.form.get("name")
        reference = request.form.get("reference")
        amount = request.form.get("amount")
        date = request.form.get("date")
        user = session['user_id']
        # check if the post request has the file part
        if 'file' not in request.files:
            db.execute("INSERT INTO donations (user_id, name, reference, amount, date) VALUES (?, ?, ?, ?, ?)",
                    user, name, reference, amount, date)
            ocash = db.execute('SELECT cash FROM assets')
            db.execute('UPDATE assets SET cash = (?)', ncash)
            flash('Sucessfully recorded (without any file uploads)')
            return redirect("/donors")
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            db.execute("INSERT INTO donations (user_id, name, reference, amount, date) VALUES (?, ?, ?, ?, ?)",
                    user, name, reference, amount, date)
            ocash = db.execute('SELECT cash FROM assets')
            ncash = float(amount) + float(ocash[0]['cash'])
            db.execute('UPDATE assets SET cash = ?', ncash)
            flash('Sucessfully recorded. (without any file uploads)')
            return redirect("/donors")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("INSERT INTO donations (user_id, name, reference, amount, date, image) VALUES (?, ?, ?, ?, ?, ?)",
                    user, name, reference, amount, date, imagetobinary(filename))
        ocash = db.execute('SELECT cash FROM assets')
        ncash = float(amount) + float(ocash[0]['cash'])
        db.execute('UPDATE assets SET cash = ?', ncash)
        os.remove(f'static/{filename}')
        falsh('Successfully recorded')
        return redirect("/donors")
    else:
        rows = db.execute("SELECT * FROM donations")
        total = 0.0
        for i in range(len(rows)):
            total = total + int(rows[i]['amount'])
            rows[i]['amount'] = bdt(rows[i]['amount'])
        return render_template("donors.html", rows=rows, total=bdt(total))


@app.route("/past", methods=["GET", "POST"])
@login_required
def past():
    return render_template("cash.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
