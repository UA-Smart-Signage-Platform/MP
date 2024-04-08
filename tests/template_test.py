import paho.mqtt.client as mqtt
import sys
import configparser
import paho.mqtt.publish as publish
import json

def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

if len(sys.argv) < 3:
    print("missing arguments | python template_test.py [group] [file]")
    sys.exit(1)

group = sys.argv[1]
file = sys.argv[2]

config = configparser.ConfigParser()
config.read("config.ini")

# create client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(config["MQTT"]["username"], config["MQTT"]["password"])

# connect to broker
host = config["MQTT"]["host"]
port = int(config["MQTT"]["port"])
username = config["MQTT"]["username"]
password = config["MQTT"]["password"]
topic = "group/" + group

payload = {"method":"TEMPLATE","html":read_html_file(file),"files":[],"schedule":[]}

publish.single(topic=topic, payload=json.dumps(payload), hostname=host, port=port, auth={"username":username, "password":password})
