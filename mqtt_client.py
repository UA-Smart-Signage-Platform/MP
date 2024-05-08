import paho.mqtt.client as mqtt
import utils
import uuid
from protocol import MessageProtocol
import json

class MQTTClient:
    def __init__(self, logger, config, window):
        self.logger = logger
        self.window = window
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
        self.publish_message(client, self.config["MQTT"]["register_topic"], MessageProtocol.register(width, height, self.identifier, self.name))

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.logger.error("Lost Connection to Broker")

    def on_message(self, client, userdata, msg):

        message = json.loads(msg.payload.decode())
        self.logger.info(f"Received message on topic '{msg.topic}': {message}")

        method = message["method"]

        if(method == "CONFIRM_REGISTER"):
            self.registered = True

        elif(method == "TEMPLATE"):
            utils.store_static("current.html", message["html"])
            self.window.load_url(utils.get_full_path("static/current.html"))

    def publish_message(self, topic, payload):
        self.client.publish(topic, payload)
        self.logger.info(f"Sent message on topic '{topic}': {payload}")
