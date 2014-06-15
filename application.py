import datetime
import requests

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy


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
    inflow = db.Column(db.Integer)
    outflow = db.Column(db.Integer)
    storage = db.Column(db.Integer)

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


sensor_ids = {"inflow": 76, "outflow": 23, "storage": 15}


def migrate_up():
    db.create_all()
    db.engine.execute("create index reservoir_data_abv_date on reservoir_data (abv, date)")


### TODO: convert units

def fetch_sensor_data(reservoir, sensor_name):
    start_date = "1/1/2012"
    end_date = "6/5/2014"

    baseurl = "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s&dur_code=D&sensor_num=%d&start_date=%s&end_date=%s"
    resp = requests.get(baseurl % (reservoir.abv, sensor_ids[sensor_name], start_date, end_date))
    for line in resp.text.split('\r\n')[2:]:  # exclude first 2 lines
        row = line.split(',')
        if len(row) < 3:
            break

        date = datetime.datetime.strptime(row[0], "%Y%m%d")
        if row[2] == 'm':
            value = 0
        else:
            value = int(row[2])

        record = ReservoirData.query.filter_by(abv=reservoir.abv, date=date).first()
        if record is None:
            record = ReservoirData(abv=reservoir.abv, date=date)
            db.session.add(record)
        setattr(record, sensor_name, value)
        db.session.commit()


def fetch_data(reservoir):
    for key in sensor_ids.keys():
        fetch_sensor_data(reservoir, key)


def populate_db():
    for reservoir in Reservoir.query.all():
        fetch_data(reservoir)


if __name__ == "__main__":
    app.run()
