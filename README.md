# picow-usb-device

## Overview

This is an early port of [https://github.com/foxy82/pi-usb-gadget-controller] from the pi zero w to the pico w.

## Installation 

* Install Circuit Python version 8.0.0 or later on to the Pico W (at time of writing this version is still in beta)
* Into the lib folder copy the `adafruit_hid` folder from the library bundles [https://circuitpython.org/libraries]
* Into the lib folder copy `adafruit_httpserver.mpy` from the library bundle
* Into the main folder copy all the files in this repo.
* Edit `secrets.py` and enter your own `WIFI_SSID` and `WIFI_PASSWORD` 
* Edit `config.py` enter the `HOSTNAME` you want to use. You can also set whether certain parts are ENABLED or DISABLED and the ports they use.

## Testing / Running

When plugged in it will open port 5000 on the pico w.

```
$ telnet <ip of pico w> 5000```
Trying 192.168.1.100...
Connected to 192.168.1.100.
Escape character is '^]'.
press|KEY_MUTE
```
## Messages

The message format is: 
```
<key press>|<key>
```
Where `<key_press>` is one of `up` (release the pressed key) , `down` (press and leave pressed the key), `press` (press and immediatly release the key)

`key` is any of the codes that has been implemented in keys.py

## Admin Interface

The admin interface allows you to check boot logs, and reboot the picow amongst other things. The admin interface runs on port 5001 by default. To see the list of avaiable commands look in: `control_handler.py` 

## Web Interface

A very simple web page is included (if enabled) that will allow you to easily send Media Remote Control commands. You can do this by going to the IP address of the picow 

## TODO

1. Test on a Google TV device (this might require HID Descriptor changes in a boot.py file see: [https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/hid-devices] to allow the "Netflix buttons"
