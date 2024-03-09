from flask import Flask, render_template, url_for, json, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from dotenv import load_dotenv
import sqlite3 as sql
import os
import random
import requests

#Citation
#code based on : https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv('API_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = 'ARISTENAYWFUL'
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)




# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
 
 
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()



# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)




@app.route('/')
def root():
    return render_template("home.html")


@app.route('/browse')
def browse():

    return render_template("browse.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + 
                                                             random.choice('abcdefghijklmnopqrstuvwxyz') + 
                                                             f"&maxResults=20&key={API_KEY}").json())


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("browse"))
    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("root"))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9115)) 
    app.run(port=port, debug=True) 