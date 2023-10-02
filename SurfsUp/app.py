# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

# Create an app, being sure to pass __name__
app = Flask(__name__)


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# List available routes.
@app.route("/")
def home():

    return (
        f"Welcome to Climate App<br/>"
        f"<br/>Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    recent_dataset = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23')\
        .filter(Measurement.date <= '2017-08-23').order_by(Measurement.date.desc()).all()
    
    # Extract date and precopitation and copy to list
    precip = []
    for date, prcp in recent_dataset:
        precip_dict = {}
        precip_dict[date] = prcp
        precip.append(precip_dict)        
    session.close()

    return jsonify(precip)

# Stations route
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations = session.query(Station.id, Station.station).all()

    station_list = []
    for id, station in stations:
        station_dict = {}
        station_dict[id] = station
        station_list.append(station_dict)        

    session.close()

    return jsonify(station_list)


# Temprerature Observations route
@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    most_recent_date = dt.datetime(2017, 8, 18)

    # Calculate the date one year from the last date in data set.
    year_from_recent_date = most_recent_date - dt.timedelta(days=365)

    tobs_dataset = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
        .filter(Measurement.date <= most_recent_date).filter(Measurement.date >= year_from_recent_date).order_by(Measurement.date.desc()).all()

    # Extract date and precopitation and copy to list
    tobs_list = []
    for date, tobs in tobs_dataset:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    session.close()

    return jsonify(tobs_list)

# Start Date route
@app.route("/api/v1.0/<start>")
def starttime(start):

    session = Session(engine)

    # Convert string to date and get temperature data
    format = "%Y-%m-%d"
    startdate = dt.datetime.strptime(start, format)
    stations = session.query(Station.id, Station.station).all()
    tobs_dataset = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= startdate).all()

    # Convert to dataframe and compute min, mean and max
    df = pd.DataFrame(tobs_dataset, columns=['date', 'tobs'])
    mean = df['tobs'].mean()
    min = df['tobs'].min()
    max = df['tobs'].max()

    temp_list = []
    temp_dict = {"TMIN":min, "TAVG":mean, "TMAX":max}
    temp_list.append(temp_dict)

    session.close()

    return jsonify(temp_list)


# Start/End Date route
@app.route("/api/v1.0/<start>/<end>")
def start_end_time(start, end):

    session = Session(engine)

    # Convert string to date and get temperature data
    format = "%Y-%m-%d"
    startdate = dt.datetime.strptime(start, format)
    enddate = dt.datetime.strptime(end, format)

    # Convert to dataframe and compute min, mean and max
    stations = session.query(Station.id, Station.station).all()
    tobs_dataset = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all()

    temp_list = []
    df = pd.DataFrame(tobs_dataset, columns=['date', 'tobs'])
    mean = df['tobs'].mean()
    min = df['tobs'].min()
    max = df['tobs'].max()

    temp_dict = {"TMIN":min, "TAVG":mean, "TMAX":max}
    temp_list.append(temp_dict)

    session.close()

    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)