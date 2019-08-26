Book Review Website
====================

A simple website in which you can search for a book, rate it and write a review about it.

What I Learned
---------------

* Developed a simple flask application and used flask sessions for different users.
* Became more comfortable with HTML and CSS.
* Used SQL to interact with the database.
* Learned how to interact with APIs and JSON data.

Used Technologies/Languages
----------------------------

* Flask
* Python
* Html and Css
* postgre-sql

Installation Steps
-------------------

1- Clone the repository to your local computer.

2- Create an account on heroku and set up a postgreSQL database following these steps (Copied from CS50 web course):

* Navigate to <https://www.heroku.com/> and create an account if you don’t already have one.

* On Heroku’s Dashboard, click “New” and choose “Create new app.”

* Give your app a name, and click “Create app.”

* On your app’s “Overview” page, click the “Configure Add-ons” button.

* In the “Add-ons” section of the page, type in and select “Heroku Postgres.”

* Choose the “Hobby Dev - Free” plan, which will give you access to a free PostgreSQL database that will support 
up to 10,000 rows of data. Click “Provision.”

* Now, click the “Heroku Postgres :: Database” link.

* You should now be on your database’s overview page. Click on “Settings”, and then “View Credentials.” This is the information you’ll need to log into your database. You can access the database via Adminer, filling in the server (the “Host” in the credentials list), your username (the “User”), your password, and the name of the database, all of which you can find on the Heroku credentials page.

3- Run These Commands in order:

    cd /path to the repository

    pip3 install -r requirements.txt

    export FLASK_APP=application.py

    export DATABASE_URL=Link to database

    python3 import.py

    flask run

4- Copy the given URL and open it in your browser.
