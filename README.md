# Installation

If you don't already have virtualenv installed:

	pip install virtualenv

Create a virtual environment to hold the installed packages:

	virtualenv venv

Run the generated script. In the future, prior to running the app you'll want to run this as well.

	source venv/bin/activate 

Now install the packages:

    pip install -r requirements.txt 


# Set up database
Make sure mysql is installed locally. 
Create a user and password (feel free to use the existing root user).
In application.py, update the SQLALCHEMY_DATABASE_URI to use your mysql user/password.
Make sure the water database exists:

    mysql> create database water;

Now create the schema in the python shell:

    >>> from application import *
    >>> migrate_up()

Populate your local database with water data. This might take a few minutes:

    >>> populate_db()


# Running

python application.py 

Navigate to http://localhost:5000/

API endpoint for all reservoirs:
http://localhost:5000/reservoirs

API endpoint for one reservoir's data (e.g. CMN):
http://localhost:5000/reservoir/CMN


# Original inspiration

KQED's [Visualization: How the Drought is Shrinking California’s Reservoirs](http://blogs.kqed.org/lowdown/2014/03/18/into-the-drought-californias-shrinking-reservoirs/)
