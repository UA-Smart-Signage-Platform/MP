import os
import time
import subprocess
import shlex

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

    if not (3 <= len(ssid) <= 32 and 8 <= len(password) <= 63):
        return

    # add quotation marks to the
    # ssid and password
    ssid = shlex.quote(ssid)
    password = shlex.quote(password)

    command = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
    return subprocess.run(command).returncode


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

def disconnect_hotspot():
    os.system("nmcli r wifi off")
    os.system("nmcli r wifi on")