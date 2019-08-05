import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    return render_template("signup.html")
    
@app.route("/signin", methods=["POST"])
def signin():
    return render_template("signin.html")

@app.route("/signingup", methods=["POST"])
def signingup():

    """ Sign up """
    
    # Create new username and new psw
    newusername = request.form.get("newusername")
    newpassword = request.form.get("newpassword")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": newusername}).rowcount != 0:
        return render_template("error.html", message="username is already taken")
  
    
    db.execute("INSERT INTO users (username,password) VALUES (:newusername, :newpassword)",
            {"newusername": newusername, "newpassword": newpassword})

    db.commit()

    return render_template("signingup.html")


@app.route("/signingin", methods=["POST"])
def signingin():

    """ Sign in """
    
    # Check username and psw
    username = request.form.get("username")
    password = request.form.get("password")


    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
        return render_template("error.html", message="The username provided did not match our records. Please re-enter and try again.")

    else:
        if db.execute("SELECT * FROM users WHERE password = :password", {"password": password}).rowcount == 0:
            return render_template("error.html", message="The password you provided did not match our records. Please re-enter and try again.")

    db.commit()


    return render_template("signingin.html")

@app.route("/homepage", methods=["POST"])
def homepage():

    """ Website homepage """


    return render_template("homepage.html")

@app.route("/search",methods=["POST"])
def search():

    return render_template("search.html")
        