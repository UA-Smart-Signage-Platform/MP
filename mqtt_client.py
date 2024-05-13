import paho.mqtt.client as mqtt
import utils
import uuid
from protocol import MessageProtocol
import json

class MQTTClient:
    def __init__(self, logger, config, scheduler):
        self.logger = logger
        self.scheduler = scheduler
        self.config = config
        self.registered = False
        self.identifier = str(uuid.uuid4())
        self.name = config["MQTT"]["name"]
    
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport=self.config["MQTT"]["transport"])
        self.client.username_pw_set(self.config["MQTT"]["username"], self.config["MQTT"]["password"])
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def start(self):
        self.client.connect_async(self.config["MQTT"]["host"], int(self.config["MQTT"]["port"]), int(self.config["MQTT"]["keepalive"]))
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info("Connected to Broker")
        
        if self.registered:
            return

        # subscribe to topic with our unique identifier
        # so that the server can send us messages "directly"
        client.subscribe(self.identifier)

        # send register message
        width, height = utils.get_monitor_size()
        self.publish_message(self.config["MQTT"]["register_topic"], MessageProtocol.register(width, height, self.identifier, self.name))

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.logger.error("Lost Connection to Broker")

    def on_message(self, client, userdata, msg):

        message = json.loads(msg.payload.decode())
        self.logger.info(f"Received message on topic '{msg.topic}': {message}")

        method = message["method"]

        if(method == "CONFIRM_REGISTER"):
            self.registered = True

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
