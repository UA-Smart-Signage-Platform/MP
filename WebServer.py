from flask import Flask
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/temp")
def ipma_temp():
    url = "https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json"
    id_aveiro = "1210702"

    # get json data of all stations
    response = requests.get(url).json()
    # get the latest information
    key = sorted(list(response.keys()), reverse=True)[0]
    # get the temperature from the station we want
    result = response[key][id_aveiro]["temperatura"]

    return str(result) + "º C"