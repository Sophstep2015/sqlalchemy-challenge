#Import dependencies 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Set up Flask 
app = Flask(__name__)

# Homepage and Routes
@app.route("/")
def home():
    return (
        f'Welcome to Weather API Homepage!<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/&lt;start&gt;<br/>'
        f'/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>'
        f'Note 1: User to replace start and end with user choosen date entered in the path in "yyyy-mm-dd" format or user will obtain Not Found Error<br/>'
        f'Note 2: Ensure start date comes before end date or user will obtain null values<br/>'
        f'Note 2: Dates entered must occur between 2010-01-01 and 2017-08-23 if earlier or later date is enters data will return for dates are present in the database'
    )

#Precipation Route
@app.route("/api/v1.0/precipitation")
def precipitation():

#Query Database
    session = Session(engine)
    precipitation_query = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

#Establish Dictionary and put into a list & JSONIFY    
    precipitation1 = []
    for date, prcp in precipitation_query:
        precipitation_dict = {"Date": date, "Precipitation": prcp}
        precipitation1.append(precipitation_dict)
    return jsonify(precipitation1)

#Stations Route
@app.route("/api/v1.0/stations")
def stations():

#Query Database
    session = Session(engine)
    station_query = session.query(Station.name).all()
    session.close()

#Establish Dictionary and put into a list & JSONIFY      
    station1 = []
    for name in station_query:
        station_dict = {"Name": name[0]}
        station1.append(station_dict)
    return jsonify(station1)

#Observed Tempurature Route
@app.route("/api/v1.0/tobs")
def tobs():
#Query Database   
    session = Session(engine)

#Establish Top Station
    top_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()
    highest_activity = top_station[0]
    
# Calculate the 12 month mark
    maxdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent = (dt.datetime.strptime(maxdate, "%Y-%m-%d")).date()
    year_ago = most_recent - dt.timedelta(days=365)
    
# Perform query for 12 months of meaurements on the most active station
    tobs_query = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter((Measurement.date >= year_ago) & (Measurement.station == highest_activity)).all()

    session.close()
#Establish Dictionary and put into a list & JSONIFY     
    tobs1 = []
    for name, date, temp in tobs_query:
        tobs_dict = {"Name": name, "Date": date, "Temp": temp}
        tobs1.append(tobs_dict)
    return jsonify(tobs1)

#Start Route
@app.route("/api/v1.0/<start>")
def start(start):

#Query Database    
    session = Session(engine)
    start_query = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

#Establish Dictionary and put into a list & JSONIFY     
    start_stats1 = []
    for Average, Minimum, Maximum in start_query:
        start_dict = {"Start Date": start, "Temp Average": Average, "Temp Minimum": Minimum, "Temp Maximum": Maximum}
        start_stats1.append(start_dict)
    return jsonify(start_stats1)   


#Start and End Route
@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
#Query Database   
    session = Session(engine)
    startend_query = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

#Establish Dictionary and put into a list & JSONIFY     
    startend_stats1 = []
    for Average, Minimum, Maximum in startend_query:
        startend_dict = {"Start Date": start, "End Date": end, "Temp Average": Average, "Temp Minimum": Minimum, "Temp Maximum": Maximum}
        startend_stats1.append(startend_dict)
    return jsonify(startend_stats1)   

#End Statement for Flask
if __name__ == "__main__":
    app.run(debug=True)