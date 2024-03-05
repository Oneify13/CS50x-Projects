import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime
date = datetime.now()

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userId = session["user_id"]
    # Select all the information we need from our database to make the html table for our portfolio.
    cash = db.execute("SELECT cash FROM users WHERE id = ?", userId)[0]["cash"]
    username = db.execute("SELECT username FROM users WHERE id = ?", userId)
    stocks = db.execute("SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol", userId)
    for stock in stocks:
        symbol = lookup(stock["symbol"])
        stock["price"] = symbol["price"]
    value = 0
    # Finds the total value of all the stocks in a user's portfolio.
    for stock in stocks:
        value = value + (stock["price"] * stock["shares"])

    total = value + cash

    return render_template("index.html", database=stocks, cash=cash, username=username, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        # makes sure shares is an integer.
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares Must Be An Integer")

        stock = lookup(symbol.upper())

        if not symbol:
            return apology("Please Enter A Symbol")
        if stock is None:
            return apology("Stock Does Not Exist")
        if shares <= 0:
            return apology("Number Of Shares Must Be Positive")

        userId = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", userId)[0]['cash']
        price = stock["price"]
        total = price * shares
        new_balance = cash - total

        # Check to make sure we have enough cash for the purchase.
        if cash < total:
            return apology("Not Enough Money In Account")
        else:
            # Deduct the cost of the purchase from the user's account and add all the transaction information into the transactions table.
            db.execute("UPDATE users SET cash = ? WHERE id = ?;", new_balance, userId)
            db.execute("INSERT INTO transactions(user_id, symbol, price, type, shares, total_cost, time) VALUES(?, ?, ?, ?, ?, ?, ?)",
                       userId, symbol, price, 'Buy', shares, total, datetime.now())
            flash("Bought!")
            return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userId = session["user_id"]
    # Select all the information from transactions table for that user so we can display it in a table in html.
    transactions_db = db.execute("SELECT * FROM transactions WHERE user_id = ?", userId)
    return render_template("history.html", database=transactions_db)


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
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please Enter A Stock")
        stock = lookup(symbol.upper())
        if stock is None:
            return apology("Stock Does Not Exist")
        price = lookup(symbol)["price"]
        name = lookup(symbol)["name"]
        return render_template("quoted.html", price=price, name=name, symbol=symbol)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Makes sure inputs were given correctly.
        if not username:
            return apology("Please Enter A Username")
        if not password:
            return apology("Please Enter A Password")
        if not confirmation:
            return apology("Please Confirm Password")

        # Makes sure the username isn't already taken.
        username_db = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(username_db) == 1:
            return apology("Username Is Already Taken")
        # Checks to see if the user confirmed their password correctly.
        if password != confirmation:
            return apology("Passwords do not match")
        else:
            # Create the hash for the password and then insert the username and hash into our users table to be stored.
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        userId = session["user_id"]
        stocks = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares)", userId)
        return render_template("sell.html", stocks=stocks)
    else:
        symbol = request.form.get("symbol")
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares Must Be An Integer")

        userId = session["user_id"]
        stock = lookup(symbol.upper())
        total_shares = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ?", userId, symbol)[
            0]['shares']

        if not symbol:
            return apology("Please Enter A Symbol")

        if shares <= 0:
            return apology("Number Of Shares Must Be Positive")

        if shares > total_shares:
            return apology("You Are Trying To Sell More Stocks Than You Own")

        cash = db.execute("SELECT cash FROM users WHERE id = ?", userId)[0]['cash']
        price = stock["price"]
        total = price * shares

        # Add money to the account for the sale and insert all the transaction info into the transactions table.
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash + total, userId)
        db.execute("INSERT INTO transactions(user_id, symbol, price, type, shares, total_cost, time) VALUES(?, ?, ?, ?, ?, ?, ?)",
                   userId, symbol, price, 'Sell', 0 - shares, total, datetime.now())
        flash("Sold!")
        return redirect("/")


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method == "GET":
        return render_template("deposit.html")
    else:
        userId = session["user_id"]

        try:
            deposit = float(request.form.get("deposit"))
        except:
            return apology("Shares Must Be A Cash Amount")

        # Updates the user's balance
        balance = db.execute("SELECT cash FROM users WHERE id = ?", userId)[0]['cash']
        new_balance = deposit + balance

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, userId)
        return redirect("/")