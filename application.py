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
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if request.form.get("event")=='' or request.form.get("date")=='':
            return apology("Invalid Request!")
        event = request.form.get("event")
        rows = db.execute("SELECT event FROM events WHERE event = ?", event)
        print(rows)
        if len(rows) != 0:
            return apology ("Event already exists!")
        else:
            date = request.form.get("date")
            db.execute("INSERT INTO events (event, date) VALUES (?, ?)", event, date)
            flash("Event Successfully Created!")
            return redirect("/")
    else:
        name = db.execute('SELECT username FROM users WHERE id = ?', session['user_id'])
        return render_template("index.html", name=name[0]['username'])


@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    """Record event expenses"""
    if request.method == "POST":
        vent = db.execute("SELECT event FROM events")
        vents = []
        for i in range(len(vent)):
            vents.append(vent[i]['event'])
        if request.form['date'] and request.form['event'] and request.form['item'] and request.form['qty'] and request.form['cost'] and (request.form['event'] in vents) == True:
            date = request.form['date']
            event = request.form['event']
            item = request.form['item']
            qty = int(request.form['qty'])
            cost = float(request.form['cost'])
            amount = qty * cost
            event_id = db.execute('SELECT id FROM events WHERE event = ?', event)
            db.execute('INSERT INTO expenses (event_id, event, date, item, qty, cost, amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        event_id[0]['id'], event, date, item, qty, cost, amount)
            pid =  db.execute('INSERT INTO temp (event_id, event, date, item, qty, cost, amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        event_id[0]['id'], event, date, item, qty, cost, amount)
            total = amount
            ocash = db.execute('SELECT cash FROM assets')
            ncash = float(ocash[0]['cash']) - float(amount)
            db.execute('UPDATE assets SET cash = (?)', ncash)
            if pid == 1:
                expenses = {
                    "no": f"{pid}",
                    "item": f"{item}",
                    "qty": f"{qty}",
                    "cost": f"{bdt(cost)}",
                    "amount": f"{bdt(amount)}",
                    "total": f"{bdt(total)}",
                    "cash": f"{bdt(ncash)}"
                }
                total = 0.0
                data = db.execute("SELECT amount FROM expenses WHERE event_id = ?", event_id[0]['id'])
                for i in range(len(data)):
                    total = total + data[i]['amount']
                db.execute('UPDATE events SET total = (?) WHERE id = (?)', total, event_id[0]['id'])
            else:
                total = 0.0
                data = db.execute("SELECT amount FROM expenses WHERE event_id = ?", event_id[0]['id'])
                for i in range(len(data)):
                    total = total + data[i]['amount']
                expenses = {
                    "no": f"{pid}",
                    "item": f"{item}",
                    "qty": f"{qty}",
                    "cost": f"{bdt(cost)}",
                    "amount": f"{bdt(amount)}",
                    "total": f"{bdt(total)}",
                    "cash": f"{bdt(ncash)}"
                }
                db.execute('UPDATE events SET total = (?) WHERE id = (?)', total, event_id[0]['id'])

            return jsonify(expenses)
        else:
            flash('Invalid submission')
            return render_template('record.html')
    else:
        db.execute('DELETE FROM temp')
        vent = db.execute("SELECT event FROM events")
        cash = db.execute("SELECT cash FROM assets")
        return render_template("record.html", vent=vent, cash=bdt(float(cash[0]["cash"])))


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

            data = db.execute('SELECT member_id FROM members WHERE member_id = ?', fid)
            if len(data) != 0:
                mid = db.execute('SELECT * FROM members WHERE member_id = ?', fid)
                return render_template("memberinfo.html", mid=mid[0])
            else:
                return apology("No match")
    else:
        rows = db.execute('SELECT full_name, school, member_id FROM members')
        return render_template("members.html", rows=rows)


@app.route("/register", methods=["GET"])
def register():
    """Register user"""
    return render_template("inprogress.html")



@app.route("/donors", methods=["GET", "POST"])
@login_required
def donors():
    if request.method == "POST":
        # Declare variables for each form data entered
        name = request.form.get("name")
        event = request.form.get("event")
        reference = request.form.get("reference")
        amount = request.form.get("amount")
        date = request.form.get("date")
        user = session['user_id']
        eid = db.execute("SELECT id FROM events WHERE event = ?", event)
        eid = eid[0]["id"]
        # check if the post request has the file part
        if 'file' not in request.files:
            db.execute("INSERT INTO donations (event_id, user_id, name, reference, amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                    eid, user, name, reference, amount, date)
            ocash = db.execute('SELECT cash FROM assets')
            ncash = float(amount) + float(ocash[0]['cash'])
            db.execute('UPDATE assets SET cash = (?)', ncash)
            total = 0.0
            data = db.execute("SELECT amount FROM donations WHERE event_id = ?", eid)
            for i in range(len(data)):
                total = total + data[i]['amount']
            db.execute('UPDATE events SET donations = (?) WHERE id = (?)', total, eid)
            flash('Sucessfully recorded (without any file uploads)')
            return redirect("/donors")
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            db.execute("INSERT INTO donations (event_id, user_id, name, reference, amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                    eid, user, name, reference, amount, date)
            ocash = db.execute('SELECT cash FROM assets')
            ncash = float(amount) + float(ocash[0]['cash'])
            db.execute('UPDATE assets SET cash = ?', ncash)
            data = db.execute("SELECT amount FROM donations WHERE event_id = ?", eid)
            total = 0.0
            for i in range(len(data)):
                total = total + data[i]['amount']
            db.execute('UPDATE events SET donations = (?) WHERE id = (?)', total, eid)
            flash('Sucessfully recorded. (without any file uploads)')
            return redirect("/donors")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("INSERT INTO donations (event_id, user_id, name, reference, amount, date, image) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    eid, user, name, reference, amount, date, imagetobinary(filename))
        ocash = db.execute('SELECT cash FROM assets')
        ncash = float(amount) + float(ocash[0]['cash'])
        db.execute('UPDATE assets SET cash = ?', ncash)
        data = db.execute("SELECT amount FROM donations WHERE event_id = ?", eid)
        total = 0.0
        for i in range(len(data)):
            total = total + data[i]['amount']
        db.execute('UPDATE events SET donations = (?) WHERE id = (?)', total, eid)
        os.remove(f'static/{filename}')
        flash('Successfully recorded')
        return redirect("/donors")
    else:
        vent = db.execute("SELECT event FROM events")
        rows = db.execute("SELECT * FROM donations")
        cash = db.execute("SELECT cash FROM assets")
        total = 0.0
        for i in range(len(rows)):
            total = total + int(rows[i]['amount'])
            rows[i]['amount'] = bdt(rows[i]['amount'])
        return render_template("donors.html", vent=vent, rows=rows, total=bdt(total), cash=bdt(float(cash[0]["cash"])))


@app.route("/past", methods=["GET", "POST"])
@login_required
def past():
    if request.method == "POST":
        vent = db.execute("SELECT event FROM events")
        buff = []
        for i in range(len(vent)):
            buff.append(vent[i]['event'])
        if request.form.get('event') in buff:
            rows = db.execute('SELECT * FROM expenses WHERE event = ?', request.form.get("event"))
            event_id = db.execute('SELECT id FROM events WHERE event = ?', request.form.get("event"))
            event_id = event_id[0]['id']
            dows = db.execute('SELECT * FROM donations WHERE event_id = ?', event_id)
            if len(rows) == 0 and len(dows) == 0:
                return apology("No Data Available")

            if len(rows) != 0 and len(dows) == 0:
                for j in range(len(rows)):
                    rows[j]['id'] = j + 1
                total = 0.0
                for k in range(len(rows)):
                    total = total + float(rows[k]['amount'])
                return render_template('indepth.html', rows=rows, total=bdt(total), event=rows[0]['event'], date=rows[0]['date'])

            elif len(dows) != 0 and len(rows) == 0:
                for l in range(len(dows)):
                    dows[l]['don_id'] = l + 1
                donations = 0.0
                for m in range(len(dows)):
                    donations = donations + float(dows[m]['amount'])
                return render_template('indepth.html', dows=dows, donations=bdt(donations), event=request.form.get('event'), date=dows[0]['date'])

            else:
                for j in range(len(rows)):
                    rows[j]['id'] = j + 1
                total = 0.0
                for k in range(len(rows)):
                    total = total + float(rows[k]['amount'])

                for l in range(len(dows)):
                    dows[l]['don_id'] = l + 1
                donations = 0.0
                for m in range(len(dows)):
                    donations = donations + float(dows[m]['amount'])

                return render_template('indepth.html', dows=dows, donations=bdt(donations), rows=rows, total=bdt(total), event=rows[0]['event'], date=rows[0]['date'])
        else:
            return apology("Invalid Submission")
    else:
        vent = db.execute("SELECT event FROM events")
        events = db.execute("SELECT * FROM events")
        total = 0.0
        for i in range(len(events)):
            if events[i]['total'] == None:
                events[i]['total'] = 0.0
                total = total + float(events[i]['total'])
            else:
                total = total + float(events[i]['total'])
        total = bdt(total)
        donations = 0.0
        for j in range(len(events)):
            if events[j]['donations'] == None:
                events[j]['donations'] = 0.0
                donations = donations + float(events[j]['donations'])
            else:
                donations = donations + float(events[j]['donations'])
        donations = bdt(donations)
        return render_template("past.html", vent=vent, events=events, total=total, donations=donations)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
