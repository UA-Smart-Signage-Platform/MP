import os
from screeninfo import get_monitors

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