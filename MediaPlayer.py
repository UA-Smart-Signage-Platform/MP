import webview
import os
import time
import sys
from utils import getURL

def main():
    if len(sys.argv) < 2:
        print("missing arguments")
        exit(-1)
    
    filename = sys.argv[1]

    window = webview.create_window('MediaPlayer', getURL(filename), fullscreen=True)
    webview.start()
    
if __name__ == '__main__':
    main()


