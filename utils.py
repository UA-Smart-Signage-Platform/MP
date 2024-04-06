import os
from screeninfo import get_monitors

def getFullPath(filename):
    return 'file://' + os.path.abspath(filename)

def getMonitorSize():
    monitor = get_monitors()[0]
    return (monitor.width, monitor.height)