from flask import Flask
import requests
import json
from flask_cors import CORS
import xml.etree.ElementTree as ET
from utils import striphtml

app = Flask(__name__)
CORS(app)

@app.route("/ipma/temperature")
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

@app.route("/ua/news")
def ua_news():
    url = "http://services.sapo.pt/UA/Online/contents_xml?n=1"

    # get the the entire xml
    response = requests.get(url).content
    # parse it
    root = ET.fromstring(response)
    # find the description
    content = root[0].find("item").find("description").text

    # remove any embedded html
    return striphtml(content)