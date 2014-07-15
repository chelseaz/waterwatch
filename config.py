
START_DATE = "01/01/2014"
END_DATE = "05/01/2014"

sensors = {
    "inflow": {"id": 76, "convert": (lambda cfs: cfs*SECONDS_IN_DAY )},
    "outflow": {"id": 23, "convert": (lambda cfs: cfs*SECONDS_IN_DAY)}, 
    "storage": {"id": 15, "convert": (lambda af: af*CUBIC_FEET_IN_ACRE_FOOT)}
}

SECONDS_IN_DAY = 86400
CUBIC_FEET_IN_ACRE_FOOT = 43560

SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/water'
#SQLALCHEMY_DATABASE_URI = 'mysql://chelsea:hetchhetchy@waterwatchca.cgxi4wiqvq40.us-east-1.rds.amazonaws.com/water'
