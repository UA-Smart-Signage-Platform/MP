import os

def getFullPath(filename):
    return 'file://' + os.path.abspath(filename)