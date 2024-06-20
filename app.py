from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
import json
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import date
import pandas as pd
import os
import download_data
from threading import Thread
from scrape import get_data, init_session


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join("static")
app.config["SQLALCHEMY_DATABASE_URI"] = rf"sqlite:///{os.getcwd()}/database.db"
app.config["SECRET_KEY"] = "ehbrfgiIYB76%$#^$rv5RRUGEVIH2VDYGIedvUYUYV"
db = SQLAlchemy(app)
Bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date_created = db.Column(db.DateTime, default=date.today)
    price_when_added = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    stocks = db.relationship("Stock", backref="user", lazy=True)
    earnings = db.Column(db.Float, nullable=False, default=0)

    def get_all_stocks(self):
        return Stock.query.filter_by(user_id=self.id).all()

    def add_stock(self, symbol, price, quantity=1):
        new_stock = Stock(
            symbol=symbol,
            user_id=self.id,
            price_when_added=price,
            date_created=date.today(),
            quantity=quantity,
        )
        db.session.add(new_stock)
        db.session.commit()


class SignUpForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    email = StringField(
        validators=[InputRequired()], render_kw={"placeholder": "Email"}
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Password"},
    )

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Password"},
    )

    submit = SubmitField("Login")


@app.route("/about")
def about():
    user = current_user
    islogin, username = user.is_authenticated, user.username if user.is_authenticated else ""
    full_filename = os.path.join(app.config["UPLOAD_FOLDER"], "photo.png")
    return render_template(
        "about.html", img_path=full_filename, islogin=islogin, username=username
    )


@app.route("/")
def homepage():
    user = current_user
    islogin, username = user.is_authenticated, user.username if user.is_authenticated else ""
    full_filename = os.path.join(app.config["UPLOAD_FOLDER"], "design.png")
    return render_template(
        "homepage.html", img_path=full_filename, islogin=islogin, username=username
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if Bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for("homepage"))
                else:
                    flash("Invalid password. Please try again.", "danger")
            else:
                flash("Username not found. Please try again.", "danger")
        else:
            flash("Invalid form data. Please check your inputs and try again.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    if request.method == "POST":
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different username.", "danger")
        else:
            hashed_password = Bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("homepage"))

    return render_template("signup.html", form=form)


with app.app_context():
    db.create_all()


nse_session = init_session()
df = pd.read_csv("ind_nifty50list.csv")
ALL_SYMBOLS = df["Symbol"].values.tolist()
live_data = pd.read_csv("stock_data.csv")
live_data_dict = live_data.to_dict(orient="records")
filterable_columns = [
    cols
    for cols in live_data_dict[0].keys()
    if (isinstance(live_data_dict[0][cols], float) or 
        isinstance(live_data_dict[0][cols], int))
]
sym_price_dict = dict(zip(live_data["Symbol"], live_data["Current Price"]))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = current_user
    islogin, username = user.is_authenticated, user.username if user.is_authenticated else ""
    selected_symbols = []
    plot_data = {}
    plot_type = "normal"
    time_interval = "week"
    if request.method == "POST":
        selected_symbols = request.form.getlist("symbols")
        time_interval = request.form["time_interval"]
        plot_type = request.form["plot_type"]
        inv_to_days = {"week": 7, "month": 30, "quarter": 90, "halfyear": 180, "year": 365}
        for sym in selected_symbols:
            plot_data[sym] = get_data(nse_session, sym, inv_to_days[time_interval])
    plot_data = json.dumps(plot_data)
    return render_template(
        "dashboard.html",
        plot_type=plot_type,
        time_interval=time_interval,
        plot_data=plot_data,
        symbols=selected_symbols,
        all_symbols=ALL_SYMBOLS,
        islogin=islogin,
        username=username,
    )


@app.route("/livemarket", methods=["GET"])
def livemarket():
    user = current_user
    islogin, username = user.is_authenticated, user.username if user.is_authenticated else ""
    return render_template(
        "livemarket.html",
        all_symbols=ALL_SYMBOLS,
        live_data=live_data_dict,
        live_data_columns=list(live_data_dict[0].keys()),
        filterable_columns=filterable_columns,
        islogin=islogin,
        username=username,
    )


@app.route("/investments", methods=["GET", "POST"])
@login_required
def investments():
    user: User = current_user
    islogin, username = user.is_authenticated, user.username
    if request.method == "POST":
        idx = int(request.form["idx"])
        if idx == -1:
            symbol = request.form["symbol"]
            price = sym_price_dict[symbol]
            quantity = int(request.form["quantity"] if request.form["quantity"] else 1)
            user.add_stock(symbol, price, quantity)
        else:
            stock = Stock.query.filter_by(id=idx).first()
            earn = (
                sym_price_dict[stock.symbol] - stock.price_when_added
            ) * stock.quantity
            user.earnings += earn
            db.session.delete(stock)
            db.session.commit()
        return redirect(url_for("investments"))
    stocks = user.get_all_stocks()
    for stk in stocks:
        stk.current_price = sym_price_dict[stk.symbol]
        stk.profit = (stk.current_price - stk.price_when_added) * stk.quantity
        stk.color = "green" if stk.profit >= 0 else "red"
        stk.profit_percent = (stk.profit / stk.price_when_added) * 100
        stk.profit_percent = round(stk.profit_percent, 2)
        stk.profit = round(stk.profit, 2)
        stk.date = stk.date_created.strftime("%d-%m-%Y")
    return render_template(
        "investments.html",
        islogin=islogin,
        username=username,
        earnings=round(user.earnings, 2),
        symbols=ALL_SYMBOLS,
        stocks=stocks,
    )


if __name__ == "__main__":
    Thread(target=download_data.main).start()
    app.run(debug=True)
