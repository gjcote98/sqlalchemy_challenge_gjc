#app.py
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement=Base.classes.measurement
station=Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    #List all routes that are available.
    return (
        f"Available Routes:<br/>"
        f"<br/>"  
        f"Precipitation Data with Dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"Stations and Names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Temprture Observations for Last 12 Months:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, Max, and Avg Temperatures for Given Start Date: (use format of 'yyyy-mm-dd'):<br/>"
        f"/api/v1.0/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min, Max, and Avg Temperatures for Given Start and End Date: (use format of 'yyyy-mm-dd'/'yyyy-mm-dd' for start and end values):<br/>"
        f"/api/v1.0/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    last_date=session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_date=dt.datetime.strptime(last_date,"%Y-%m-%d")
    prev_year=last_date-dt.timedelta(days=365)
    prcp_12mo=session.query(measurement.date,measurement.prcp).filter(measurement.date >= prev_year).all()
    session.close()
    
    precip=[]
    for date, prcp in prcp_12mo:
        precip_dict={}
        precip_dict["date"]= date
        precip_dict["prcp"]=prcp
        precip.append(precip_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)
    activestations=session.query(measurement.station,func.count(measurement.id)).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()
    session.close()
    activestations=list(np.ravel(activestations))
    return jsonify(activestations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    most_active_station_stats=session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).group_by(measurement.station).order_by(func.count(measurement.id).desc()).first()
    session.close()
    most_active_station_stats=list(np.ravel(most_active_station_stats))
    return jsonify(most_active_station_stats)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end=None):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    session = Session(engine)
    date=start
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        start_no_end=session.query(*sel).filter(func.strftime("%m-%d", measurement.date) == date).all()
        start_no_end=list(np.ravel(start_no_end))
        return jsonify(start_no_end)
    start_yes_end=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    start_yes_end=list(np.ravel(start_yes_end))
    return jsonify(start_yes_end)


if __name__ == "__main__":
    app.run(debug=True)

