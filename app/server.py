# Integrating Flask and Flutter with: https://stackoverflow.com/questions/64853113/how-to-integrate-flutter-app-with-python-code
# Send matplotlib graphs through Flask: https://stackoverflow.com/questions/49864298/how-do-i-use-flask-to-show-a-generated-matplotlib-image-on-the-same-screen-as-th
from flask import Flask, jsonify, request, Response, make_response
from flask_cors import CORS, cross_origin

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import numpy as np

from Environment import Environment

app = Flask(__name__)


def runEnv(inputs):
    values.Env = Environment(
        railLength=inputs["railLength"],
        latitude=0 if "lat" not in inputs else inputs["lat"],
        longitude=0 if "long" not in inputs else inputs["long"],
        elevation=0 if "elevation" not in inputs else inputs["elevation"],
    )
    if "launch_date" in inputs:
        date = inputs["launch_date"]
        values.Env.setDate((date["year"], date["month"], date["day"], date["hour"],))
    values.Env.setAtmosphericModel(
        type=inputs["modelType"],
        file=None if "atmFilePath" not in inputs else inputs["atmFilePath"],
        dictionary=None if "atmDictionary" not in inputs else inputs["atmDictionary"],
    )

    values.jsonInfo = values.Env.allInfoReturned()
    values.jsonPlots = values.Env.allPlotInfoReturned()


class DataStore:
    jsonInfo = {}
    jsonPlots = []
    jsonInputs = {}
    envInfo = {}


values = DataStore()


@app.route("/Env", methods=["GET", "POST", "OPTIONS"])
@cross_origin()
def index():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    if request.method == "POST":
        runEnv(request.get_json())
    response = jsonify(envInfo=values.jsonInfo, envPlot=values.jsonPlots)
    return response


@app.route("/Env/plots/", methods=["GET"])
@cross_origin()
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


if __name__ == "__main__":
    app.run(debug=True)
    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"
