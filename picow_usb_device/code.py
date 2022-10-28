import socketpool
import wifi
import microcontroller
import time

from socketserver import SocketServer
from secrets import secrets
from usb_handler import UsbHandler
from errno import EADDRINUSE


# Connect to WIFI
print()
ssid = secrets['WIFI_SSID']
print("Connecting to Wifi")
wifi.radio.connect(ssid, secrets['WIFI_PASSWORD'])
print(f"Connected: IP address is {wifi.radio.ipv4_address}")
pool = socketpool.SocketPool(wifi.radio)
server = SocketServer(pool)

EMPTY_STRING = ""
MESSAGE_DELIMITER = ord("\n")
TRIM_CHAR = "\r"
message = ""
usb_handler = UsbHandler("Name")

@server.message_processor()
def process(received_message):
    global message
    # TODO Protect against UNICODE error here
    for letter in received_message.decode():
        if ord(letter) == MESSAGE_DELIMITER:
            if message[-1] == TRIM_CHAR:
                usb_handler.handle_message(message[:-1])
            else:
                usb_handler.handle_message(message)
            message = EMPTY_STRING
        else:
            message = message + letter
    return None

server.request_buffer_size = 64
# TODO remove try/catch when SO_REUSEADDRESS is out
try:
    server.serve_forever(str(wifi.radio.ipv4_address), 5000)
except OSError as ex:
    if ex.errno == EADDRINUSE:
        print("Port in use hard resetting")
        microcontroller.reset()
    raise
