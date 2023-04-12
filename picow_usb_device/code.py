# This is a workaround mentioned here:
# https://github.com/adafruit/circuitpython/issues/7333
import time
# time.sleep(5)

import traceback
import socketpool
import wifi
import board
import digitalio
import microcontroller
import watchdog
import os
import json
from utils import create_run_dict

from config import DEFAULT_CONFIG, get_config_or_default

from iot_management_client import IotManagementClient
from messageserver import MessageServer
from usbhttpserver import UsbHttpServer
from usb_handler import UsbHandler
from control_handler import ControlMessageHandler

run_dict = create_run_dict()
print(run_dict)

# Load Config from config.json
config = {}
try:
    with open("config.json") as f:
        config = json.load(f)
except OSError as e:
    # boot.py should have created a default config file
    # so this error would be strange.
    print("Couldn't open config file but boot.py should have created it! Using default", e)
    config = DEFAULT_CONFIG
print("Config: ", config)

# Turn on the LED, so we can see we have power.
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Watchdog will restart if the app hangs
# I've seen this happen if you hit the webserver too quickly
wdt = None
if get_config_or_default("WATCHDOG_ENABLED", config):
    wdt = microcontroller.watchdog
    wdt.timeout = 5
    wdt.mode = watchdog.WatchDogMode.RESET

# Connect to WI-FI
print()
if not wifi.radio.ipv4_address:
    ssid = os.getenv('CIRCUITPY_WIFI_SSID')
    print(f"Connecting to Wifi: {ssid}")
    wifi.radio.hostname = get_config_or_default("HOSTNAME", config)
    wifi.radio.connect(ssid, os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print(f"Connected: IP address is {wifi.radio.ipv4_address}")

pool = socketpool.SocketPool(wifi.radio)
host = str(wifi.radio.ipv4_address)

updater = IotManagementClient(
    identifier="ALL",
    server_url="http://192.168.1.12:80",
    socket_pool=pool,
)

usb_handler = UsbHandler()
control_handler = ControlMessageHandler()

server = None
if get_config_or_default("SOCKET_SERVER_ENABLED", config):
    server = MessageServer(pool, "USBServer", usb_handler, 64)

http_server = None
if get_config_or_default("HTTP_SERVER_ENABLED", config):
    http_server = UsbHttpServer(pool, "HttpServer", usb_handler, control_handler)

admin_server = None
if get_config_or_default("ADMIN_SERVER_ENABLED", config):
    admin_server = MessageServer(pool, "AdminServer", control_handler)

if server is not None:
    server.start(host, get_config_or_default("PORT", config))
if admin_server is not None:
    admin_server.start(host, get_config_or_default("ADMIN_SERVER_PORT", config))
if http_server is not None:
    http_server.start(host, get_config_or_default("HTTP_SERVER_PORT", config))

while True:
    try:
        if wdt is not None:
            wdt.feed()
        if server is not None:
            server.poll()
        if http_server is not None:
            http_server.poll()
        if admin_server is not None:
            admin_server.poll()
        time.sleep(0.001)
    except OSError as e:
        formatted = traceback.format_exception(e)
        print(formatted)
        continue
    except Exception as e:
        print(e)
        raise e
