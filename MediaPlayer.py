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
    mqtt_logger.info("Connected to Broker")
    client.subscribe("#") # temp

def on_disconnect(client, userdata, flags, reason_code, properties):
    mqtt_logger.error(f"Lost Connection to Broker")

def on_message(mosq, obj, msg):
    message = bson.loads(msg.payload)
    mqtt_logger.info(f"Received message on topic '{msg.topic}': {message}")
    
    with open("static/current.html", 'w') as file:
        file.write(message["html"])

    window.load_url(getFullPath("static/current.html"))

if __name__ == '__main__':

    # load config
    config = configparser.ConfigParser()
    config.read("config.ini")

    # setup logging
    logging.basicConfig(level=config["Logging"]["log_level"], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=config["Logging"]["log_file"])
    mqtt_logger = logging.getLogger("MQTTClient")
    webview_logger = logging.getLogger("webview")

    # setup the mqtt client and start loop
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect_async(config["MQTT"]["host"], int(config["MQTT"]["port"]), int(config["MQTT"]["keepalive"]))
    client.loop_start()

    # setup the window and display it
    window = webview.create_window('MediaPlayer', config["MediaPlayer"]["default_template"], fullscreen=True, confirm_close=False)
    webview.start()

