import os

def getURL(filename):
    return 'file://' + os.path.abspath(filename)