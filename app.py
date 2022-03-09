import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect
from flask import Flask, jsonify
import json

engine = create_engine("sqlite:///Resources\hawaii.sqlite")


# #####################################################

app = Flask(__name__)

@app.route("/")
def home():
    print("Client requested the home page from the server")
    return ("<h1>Welcome to my home page!</h1>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs/< start ><br/>"
        f"/api/v1.0/tobs/< start >/< end >"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    query = """
            SELECT 
                date,prcp
            FROM
                measurement
            """
    conn = engine.connect()
    df = pd.read_sql(query, con=conn)
    conn.close()
    return jsonify(json.loads(df.to_json(orient="records")))
@app.route("/api/v1.0/stations")
def stations():
    query = """
            SELECT DISTINCT
                station
            FROM
                measurement
            """
    conn = engine.connect()
    df = pd.read_sql(query, con=conn)
    conn.close()
    return jsonify(json.loads(df.to_json(orient="records")))


@app.route("/api/v1.0/tobs")
def temps():
    query = """
            SELECT
                station,
                date,
                tobs
            FROM
                measurement
            WHERE
                date >= (
                        SELECT
                           date(MAX(date), '-365 day')
                        FROM
                            measurement
                    )
            ORDER BY 
                date
            """
    conn = engine.connect()
    df1 = pd.read_sql(query, con=conn)
    conn.close()
    most_temp_observations=df1.station.value_counts()
    station_needed=most_temp_observations.index[0]
    df=df1.loc[df1.station==station_needed].reset_index(drop=True)
    return jsonify(json.loads(df.to_json(orient="records")))


@app.route("/api/v1.0/<start>")
def startingdate(start):
    query = f"""
            SELECT 
                station,
                date,
                min(tobs) AS min_temp,
                max(tobs) AS max_temp,
                avg(tobs) AS avg_temp
            FROM
                measurement
            WHERE
               date= '{start}' 
            """
    conn = engine.connect()
    df = pd.read_sql(query, con=conn)
    conn.close()

    return jsonify(json.loads(df.to_json(orient="records")))

@app.route("/api/v1.0/<start>/<end>")
def startandend(start,end):
    query = f"""
            SELECT 
                station,
                date,
                min(tobs) AS min_temp,
                max(tobs) AS max_temp,
                avg(tobs) AS avg_temp
            FROM
                measurement
            WHERE
               date >= '{start}' 
               AND date <= '{end}'
            """
    conn = engine.connect()
    df = pd.read_sql(query, con=conn)
    conn.close()

    return jsonify(json.loads(df.to_json(orient="records")))

@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return "<h1>404</h1><p>I'm sorry, the page you were trying to reach could not be found at this time.</p>", 404


if __name__ == '__main__':
    app.run(debug=True)