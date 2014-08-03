import argparse
import datetime
import json
import os
import re
import requests

from apscheduler.scheduler import Scheduler
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from pattern import web

from config import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
sched = Scheduler()
sched.start()


class Reservoir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abv = db.Column(db.String(3), nullable=False, unique=True)
    name = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    header = "ID,NAME,LATITUDE,LONGITUDE"

    def toCsvRow(self):
        return ",".join([self.abv, self.name, str(self.latitude), str(self.longitude)])

    def to_JSON(self):
        return json.dumps({"id": abv, "latitude": latitude, "longitude": longitude})


class ReservoirData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abv = db.Column(db.String(3), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    inflow = db.Column(db.BigInteger)
    outflow = db.Column(db.BigInteger)
    storage = db.Column(db.BigInteger)

    header = "DATE,INFLOW (CF),OUTFLOW (CF),STORAGE"

    column_by_sensor_name = {"inflow": inflow, "outflow": outflow, "storage": storage}

    def toCsvRow(self):
        return ",".join([self.date.strftime("%Y%m%d"), str(self.inflow), str(self.outflow), str(self.storage)])

    @classmethod
    def column_for_sensor_name(cls, sensor_name):
        return cls.column_by_sensor_name[sensor_name]


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/popover")
def popover():
    return render_template('popover.html')


@app.route("/reservoirs")
def reservoirs_api():
    rows = Reservoir.query.all()
    return Reservoir.header + "\n" + "\n".join(map(lambda row: row.toCsvRow(), rows))


@app.route("/reservoir/<abv>")
def reservoir_api(abv):
    rows = ReservoirData.query.filter_by(abv=abv).order_by(ReservoirData.date).all()
    return ReservoirData.header + "\n" + "\n".join(map(lambda row: row.toCsvRow(), rows))


# TODO: require auth
@app.route("/admin/repopulate-db")
def repopulate_db():
    migrate_up()
    populate_db()


# TODO: pick up any new reservoirs
@app.route("/admin/update-data")
def update_data():
    # the API might not return data for today or yesterday
    end_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%m/%d/%Y")

    for reservoir in Reservoir.query.all():
        for key in sensors.keys():
            last_saved = last_saved_date(reservoir, key)
            if last_saved is None:
                start_date = START_DATE 
            else:
                start_date = (last_saved + datetime.timedelta(days=1)).strftime("%m/%d/%Y")
            fetch_sensor_data(reservoir, key, start_date, end_date)


# This is now handled by Heroku scheduler
# sched.add_cron_job(update_data, day_of_week='sun', hour=6)


def migrate_up():
    db.drop_all()
    db.create_all()
    db.engine.execute("create index reservoir_data_abv_date on reservoir_data (abv, date)")


def fetch_reservoirs():
    xml = requests.get('http://cdec.water.ca.gov/misc/daily_res.html').text
    dom = web.Element(xml)
    for tr in dom.by_tag('tr')[1:]: 
        if re.search(r'colspan="7"', tr.content):
            continue

        name = None
        ID = None
        Data = []  # elevation, latitude, longitude

        for td in tr.by_tag('td'):
            str = td.content
            if re.search(r'href', str):
                name = tr.by_tag('a')[0].content
            elif re.search(r'<b', str):
                ID = tr.by_tag('b')[0].content
            elif re.search(r'\d+', str):
                Data.append(str.strip())

        record = Reservoir(abv=ID, name=name, latitude=float(Data[1]), longitude=-float(Data[2]))
        db.session.add(record)
        db.session.commit()


# start_date and end_date are in MM/DD/YYYY format
def fetch_sensor_data(reservoir, sensor_name, start_date, end_date):
    sensor_id = sensors[sensor_name]["id"]
    sensor_convert_fn = sensors[sensor_name]["convert"]
    print "Fetching %s data for reservoir %s, starting %s, ending %s" % (sensor_name, reservoir.abv, start_date, end_date)

    baseurl = "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s&dur_code=D&sensor_num=%d&start_date=%s&end_date=%s"
    resp = requests.get(baseurl % (reservoir.abv, sensor_id, start_date, end_date))
    for line in resp.text.split('\r\n')[2:]:  # exclude first 2 lines
        row = line.split(',')
        if len(row) < 3:
            break

        date = datetime.datetime.strptime(row[0], "%Y%m%d")
        if row[2] == 'm':
            value = 0
        else:
            value = sensor_convert_fn(int(row[2]))

        record = ReservoirData.query.filter_by(abv=reservoir.abv, date=date).first()
        if record is None:
            record = ReservoirData(abv=reservoir.abv, date=date)
            db.session.add(record)
        setattr(record, sensor_name, value)
        db.session.commit()

    db.session.flush()


def populate_db():
    fetch_reservoirs()
    for reservoir in Reservoir.query.all():
        for key in sensors.keys():
            fetch_sensor_data(reservoir, key, START_DATE, END_DATE)


def last_saved_date(reservoir, sensor_name):
    sensor_col = ReservoirData.column_for_sensor_name(sensor_name)
    latest = ReservoirData.query.filter(ReservoirData.abv == reservoir.abv, sensor_col != None) \
        .order_by(ReservoirData.date.desc()).first()
    return None if latest is None else latest.date


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    sched.print_jobs()
    app.run(host='0.0.0.0', port=port, debug=args.debug)
    