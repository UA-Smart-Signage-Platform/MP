import os
from screeninfo import get_monitors
import re
import jinja2
import socket
import qrcode
import requests

# strip html from string
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

# get the correct path to be given
# to pywebview.load_url()
def get_full_path(filename):
    return 'file://' + os.path.abspath(filename)

# get monitor width and height
def get_monitor_size():
    monitor = get_monitors()[0]
    return (monitor.width, monitor.height)

# store content inside a file in
# the static folder
def store_static(filename, content):
    with open("static/" + filename, 'w') as file:
        file.write(content)

# function to load a jinja template
# into string without using flask
def render_jinja_html(template_loc,file_name,**context):

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_loc+'/'), autoescape=True
    ).get_template(file_name).render(context)

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

def generate_wifi_qrcode(
    ssid: str,
    password: str,
    security_type="WPA",
    target: str = "static/wifi_qrcode.png",
) -> None:
    wifi_data = f"WIFI:T:{security_type};S:{ssid};P:{password};;"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(wifi_data)
    qr.make(fit=True)

    qr_code_image = qr.make_image(
        fill_color="black", back_color="white"
    )

    qr_code_image.save(target)
    
# download a file to a specific path
def download_file(url, path_to_save):
    response = requests.head(url)

    if "Content-Disposition" in response.headers:
        content_disposition = response.headers["Content-Disposition"]
        filename_index = content_disposition.find("filename=")
        filename = content_disposition[filename_index + len("filename="):]
        filename = filename.strip('"')
    else:
        filename = url.split("/")[-1]
                        
    response = requests.get(url)
    with open(os.path.join(path_to_save, filename), "wb") as file:
        file.write(response.content)
