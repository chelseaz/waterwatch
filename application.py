import datetime
import re
import requests

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from pattern import web


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
    abv = db.Column(db.String(3), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    inflow = db.Column(db.BigInteger)
    outflow = db.Column(db.BigInteger)
    storage = db.Column(db.BigInteger)

    def toCsvRow(self):
        return ",".join([self.date.strftime("%Y%m%d"), str(self.inflow), str(self.outflow), str(self.storage)])

    header = "DATE,INFLOW (CF),OUTFLOW (CF),STORAGE (CF)"


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/reservoir/<abv>")
def reservoir_api(abv):
    rows = ReservoirData.query.filter_by(abv=abv).order_by(ReservoirData.date).all()
    return ReservoirData.header + "\n" + "\n".join(map(lambda row: row.toCsvRow(), rows))


SECONDS_IN_DAY = 86400
CUBIC_FEET_IN_ACRE_FOOT = 43560
sensors = {
    "inflow": {"id": 76, "convert": (lambda cfs: cfs*SECONDS_IN_DAY )},
    "outflow": {"id": 23, "convert": (lambda cfs: cfs*SECONDS_IN_DAY)}, 
    "storage": {"id": 15, "convert": (lambda af: af*CUBIC_FEET_IN_ACRE_FOOT)}
}


def migrate_up():
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

        record = Reservoir(abv=ID, name=name, latitude=float(Data[1]), longitude=float(Data[2]))
        db.session.add(record)
        db.session.commit()


def fetch_sensor_data(reservoir, sensor_name):
    START_DATE = "1/1/2012"
    END_DATE = "6/5/2014"
    sensor_id = sensors[sensor_name]["id"]
    sensor_convert_fn = sensors[sensor_name]["convert"]
    print "Fetching %s data for reservoir %s, starting %s, ending %s" % (sensor_name, reservoir.abv, START_DATE, END_DATE)

    baseurl = "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s&dur_code=D&sensor_num=%d&START_DATE=%s&END_DATE=%s"
    resp = requests.get(baseurl % (reservoir.abv, sensor_id, START_DATE, END_DATE))
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


def populate_db():
    fetch_reservoirs()
    for reservoir in Reservoir.query.all():
        for key in sensors.keys():
            fetch_sensor_data(reservoir, key)


if __name__ == "__main__":
    app.run()
