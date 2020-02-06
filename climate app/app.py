import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session=Session(engine)
    results=session.query(Measurement.station,Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation=[]
    for station,date,prcp in results:
        precipitation_dict={}
        precipitation_dict['station']=station
        precipitation_dict["date"]=date
        precipitation_dict["precipitation"]=prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)



@app.route('/api/v1.0/stations')
def stations():
    session=Session(engine)
    results=session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    stations=[]
    for id,station,name,latitude,longitude,elevation in results:
        stations_dict={}
        stations_dict['id']=id
        stations_dict['station']=station
        stations_dict['name']=name
        stations_dict['latitude']=latitude
        stations_dict['longitude']=longitude
        stations_dict['elevation']=elevation
        stations.append(stations_dict)
    
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session=Session(engine)
    last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=dt.datetime.strptime(last[0],"%Y-%m-%d")
    querydate = dt.date(last_date.year -1, last_date.month, last_date.day)
    
    results=session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>=querydate).all()
    session.close()

    tobs_list =list(np.ravel(results))
    return jsonify(tobs_list)

  
@app.route('/api/v1.0/<start>')
def start(start):
    session=Session(engine)
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>= start).all()
    session.close()

    statsforstart = []
    for min,avg,max in results:
        statsforstart_dict={}
        statsforstart_dict['minimum']=min
        statsforstart_dict['average']=avg
        statsforstart_dict['maximum']=max
        statsforstart.append(statsforstart_dict)
        
    return jsonify(statsforstart)

@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    session=Session(engine)
    results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>= start).filter(Measurement.date<= stop).all()
    session.close()

    startclose=[]
    for min,avg,max in results:
        startclose_dict={}
        startclose_dict['minimum']=min
        startclose_dict['average']=avg
        startclose_dict['maximum']=max
        startclose.append(startclose_dict)
    
    return jsonify(startclose)

if __name__ == '__main__':
    app.run(debug=True)
