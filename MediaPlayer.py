import webview
import os
import time
import sys
import threading
import paho.mqtt.client as mqtt
import logging
import bson
from utils import getFullPath

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        mqtt_logger.info("Connected to MQTT broker")
    else:
        mqtt_logger.error(f"Connection to MQTT broker failed with return code {rc}")

    client.subscribe("group/1")

def on_message(mosq, obj, msg):
    message = bson.loads(msg.payload)
    mqtt_logger.info(f"Received message on topic '{msg.topic}': {message}")
    
    with open("static/current.html", 'w') as file:
        file.write(message["html"])

    window.load_url(getFullPath("static/current.html"))

def on_window_closed():
    webview_logger.error("window has been closed")

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="logs.txt")
    mqtt_logger = logging.getLogger("MQTTClient")
    webview_logger = logging.getLogger("webview")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect("localhost", 1883, 60)

    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.start()

    window = webview.create_window('MediaPlayer', getFullPath("static/template2.html"), fullscreen=True, confirm_close=False)
    window.events.closed += on_window_closed
    webview.start()

