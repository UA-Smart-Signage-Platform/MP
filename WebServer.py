from flask import Flask, request
import requests
import json
from flask_cors import CORS
import xml.etree.ElementTree as ET
from utils import striphtml
from flask import render_template
import configparser
import os

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

@app.route("/config", methods=['GET', 'POST'])
def config():

    config = configparser.ConfigParser()
    if os.path.isfile("config.ini"):
        config.read('config.ini')
    else:
        config.read('default_config.ini')

    if request.method == 'POST':
        for section in config.sections():
            for option in config.options(section):
                new_value = request.form.get(option)
                config.set(section, option, new_value)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        return "Configuration updated successfully!"

    if request.method == 'GET':
        return render_template('config.html', config=config)

def run():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)