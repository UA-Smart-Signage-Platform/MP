import os

# this way of storing the networks is because
# I can't get a list of the networks after
# creating the hotspot

# it is working but needs to be changed

def get_networks():
    
    if os.path.isfile("networks.txt"):
        with open("networks.txt") as file:
            return file.read().strip('][').replace("'","").split(', ')
    else:
        return os.popen("nmcli -f SSID device wifi | awk 'NR>1' | sed 's/[[:space:]]*$//'").read().split("\n")[:-1]
    
def create_hotspot(ssid, password):
    networks = str(get_networks())
    with open("networks.txt", 'w') as file:
        file.write(networks)
    os.system(f"nmcli dev wifi hotspot ssid {ssid} password '{password}'")
        
def connect(ssid, password):
    os.system("nmcli r wifi off")
    os.system("nmcli r wifi on")
    os.system(f"nmcli device wifi connect {ssid} password {password}")
    os.remove("networks.txt")