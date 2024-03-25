import os
import re

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def getFullPath(filename):
    return 'file://' + os.path.abspath(filename)