from flask import Flask, request
import requests
import json
from flask_cors import CORS
import xml.etree.ElementTree as ET
from utils import striphtml
from flask import render_template, redirect, url_for
import configparser
import os
import secrets
import network_manager
import utils
from flask_wtf import CSRFProtect
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(12).hex()
csrf = CSRFProtect()
csrf.init_app(app)

CONFIG_FILE = "config.ini"
DEFAULT_CONFIG_FILE = "default_config.ini"

@app.route("/ipma/temperature")
def ipma_temp():
    
    temperature_url = "https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json"
    stations_url = "https://api.ipma.pt/open-data/observation/meteorology/stations/stations.json"
    requested_station = request.args.get('station')

    # get information of all the stations
    stations = requests.get(stations_url).json()
    # parse the json into a simpler list [(id,name), ...]
    station_list = [(item['properties']['idEstacao'], item['properties']['localEstacao']) for item in stations]

    fallback_station_id = "1210702" # Universidade de Aveiro
    station_id = fallback_station_id

    for station in station_list:
        if station[1] == requested_station:
            station_id = str(station[0])

    # get temperature data of all stations
    response = requests.get(temperature_url).json()
    # get the latest information
    key = sorted(list(response.keys()), reverse=True)[0]
    # get the temperature from the station we want
    station_info = response[key][station_id]

    # if station does not exist use fallback
    if station_info != None:
        result = station_info["temperatura"]
    else:
        result = response[key][fallback_station_id]["temperatura"]
        requested_station = ""

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


@app.route("/ua/events")
def ua_events():
    url = "https://timelyapp.time.ly/api/calendars/54725998/events"
    headers = {"X-Api-Key":"c6e5e0363b5925b28552de8805464c66f25ba0ce"}

    response = requests.get(url, headers=headers).content
    events = json.loads(response)["data"]["items"]
    event = secrets.choice(events)

    title = event["title"]

    start_datetime = datetime.strptime(event["start_utc_datetime"], "%Y-%m-%d %H:%M:%S")
    start_date =start_datetime.strftime("%d-%m-%Y")
    end_datetime = datetime.strptime(event["end_utc_datetime"], "%Y-%m-%d %H:%M:%S")
    end_date =end_datetime.strftime("%d-%m-%Y")

    if "taxonomy_venue" in event["taxonomies"].keys():
        location = event["taxonomies"]["taxonomy_venue"][0]["title"]
    else:
        location = ""

    if start_date == end_date:
        date = start_date
    else:
        date = f"{start_date} - {end_date}"

    return f'''
    <p style="font-size: 1.5vw; margin: 0; ">{date}</p>
    <p style="font-size: 1.1vw; margin: 0.1vw 0;">{location}</p>
    <p style="font-size: 1.7vw; font-weight: 600; margin-top: 0.5vw;">{title}</p>
    '''

@app.route("/updateConfig", methods=['POST'])
def update_config():

    if is_already_setup():
        return

    config = configparser.ConfigParser()
    if os.path.isfile(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config.read(DEFAULT_CONFIG_FILE)

    for section in config.sections():
        for option in config.options(section):
            new_value = request.form.get(option)
            config.set(section, option, new_value)

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    ssid = request.form.get("network")
    password = request.form.get("wifi_password")
    h_ssid, h_password = network_manager.get_ssid_and_password()

    if password != "":
        network_manager.connect(ssid, password)
        
    if not network_manager.has_internet():
        network_manager.create_hotspot(h_ssid, h_password)
        return redirect("/config")
    else:
        network_manager.disconnect_hotspot()

    utils.get_uuid()
    return "config updated"

@app.route("/config", methods=['GET'])
def config():

    if is_already_setup():
        return

    config = configparser.ConfigParser()
    if os.path.isfile(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config.read(DEFAULT_CONFIG_FILE)

    networks = app.config["networks"]
    return render_template('config.html', config=config, networks=networks)

def is_already_setup():
    if not os.path.isfile(CONFIG_FILE) or not network_manager.has_internet():
        return False
    else:
        return True

def run(networks=None):
    app.config["networks"] = networks
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
