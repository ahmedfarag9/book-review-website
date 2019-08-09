import csv
import os


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():


    db.execute("CREATE TABLE books ( id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL  );")
    print("Created books table in database")

    f = open("books.csv")
    reader = csv.reader(f)
    x = 1
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(x)
        x += 1
    print("Added info about all books")


    db.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL );")
    print("Created users table in database")

    db.execute("CREATE TABLE reviews ( id SERIAL PRIMARY KEY, review VARCHAR NOT NULL, rate INTEGER NOT NULL, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books );")
    print("Created reviews table in database")


    db.commit()

if __name__ == "__main__":
    main()