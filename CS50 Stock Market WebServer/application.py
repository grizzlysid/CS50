import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, text

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    recs = db.execute("select  symbol, stock , sum(qty) as shares , price, sum(totals) as total from  portfolio where userid is ? group by symbol", session["user_id"])
    rows = db.execute("SELECT * FROM users WHERE id is ?", session["user_id"])

    if not rows:
        cash =0
        rem = 0
    else:
        cash = rows[0]["cash"]
        ftotal = 0
        for rec in recs:
            rec["price"] = lookup(rec["symbol"])["price"]
            rec["total"] = rec["shares"] * rec["price"]
            ftotal = ftotal + rec["total"]

        rem = cash + ftotal
    return render_template("index.html", recs = recs, cash=cash, rem=rem)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        try:
            tmp = int(request.form.get("shares"))
        except:
            return apology("Enter valid number", 400)
        if tmp != float(request.form.get("shares")):
            return apology("Enter valid number", 400)
        if tmp < 0:
            return apology("Enter valid number", 400)
        shares = float(request.form.get("shares"))
        rows = db.execute("SELECT * FROM users WHERE id is ?", session["user_id"])
        info = lookup(symbol)
        if not info or not shares:
            return apology("Invalid Ticker", 400)
        else:
            price = float(info["price"])
            if(float(rows[0]["cash"])<price*shares):
                return apology("Not enough cash")
            else:
                newcash = rows[0]["cash"] - price * shares
                db.execute("UPDATE users SET cash = ? WHERE id is ?",newcash, session["user_id"])
                db.execute("insert into portfolio (userid,stock,symbol,qty,price) values(?,?,?,?,?)",session["user_id"], info["name"], info["symbol"], shares, info["price"])
                return redirect("/")
    else:
        return render_template("buy.html")




@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    historys = db.execute("SELECT * FROM portfolio where userid is ?", session["user_id"])


    return render_template("history.html", historys = historys)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method =="POST":
        symbol = request.form.get("symbol")
        info = lookup(symbol)
        if not info:
            return apology("Invalid Ticker", 400)
        else:
            return text("A share of " + info["name"] + "(" + info["symbol"] + ") costs " + usd(info["price"]))
    else:
        return render_template("quote.html")

@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():

    if request.method =="POST":
        amount = request.form.get("amount")
        rows = db.execute("SELECT * FROM users WHERE id is ?", session["user_id"])
        acash = rows[0]["cash"] + float(amount)
        db.execute("UPDATE users SET cash = ? WHERE id is ?",acash, session["user_id"])


        return text("Cash of amount: " + str(amount) + " added to the account")
    else:
        return render_template("cash.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        find = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not find:
            if (password != confirm):
                return apology("Passwords Don't Match", 400)
            else:
                phash = generate_password_hash(password)
                db.execute("INSERT INTO users (username,hash) VALUES(?,?)", username, phash)
                rows = db.execute("SELECT * FROM users WHERE username = ?", username)

                session["user_id"] = rows[0]["id"]
                flash("You were successfully registered!")
                return redirect("/")
        elif username in find[0]["username"]:
            return apology("Username taken", 400)
        else:

            if (password != confirm):
                return apology("Passwords Don't Match", 400)
            else:
                phash = generate_password_hash(password)
                db.execute("INSERT INTO users (username,hash) VALUES(?,?)", username, phash)
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

                session["user_id"] = rows[0]["id"]
                flash("You were successfully registered!")
                return redirect("/")

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        try:
            tmp = int(request.form.get("shares"))
        except:
            return apology("Enter valid number", 400)
        if tmp != float(request.form.get("shares")):
            return apology("Enter valid number", 400)
        if tmp < 0:
            return apology("Enter valid number", 400)
        shares = float(request.form.get("shares"))

        rows = db.execute("SELECT * FROM users WHERE id is ?", session["user_id"])
        port = db.execute("select * from portfolio where userid is ? and symbol =? ", session["user_id"], symbol)
        print("")
        print(port)
        print("")

        if port[0]["qty"] < shares:
            return apology("Not enough shares", 400)
        else:
            info = lookup(symbol)
            price = float(info["price"])
            newcash = rows[0]["cash"] + price * shares
            nshares = port[0]["qty"] - shares
            if nshares == 0:
                db.execute("DELETE FROM portfolio WHERE symbol = ? and userid is ?", symbol, session["user_id"])
            else:
                db.execute("UPDATE portfolio SET qty = ? WHERE userid is ? and symbol=? ",nshares, session["user_id"], symbol)


            db.execute("UPDATE users SET cash = ? WHERE id is ?",newcash, session["user_id"])
            return redirect("/")
    else:
        ticks = db.execute("Select DISTINCT symbol from portfolio where userid is ?", session["user_id"])
        return render_template("sell.html", ticks = ticks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
