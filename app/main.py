from flask import Flask, jsonify, request, make_response
from Environment import *
from Flight import *
from Function import *
from Rocket import *
from SolidMotor import *

app = Flask(__name__)


def runEnv(inputs):
    data.Env = Environment(
        railLength=inputs["railLength"],
        latitude=0 if "lat" not in inputs else inputs["lat"],
        longitude=0 if "long" not in inputs else inputs["long"],
        elevation=0 if "elevation" not in inputs else inputs["elevation"],
    )
    if "launch_date" in inputs:
        date = inputs["launch_date"]
        data.Env.setDate(
            (
                date["year"],
                date["month"],
                date["day"],
                date["hour"],
            )
        )
    data.Env.setAtmosphericModel(
        type=inputs["modelType"],
        file=None if "atmFilePath" not in inputs else inputs["atmFilePath"],
        dictionary=None if "atmDictionary" not in inputs else inputs["atmDictionary"],
    )

    data.env.jsonInfo = data.Env.allInfoReturned()
    data.env.jsonPlots = data.Env.allPlotInfoReturned()


def runMotor(inputs):  # DEBUG SOLIDMOTOR
    data.Motor = SolidMotor(
        thrustSource="Cesaroni_M1670.eng",
        burnOut=3.9,
        grainNumber=5,
        grainSeparation=5 / 1000,
        grainDensity=1815,
        grainOuterRadius=33 / 1000,
        grainInitialInnerRadius=15 / 1000,
        grainInitialHeight=120 / 1000,
        nozzleRadius=33 / 1000,
        throatRadius=11 / 1000,
        interpolationMethod="linear",
    )


def runRocket(inputs):  # DEBUG ROCKET
    data.Rocket = Rocket(
        motor=data.Motor,
        radius=127 / 2000,
        mass=19.197 - 2.956,
        inertiaI=6.60,
        inertiaZ=0.0351,
        distanceRocketNozzle=-1.255,
        distanceRocketPropellant=-0.85704,
        powerOffDrag="powerOffDragCurve.csv",
        powerOnDrag="powerOnDragCurve.csv",
    )
    data.Rocket.setRailButtons([0.2, -0.5])
    NoseCone = data.Rocket.addNose(
        length=0.55829, kind="vonKarman", distanceToCM=0.71971
    )
    FinSet = data.Rocket.addFins(
        4, span=0.100, rootChord=0.120, tipChord=0.040, distanceToCM=-1.04956
    )
    Tail = data.Rocket.addTail(
        topRadius=0.0635, bottomRadius=0.0435, length=0.060, distanceToCM=-1.194656
    )


def runFlight(inputs):
    runMotor(inputs)  # DEBUG
    runRocket(inputs)  # DEBUG
    print(inputs)
    data.Flight = Flight(
        environment=data.Env,
        rocket=data.Rocket,
        inclination=80 if inputs["inclination"] is None else inputs["inclination"],
        heading=90 if inputs["heading"] is None else inputs["heading"],
        rtol=1e-6 if inputs["rtol"] is None else inputs["rtol"],
        atol=6 * [1e-3] + 4 * [1e-6] + 3 * [1e-3]
        if inputs["atol"] is None
        else inputs["atol"],
    )
    data.flight.jsonInfo = data.Flight.allInfoReturned()
    data.flight.jsonPlots = data.Flight.allPlotInfoReturned()
class EnvironmentData:
    jsonInfo = {}
    jsonPlots = []
    envInfo = {}


class FlightData:
    jsonInfo = {}
    jsonPlots = []
    flightInfo = {}


class DataStore:
    env = EnvironmentData()
    flight = FlightData()
    jsonInfo = {}
    jsonPlots = []
    envInfo = {}


data = DataStore()

@app.route("/Env", methods=["GET", "POST", "OPTIONS"])
def environment():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    if request.method == "POST":
        runEnv(request.get_json())
    response = jsonify(envInfo=data.env.jsonInfo, envPlot=data.env.jsonPlots)
    return response


# TODO: Create more routes, this thing is becoming MASSIVE
# Data on GET methods: receiving 1657.9 KB of data, taking 2 secs avg, returning over 63k lines on a JSON
@app.route("/Flight", methods=["GET", "POST", "OPTIONS"])
def flight():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    if request.method == "POST":
        runFlight(request.get_json())
    response = jsonify(
        flightInfo=data.flight.jsonInfo, flightPlot=data.flight.jsonPlots
    )
    return response


@app.route("/Env/plots/", methods=["GET"])
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


