import webview
import os
import time
import sys
import threading
import paho.mqtt.client as mqtt
import logging
import json
import uuid
import configparser
import utils
from protocol import MessageProtocol
import WebServer
import threading
import network_manager
from mqtt_client import MQTTClient

# def wait_for_config():
#     pass

def setup():

    while not os.path.exists("config.ini"):
        time.sleep(1)

    # load config
    config = configparser.ConfigParser()
    config.read("config.ini")

    # setup logging
    logging.basicConfig(level=config["Logging"]["log_level"], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=config["Logging"]["log_file"])
    mqtt_logger = logging.getLogger("MQTTClient")
    webview_logger = logging.getLogger("webview")
    
    # create an instante of the mqtt client and start the loop
    mqtt_client = MQTTClient(mqtt_logger, config, window)
    mqtt_client.start()
    
    # change to the default template
    window.load_url(utils.get_full_path(default_config["MediaPlayer"]["default_template"]))
        
if __name__ == '__main__':

    # load default config
    default_config = configparser.ConfigParser()
    default_config.read("default_config.ini")
    
    flask_thread = threading.Thread(target=WebServer.run, daemon=True)
    flask_thread.start()
    
    window = None

    if not os.path.isfile("config.ini"):

        ssid = "DetiSignage-" + str(uuid.uuid4())[:8]
        password = str(uuid.uuid4())[:8]
        network_manager.create_hotspot(ssid,password)
        
        utils.generate_wifi_qrcode(ssid, password, target="static/qr_code.png")
        
        url = utils.get_local_ip() + ":5000/config"

        html = utils.render_jinja_html("templates", "setup.html", ssid=ssid, password=password, url=url)
        utils.store_static("setup.html", html)
        
        window = webview.create_window('MediaPlayer', "static/setup.html", fullscreen=True)
    
    else:
        window = webview.create_window('MediaPlayer', default_config["MediaPlayer"]["default_template"], fullscreen=True, confirm_close=False)
    
    webview.start(func=setup)





