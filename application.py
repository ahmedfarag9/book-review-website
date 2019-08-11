import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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

#    session["newusername"] = None
#    session["newpassword"] = None
#    session["username"] = None
#    session["password"] = None
#    session.clear()
    if session:
        session.clear()

        for key in session.keys():
            session.pop(key)

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
    session["newusername"] = request.form.get("newusername")
    session["newpassword"] = request.form.get("newpassword")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": session["newusername"]}).rowcount != 0:
        return render_template("error.html", message="username is already taken")
  
    
    db.execute("INSERT INTO users (username,password) VALUES (:newusername, :newpassword)",
            {"newusername": session["newusername"], "newpassword": session["newpassword"]})

    db.commit()

    return render_template("signingup.html")


@app.route("/signingin", methods=["POST"])
def signingin():

    """ Sign in """
    
    # Check username and psw
    session["username"] = request.form.get("username")
    session["password"] = request.form.get("password")


    if db.execute("SELECT * FROM users WHERE username = :username", {"username":  session["username"]}).rowcount == 0:
        return render_template("error.html", message="The username provided did not match our records. Please re-enter and try again.")

    if db.execute("SELECT * FROM users WHERE password = :password", {"password": session["password"]}).rowcount == 0:
            return render_template("error.html", message="The password you provided did not match our records. Please re-enter and try again.")

    session["user"] =  db.execute("SELECT * FROM users WHERE username = :username", {"username":  session["username"]}).fetchone()  

    session["id"] = session["user"].id

    db.commit()


    return render_template("signingin.html")

@app.route("/homepage", methods=["POST"])
def homepage():

    """ Website homepage """


    return render_template("homepage.html")

@app.route("/search",methods=["POST"])
def search():

    # Search for a book.

    # Get form information.
    session["searchquery"] = request.form.get("search")
    session["option"] = request.form.get("option")
    
    if session["option"] == "title":
    
        """Search by a books's title"""

        try:
            session["title"] = str(session["searchquery"])
            
        except ValueError:
            return render_template("error.html", message="Please enter a valid book's title.")


        if session["title"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter a book's title.")

        if session["title"] == "":
            return render_template("error.html", message="The search box is empty. Please enter a book's title.")


        session["title"] = "%" + session["title"] + "%"
        
        session["searchresults"] = db.execute("SELECT * FROM books WHERE title SIMILAR TO :title", {"title": session["title"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["searchresults"] )





    elif session["option"] == "isbn":
        """Search by a books's isbn number"""
        
        try:
            session["isbn"] = str(session["searchquery"])

        except ValueError:
            return render_template("error.html", message="Please enter a valid book's isbn number.")
            

        if session["isbn"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter a book's isbn number.")
        
        if session["isbn"] == "":
            return render_template("error.html", message="The search box is empty. Please enter a book's isbn number.")

        session["isbn"] = "%" + session["isbn"] + "%"
        


        session["searchresults"] = db.execute("SELECT * FROM books WHERE isbn SIMILAR TO :isbn", {"isbn": session["isbn"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["searchresults"] )


    else:
        """Search by an author's name"""

        try:
            session["author"] = str(session["searchquery"])

        except ValueError:
            return render_template("error.html", message="Please enter a valid author's name.")


        if session["author"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter an author's name.")

        if session["author"] == "":
            return render_template("error.html", message="The search box is empty. Please enter an author's name.")


        session["author"] = "%" + session["author"] + "%"
        
        session["searchresults"] = db.execute("SELECT * FROM books WHERE author SIMILAR TO :author", {"author": session["author"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["searchresults"] )



@app.route("/bookpage/<int:book_id>",methods=["POST", "GET"])
def bookpage(book_id):

    #show info about the chosen book
    session["book_id"] = book_id

    session["book"] = db.execute("SELECT * FROM books WHERE id = :id", {"id": session["book_id"]}).fetchone()

    session["isbn"] = session["book"].isbn

    session["reviews"] = db.execute("SELECT reviews.id, review, rate, user_id, book_id, username FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id" , {"book_id": session["book_id"]}).fetchall()
    
    session["rates"] = db.execute("SELECT rate FROM reviews WHERE book_id = :book_id", {"book_id": session["book_id"]}).fetchall()

    session["res"] = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ssbeJ9OASssx1U3OvHMywQ", "isbns": session["isbn"]})

    session["data"] = session["res"].json()

    session["average_rating"] = session["data"]['books'][0]['average_rating']

    session["work_ratings_count"] = session["data"]['books'][0]['work_ratings_count']


    #Submit your review
    if request.form.get("btn") == "Clicked":


        if db.execute("SELECT * FROM reviews WHERE user_id = :user_id", {"user_id": session["id"]}).rowcount == 0:


            session["newreview"] = request.form.get("newreview")
            session["rate"] = request.form.get("rate")
                

            try:
                session["rate"] = int(session["rate"])
                
            except ValueError:
                return render_template("error.html", message="Please rate the book from 1 to 5 stars.")

            try:
                session["newreview"] = str(session["newreview"])
                
            except ValueError:
                return render_template("error.html", message="Please enter a review.")


            if session["newreview"].isspace() is True:
                return render_template("error.html", message="The review box is empty. Please enter a review.")

            if session["newreview"] == "":
                return render_template("error.html", message="The review box is empty. Please enter a review.")


            db.execute("INSERT INTO reviews (review,rate,user_id,book_id) VALUES (:review, :rate, :user_id, :book_id)",
            {"review": session["newreview"], "rate": session["rate"], "user_id": session["id"], "book_id": session["book_id"]})

            db.commit()

            return render_template("success.html", book=session["book"], message="Your review was submited successfuly")

            
        else:

            return render_template("review-error.html", book=session["book"], message="You've already submited a review")


    db.commit()
    return render_template("bookpage.html", book=session["book"], reviews=session["reviews"], average_rating = session["average_rating"], work_ratings_count = session["work_ratings_count"] )