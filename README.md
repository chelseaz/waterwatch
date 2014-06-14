# Installation

pip install -r requirements.txt 


# Set up database
Make sure mysql is installed locally. 
Create a user and password (feel free to use the existing root user).
In application.py, update the SQLALCHEMY_DATABASE_URI for your mysql user/password.
Make sure the water database exists:

mysql> create database water;

Now create the schema in the python shell:

>>> from application import db
>>> db.create_all()


# Running

python application.py 

Navigate to http://localhost:5000/