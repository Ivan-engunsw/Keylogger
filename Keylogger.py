from pynput import keyboard
import time
import os

fileName = "log.txt"
# maximum file size in MB to be read
maxFileSize = 10 * 1024
inputDelayOnHeldSec = 0.5
charsPerSecAfterHeld = 30

lastKeyPressedTime = {}

def on_press(key):
    if key == keyboard.Key.esc:
        return False
    
    lastKeyPressedTime[key] = time.time()

    if (os.path.isfile(fileName) and os.path.getsize(fileName) <= maxFileSize):
        flag = "a"
    else:
        flag = "w"
    with open(fileName, flag) as f:
        lastKeyPressedTimeString = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            f.write(f"{key.char} pressed at {lastKeyPressedTimeString}\n")
        except AttributeError:
            f.write(f"{key.name} pressed at {lastKeyPressedTimeString}\n")

def on_release(key):
    currentTime = time.time()
    if (currentTime - lastKeyPressedTime[key] > inputDelayOnHeldSec):
        print(currentTime)
        print(lastKeyPressedTime)
        with open(fileName, "a") as f:
            i = ((currentTime - lastKeyPressedTime - inputDelayOnHeldSec) / charsPerSecAfterHeld)
            currentTimeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(currentTime))

            try:
                f.write(f"{key.char} repeated {i} times until {currentTimeString}.\n")
            except AttributeError:
                f.write(f"{key.name} repeated {i} times  until {currentTimeString}\n")
    del lastKeyPressedTime[key]
            

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
time.sleep(5)
listener.stop()