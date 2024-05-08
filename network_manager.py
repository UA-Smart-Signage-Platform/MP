import os
import time
import subprocess
from wifi import Cell

def get_networks():
    return os.popen("nmcli -f SSID device wifi | awk 'NR>1' | sed 's/[[:space:]]*$//'").read().split("\n")[:-1]
    
def create_hotspot(ssid, password):
    return subprocess.run(["nmcli", "dev", "wifi", "hotspot", "ssid", ssid, "password", password]).returncode
        
def connect(ssid, password):
    if is_hotspot():
        os.system("nmcli r wifi off")
        os.system("nmcli r wifi on")
        while get_networks() == []:
            time.sleep(1) 

    return subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password]).returncode
     
def has_internet():
    status = os.popen("nmcli networking connectivity check").read().strip()
    if status == "full":
        return True
    elif status == "none":
        return False
    
def is_hotspot():
    status = os.popen("nmcli networking connectivity check").read().strip()
    if status == "limited":
        return True
    return False
    
def get_ssid_and_password():
    result = os.popen("nmcli dev wifi show-password | awk '/SSID:/ { ssid = $2 } /Password:/ { password = $2 } END { print ssid, password }'").read().strip()
    split = result.split(" ")
    return (split[0], split[1])