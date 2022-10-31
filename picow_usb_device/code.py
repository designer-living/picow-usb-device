import socketpool
import wifi
import board
import digitalio

from socketserver import SocketServer
from secrets import secrets
from usb_handler import UsbHandler
from control_handler import ControlMessageHandler
# from errno import EADDRINUSE

# Turn on the LED so we can see we have power.
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

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
usb_handler = UsbHandler()
control_handler = ControlMessageHandler()


@server.message_processor()
def process(received_message):
    global message
    try:
        for letter in received_message.decode():
            if ord(letter) == MESSAGE_DELIMITER:
                message_to_handle = message
                if len(message) > 1 and message[-1] == TRIM_CHAR:
                    message_to_handle = message[:-1]

                if not control_handler.handle_message(message_to_handle):
                    usb_handler.handle_message(message_to_handle)
                else:
                    print("Handled Control message")
                message = EMPTY_STRING
            else:
                message = message + letter
    except Exception as e:
        print(e)
        # Reset the message if we have an error as it could be corrupt
        message = EMPTY_STRING
    return None


server.request_buffer_size = 64
# TODO remove try/catch when SO_REUSEADDRESS is out
# https://github.com/adafruit/circuitpython/commit/ca25016b528903716232c4ac86fe680e6fcb0d27
#try:
server.serve_forever(str(wifi.radio.ipv4_address), 5000)
#except OSError as ex:
#    if ex.errno == EADDRINUSE:
#        print("Port in use hard resetting")
#        microcontroller.reset()
#    raise
