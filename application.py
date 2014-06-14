from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/water'
db = SQLAlchemy(app)


class Reservoir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abv = db.Column(db.String(3), nullable=False, unique=True)
    name = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class ReservoirData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abv = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False)
    inflow = db.Column(db.Integer)
    outflow = db.Column(db.Integer)
    storage = db.Column(db.Integer)


@app.route("/")
def hello():
    return render_template('index.html')

sensor_ids = {"inflow": 76, "outflow": 23, "storage": 15}


def fetch_sensor_data(station_id, sensor_name):
    start_date = "1/1/2014"
    end_date = "6/5/2014"

    baseurl = "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s&dur_code=D&sensor_num=%d&start_date=%s&end_date=%s"
    resp = requests.get(baseurl % (station_id, sensor_ids[sensor_name], start_date, end_date))
    return resp.text


def fetch_data(reservoir):
    inflow = fetch_sensor_data(reservoir.abv, "inflow")
    print inflow


def populate_db():
    for reservoir in Reservoir.query.all():
        fetch_data(reservoir)


if __name__ == "__main__":
    app.run()
