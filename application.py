import os

from flask import Flask, session, render_template, jsonify, request
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
    """ Main route which runs first when user access the website """

    # Make sure all previous sessions data is removed
    if session:
        session.clear()

        for key in session.keys():
            session.pop(key)

    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    """ Take a new user to the signup page """

    return render_template("signup.html")
    
@app.route("/signin", methods=["POST"])
def signin():
    """ Take user to the sign in page to sign in using his username and password """

    return render_template("signin.html")

@app.route("/signingup", methods=["POST"])
def signingup():
    """ Take username and password and save them in database  """
    
    # Create new username and new psw
    session["new_username"] = request.form.get("new_username")
    session["new_password"] = request.form.get("new_password")

    # Check for input errors
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": session["new_username"]}).rowcount != 0:
        return render_template("error.html", message="username is already taken")
  
    # Save info into database
    db.execute("INSERT INTO users (username,password) VALUES (:new_username, :new_password)",
            {"new_username": session["new_username"], "new_password": session["new_password"]})

    db.commit()

    return render_template("signingup.html")


@app.route("/signingin", methods=["POST"])
def signingin():
    """ Check whether username and password are correct or not """
    
    # Check username and psw
    session["username"] = request.form.get("username")
    session["password"] = request.form.get("password")

    # Check for input errors
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
    """ simple Website homepage """

    return render_template("homepage.html")

@app.route("/search",methods=["POST"])
def search():
    """ Search for a book """

    # Get form information
    session["search_query"] = request.form.get("search")
    session["option"] = request.form.get("option")
    
    # Search by book title
    if session["option"] == "title":    

        # Check for input errors
        try:
            session["title"] = str(session["search_query"])
            
        except ValueError:
            return render_template("error.html", message="Please enter a valid book's title.")


        if session["title"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter a book's title.")

        if session["title"] == "":
            return render_template("error.html", message="The search box is empty. Please enter a book's title.")

        # Save data to database
        session["title"] = "%" + session["title"] + "%"
        
        session["search_results"] = db.execute("SELECT * FROM books WHERE title SIMILAR TO :title", {"title": session["title"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["search_results"])


    # Search by book isbn number
    elif session["option"] == "isbn":

        # Check for input errors        
        try:
            session["isbn"] = str(session["search_query"])

        except ValueError:
            return render_template("error.html", message="Please enter a valid book's isbn number.")
            

        if session["isbn"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter a book's isbn number.")
        
        if session["isbn"] == "":
            return render_template("error.html", message="The search box is empty. Please enter a book's isbn number.")

        # Save data to database
        session["isbn"] = "%" + session["isbn"] + "%"
        

        session["search_results"] = db.execute("SELECT * FROM books WHERE isbn SIMILAR TO :isbn", {"isbn": session["isbn"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["search_results"] )

    # Search by author name
    else:

        # Check for input errors
        try:
            session["author"] = str(session["search_query"])

        except ValueError:
            return render_template("error.html", message="Please enter a valid author's name.")


        if session["author"].isspace() is True:
            return render_template("error.html", message="The search box is empty. Please enter an author's name.")

        if session["author"] == "":
            return render_template("error.html", message="The search box is empty. Please enter an author's name.")

        # Save data to database
        session["author"] = "%" + session["author"] + "%"
        
        session["search_results"] = db.execute("SELECT * FROM books WHERE author SIMILAR TO :author", {"author": session["author"]}).fetchall()
        
        db.commit()

        return render_template("search.html", results = session["search_results"] )


@app.route("/bookpage/<int:book_id>",methods=["POST", "GET"])
def bookpage(book_id):
    """ Show info about the chosen book and submiting reviews """

    # Get info about book from database
    session["book_id"] = book_id

    session["book"] = db.execute("SELECT * FROM books WHERE id = :id", {"id": session["book_id"]}).fetchone()

    session["isbn"] = session["book"].isbn

    session["reviews"] = db.execute("SELECT reviews.id, review, rate, user_id, book_id, username FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id" , {"book_id": session["book_id"]}).fetchall()
    
    session["rates"] = db.execute("SELECT rate FROM reviews WHERE book_id = :book_id", {"book_id": session["book_id"]}).fetchall()

    # Get info about book from goodreads
    session["res"] = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ssbeJ9OASssx1U3OvHMywQ", "isbns": session["isbn"]})

    session["data"] = session["res"].json()

    session["average_rating"] = session["data"]['books'][0]['average_rating']

    session["work_ratings_count"] = session["data"]['books'][0]['work_ratings_count']


    #Submit a review 
    if request.form.get("btn") == "Clicked":

        # Get info about user from database
        if db.execute("SELECT * FROM reviews WHERE user_id = :user_id", {"user_id": session["id"]}).rowcount == 0:

            # Get review and rate form user
            session["new_review"] = request.form.get("new_review")
            session["rate"] = request.form.get("rate")
            
            # Check for input errors    
            try:
                session["rate"] = int(session["rate"])
                
            except ValueError:
                return render_template("error.html", message="Please rate the book from 1 to 5 stars.")

            try:
                session["new_review"] = str(session["new_review"])
                
            except ValueError:
                return render_template("error.html", message="Please enter a review.")


            if session["new_review"].isspace() is True:
                return render_template("error.html", message="The review box is empty. Please enter a review.")

            if session["new_review"] == "":
                return render_template("error.html", message="The review box is empty. Please enter a review.")

            # Save data to database
            db.execute("INSERT INTO reviews (review,rate,user_id,book_id) VALUES (:review, :rate, :user_id, :book_id)",
            {"review": session["new_review"], "rate": session["rate"], "user_id": session["id"], "book_id": session["book_id"]})

            db.commit()

            return render_template("success.html", book=session["book"], message="Your review was submited successfuly")

            
        else:

            return render_template("review-error.html", book=session["book"], message="You've already submited a review")


    db.commit()
    return render_template("bookpage.html", book=session["book"], reviews=session["reviews"], average_rating = session["average_rating"], work_ratings_count = session["work_ratings_count"] )


@app.route("/api/<book_isbn>")
def book_api(book_isbn):
    """ Return details about a single book as a json when a request is sent to the website api """

    # Make sure book isbn exists
    session["api_book"] = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if session["api_book"] is None:
        return jsonify({"error": "Invalid book_isbn"}), 404

    # fetch data from database        
    session["api_review_count"] = str(db.execute("SELECT id FROM reviews ORDER BY id DESC LIMIT 1").fetchone())   
    session["average_score"] = str(db.execute("SELECT to_char(AVG(rate), '99999999999999999D99') AS average_rate FROM reviews").fetchall())

    db.commit()

    # fit data to send as json 
    tmp = session["average_score"].split("'")
    tmp = str(tmp[1])
    session["average_score"] = float(tmp.strip())

    session["api_review_count"] = int(''.join(e for e in session["api_review_count"] if e.isalnum()))

    # return all info about the book.

    return jsonify({
            "title": session["api_book"].title,
            "author": session["api_book"].author,
            "year": int(session["api_book"].year),
            "isbn": session["api_book"].isbn,
            "review_count": session["api_review_count"],
            "average_score": session["average_score"]
    })