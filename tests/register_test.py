import paho.mqtt.client as mqtt
import json
import sys
import configparser

def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode())
    method = message["method"]

    if(method == "REGISTER"):
        client.publish(message["uuid"], json.dumps({ "method":"CONFIRM_REGISTER", "group": group }))
        print("registered " + message["uuid"] + " to group " + group)
        

if len(sys.argv) < 2:
    print("missing arguments")
    sys.exit(1)

group = sys.argv[1]

config = configparser.ConfigParser()
config.read("config.ini")

# create client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport=config["MQTT"]["transport"])
mqttc.username_pw_set(config["MQTT"]["username"], config["MQTT"]["password"])

# connect to broker
host = config["MQTT"]["host"]
port = int(config["MQTT"]["port"])
keepalive = int(config["MQTT"]["keepalive"])
mqttc.connect(host, port, keepalive)

mqttc.on_message = on_message
mqttc.subscribe(config["MQTT"]["register"])
mqttc.loop_forever()