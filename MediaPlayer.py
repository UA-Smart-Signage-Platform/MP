import webview
import os
import time
import sys
import threading
import paho.mqtt.client as mqtt
import logging
import bson
import configparser
from utils import getFullPath

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        mqtt_logger.info("Connected to MQTT broker")
    else:
        mqtt_logger.error(f"Connection to MQTT broker failed with return code {rc}")

    # temp
    client.subscribe("#")

def on_message(mosq, obj, msg):
    message = bson.loads(msg.payload)
    mqtt_logger.info(f"Received message on topic '{msg.topic}': {message}")
    
    with open(config["MediaPlayer"]["current_template"], 'w') as file:
        file.write(message["html"])

    window.load_url(config["MediaPlayer"]["current_template"])

def on_window_closed():
    webview_logger.error("window has been closed")

if __name__ == '__main__':

    # load config
    config = configparser.ConfigParser()
    config.read("config.ini")

    # setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=config["MediaPlayer"]["log_file"])
    mqtt_logger = logging.getLogger("MQTTClient")
    webview_logger = logging.getLogger("webview")

    # setup the mqtt client and attempt to connect
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(config["MQTT"]["host"], int(config["MQTT"]["port"]), int(config["MQTT"]["keepalive"]))

    # start the consuming loop
    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.start()

    # setup the window and display it
    window = webview.create_window('MediaPlayer', config["MediaPlayer"]["default_template"], fullscreen=True, confirm_close=False)
    window.events.closed += on_window_closed
    webview.start()

