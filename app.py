import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
# from datetime import datetime
from werkzeug.datastructures import MultiDict
from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


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
    return render_template("index.html")


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
        elif not request.form.get("pa   ssword"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/upload")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# I have to make this because in database we can'nt able to store the value like "2,700" we need to store like 2700 that wise we make this function
def clean_number(value):
    return float(value.replace(",", ""))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    import io
    import csv
    from datetime import datetime
    user_id = session["user_id"]
    if request.method == "POST":
        # import pdb; pdb.set_trace()
        stock_name = request.form.get("stock_name")
        file = request.files["csv_file"]
        stream = io.StringIO(file.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)


        # if not file:
        #     return apology("No file is uploaded", 400)

        for row in reader:
            date_format = row["Date"]

            if "/" in date_format:
                date = datetime.strptime(row["Date"], "%m/%d/%Y").date()
            elif "-" in date_format:
                date = datetime.strptime(row["Date"], "%d-%m-%Y").date()

            # inserting all the details of the stock csv file into database

            db.execute("INSERT INTO stock_data(user_id, stock_name, date, open, high, low, close) VALUES (?, ?, ?, ?, ?, ?, ?)", user_id, stock_name, date, clean_number(row["Open"]), clean_number(row["High"]), clean_number(row["Low"]), clean_number(row["Price"]))

        return redirect("/backtest")

    return render_template("upload.html")

@app.route("/backtest", methods=["GET", "POST"])
@login_required
def backtest():
    user_id = session["user_id"]
    equity_curve = []
    dates = []

    if request.method == "POST":
        stock_name = request.form.get("stock_name")
        if not stock_name:
            return apology("No stock name!", 400)

        strategy = request.form.get("strategy")

        target = float(request.form.get("target") or 0)
        stop_loss = float(request.form.get("stop_loss") or 0)

        data = db.execute("SELECT * FROM stock_data WHERE user_id = ? AND stock_name = ? ORDER BY date ASC", user_id, stock_name)

        if not data:
            return apology("No data here!", 400)

        if len(data) < 20:
            return apology("No enough data to work on EMA", 400)

        current_ema10 = None
        current_ema20 = None

        previous_ema10_value = None
        previous_ema20_value = None

        capital = 100000
        position = 0
        entry_price = 0
        target_price = 0
        stop_loss_price = 0
        profit = 0
        loss = 0

        total_trades = 0
        winning_trades = 0
        lossing_trades = 0

        ema_selection = request.form.get("ema")

        multiplier = 0
        multiplier2 = 0

        if ema_selection == "ema9_15":
            multiplier = 2 / (9 + 1)
            multiplier2 = 2 / (15 + 1)
            print("ema 9_15 selected")

        if ema_selection == "ema9_50":
            multiplier = 2 / (9 + 1)
            multiplier2 = 2 / (50 + 1)
            print("ema 9_50 selected")

        for row in data:

            close_price = row["close"]

            # EMA calculation
            if current_ema10 is None:
                current_ema10 = close_price
            else:
                current_ema10 = (close_price * multiplier) + (current_ema10 * (1 - multiplier))

            if current_ema20 is None:
                current_ema20 = close_price
            else:
                current_ema20 = (close_price * multiplier2) + (current_ema20 * (1 - multiplier2))

            # trade logic
            if previous_ema10_value is not None and previous_ema20_value is not None:

                if close_price >= target_price and position > 0:
                    sell_price = close_price
                    capital = capital + (sell_price * position)
                    profit = (sell_price - entry_price) * position
                    position = 0
                    total_trades = total_trades + 1
                    winning_trades = winning_trades + 1
                    print("SELL signal")
                    print(f"Profit is {profit}")

                elif stop_loss and close_price <= stop_loss_price and position > 0:
                    sell_price = close_price
                    capital = capital + (sell_price * position)
                    loss = (entry_price - sell_price) * position
                    position = 0
                    total_trades = total_trades + 1
                    lossing_trades = lossing_trades + 1
                    print("SELL signal")
                    print(f"loss is {loss}")

                if previous_ema20_value >= previous_ema10_value and current_ema10 > current_ema20:

                    if position == 0:
                        entry_price = close_price
                        quantity = capital // entry_price
                        capital = capital - (quantity * entry_price)
                        target_price = ((entry_price * target) / 100) + entry_price
                        stop_loss_price = entry_price - ((entry_price * stop_loss) / 100)
                        position = quantity
                        print("BUY signal")
                        print(f"entry price is {entry_price}")

            previous_ema10_value = current_ema10
            previous_ema20_value = current_ema20
            portfolio_value = capital + (position * close_price)

            if len(equity_curve) == 0 or portfolio_value != equity_curve[-1]:
                equity_curve.append(portfolio_value)
                dates.append(row["date"])

        if position > 0:
            sell_price = close_price
            capital = capital + (sell_price * position)
            if (sell_price - entry_price) * position > (entry_price - sell_price) * position:
                profit = (sell_price - entry_price) * position
                winning_trades = winning_trades + 1
            else:
                loss = (entry_price - sell_price) * position
                lossing_trades = lossing_trades + 1
            position = 0
            total_trades = total_trades + 1
            print("SELL signal")
            print(f"Profit/loss is {profit}")

        net_profit = capital - 100000
        return_percentage = (net_profit / 100000) * 100

        if total_trades > 0:
            win_rate = (winning_trades / total_trades) * 100
        else:
            win_rate = 0

        print(f"new capital is {capital:.2f}")
        print(f"total trades are {total_trades}")
        print(f"net profit is {net_profit:.2f}")
        print(f"return is {return_percentage:.2f}%")
        print(f"win rate is {win_rate:.2f}%")
        print(f"winning trades {winning_trades}")
        print(f"lossing trades {lossing_trades}")

        # updating the strategy_results database

        from datetime import datetime

        db.execute("INSERT INTO strategy_results(user_id, stock_name, strategy_name, net_profit, return_percentage, total_trades, win_rate, date_run) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_id, stock_name, strategy, net_profit, return_percentage, total_trades, win_rate, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return render_template("results.html", net_profit = net_profit, return_percentage = return_percentage, win_rate = win_rate, total_trades = total_trades, winning_trades = winning_trades, lossing_trades = lossing_trades, equity_curve = equity_curve, dates = dates)


    total_stocks = db.execute("SELECT DISTINCT stock_name FROM stock_data WHERE user_id = ? ORDER BY stock_name DESC", user_id)
    return render_template("backtest.html", total_stocks = total_stocks)


@app.route("/strategy_dashboard")
@login_required
def strategy_dashboard():
    user_id = session["user_id"]

    result = db.execute("SELECT * FROM strategy_results WHERE user_id = ? ORDER BY date_run DESC", user_id)

    avg_return = db.execute("SELECT AVG(return_percentage) as return_percentage FROM strategy_results WHERE user_id = ?", user_id)

    if avg_return[0]["return_percentage"] is not None:
        avg_return = round(avg_return[0]["return_percentage"], 2)
    else:
        avg_return = 0

    return render_template("strategy_dashboard.html", result = result, avg_return = avg_return)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirm"):
            return apology("must provide confirm password", 400)

        if request.form.get("password") != request.form.get("confirm"):
            return apology("password and  confirm password must be same", 400)

        user_name = request.form.get("username")

        password = generate_password_hash(request.form.get("password"))

        try:
            db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", user_name,password)
        except ValueError:
            return apology("Username is already taken", 400)

        return render_template("login.html")

    return render_template("register.html")

