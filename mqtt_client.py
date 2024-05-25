import paho.mqtt.client as mqtt
import utils
import uuid
from protocol import MessageProtocol
import json
import threading
import time

class MQTTClient:
    def __init__(self, logger, config, scheduler):
        self.logger = logger
        self.scheduler = scheduler
        self.config = config
        self.identifier = utils.get_uuid()
        self.name = config["MQTT"]["name"]
        self.keepalive_thread = None
        self.stop_keepalive_event = threading.Event()
    
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport=self.config["MQTT"]["transport"], client_id=self.identifier, clean_session=False)
        self.client.username_pw_set(self.config["MQTT"]["username"], self.config["MQTT"]["password"])
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def start(self):
        self.client.connect_async(self.config["MQTT"]["host"], int(self.config["MQTT"]["port"]), int(self.config["MQTT"]["keepalive_mqtt"]))
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info("Connected to Broker")

        # subscribe to topic with our unique identifier
        # so that the server can send us messages "directly"
        client.subscribe(self.identifier, qos=1)

        # send register message
        width, height = utils.get_monitor_size()
        self.publish_message(self.config["MQTT"]["register_topic"], MessageProtocol.register(width, height, self.identifier, self.name))

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.logger.error("Lost Connection to Broker")
        self.stop_keepalive()

    def on_message(self, client, userdata, msg):

        message = json.loads(msg.payload.decode())
        self.logger.info(f"Received message on topic '{msg.topic}': {message}")

        method = message["method"]

        if(method == "CONFIRM_REGISTER"):
            self.stop_keepalive()
            self.start_keepalive()

        elif(method == "RULES"):

            files = message["files"]
            if isinstance(files, list) and len(files) != 0:
                for url in files:
                    utils.download_file(url, "static")
            
            rules = message["rules"]
            self.scheduler.set_rules(rules)

    def publish_message(self, topic, payload):
        self.client.publish(topic, payload)
        self.logger.info(f"Sent message on topic '{topic}': {payload}")


    def keepalive_loop(self):
        while not self.stop_keepalive_event.is_set():
            self.publish_message(self.config["MQTT"]["keepalive_logs_topic"], MessageProtocol.keep_alive(self.identifier))
            delay = int(self.config["MQTT"]["keepalive_logs_delay"])
            self.stop_keepalive_event.wait(delay) 

    def start_keepalive(self):
        if self.keepalive_thread is None or not self.keepalive_thread.is_alive():
            self.stop_keepalive_event.clear()
            self.keepalive_thread = threading.Thread(target=self.keepalive_loop)
            self.keepalive_thread.start()

    def stop_keepalive(self):
        if self.keepalive_thread is not None:
            self.stop_keepalive_event.set()
            self.keepalive_thread.join()