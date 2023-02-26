import socketpool
import wifi
import board
import digitalio
import time
import microcontroller
import watchdog
import os

from config import PORT, HOSTNAME, WATCHDOG_ENABLED
from config import HTTP_SERVER_ENABLED, HTTP_SERVER_PORT
from config import ADMIN_SERVER_ENABLED, ADMIN_SERVER_PORT


from messageserver import MessageServer
from usbhttpserver import UsbHttpServer
from usb_handler import UsbHandler
from control_handler import ControlMessageHandler

# Turn on the LED so we can see we have power.
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Watchdog will restart if the app hangs
# I've seen this happen if you hit the webserver too quickly
wdt = None
if WATCHDOG_ENABLED:
    wdt = microcontroller.watchdog
    wdt.timeout = 5
    wdt.mode = watchdog.WatchDogMode.RESET

# Connect to WIFI
print()
if not wifi.radio.ipv4_address:
    ssid = os.getenv('CIRCUITPY_WIFI_SSID')
    print(f"Connecting to Wifi: {ssid}")
    wifi.radio.hostname = HOSTNAME
    wifi.radio.connect(ssid, os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print(f"Connected: IP address is {wifi.radio.ipv4_address}")

pool = socketpool.SocketPool(wifi.radio)
host = str(wifi.radio.ipv4_address)

usb_handler = UsbHandler()

server = MessageServer(pool, "USBServer", usb_handler, 64)

http_server = None
if HTTP_SERVER_ENABLED:
    http_server = UsbHttpServer(pool, "HttpServer", usb_handler)

admin_server = None
if ADMIN_SERVER_ENABLED:
    admin_server = MessageServer(pool, "AdminServer", ControlMessageHandler())

server.start(host, PORT)
if admin_server is not None:
    admin_server.start(host, ADMIN_SERVER_PORT)
if http_server is not None:
    http_server.start(host, HTTP_SERVER_PORT)

while True:
    try:
        if wdt is not None:
            wdt.feed()
        server.poll()
        if http_server is not None:
            http_server.poll()
        if admin_server is not None:
            admin_server.poll()
        time.sleep(0.001)
    except OSError as e:
        print(e)
        continue
