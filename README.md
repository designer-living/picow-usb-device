# picow-usb-device

## Overview

This is an early port of [https://github.com/foxy82/pi-usb-gadget-controller] from the pi zero w to the pico w.

## Installation 

* Install Circuit Python version 8.0.0 or later on to the Pico W (at time of writing this version is still in beta)
* Into the lib folder copy the adafruit_hid folder from the library bundles.
* Into the main folder copy all the files in this repo.
* Edit `secrets.py` and enter your own `WIFI_SSID` and `WIFI_PASSWORD` 

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

## TODO

1. Port Keyboard
1. Port Mouse
1. Implement and test the keys that send more than one byte for the message. e.g. `KEY_HOMEPAGE` 
1. Test on a Fire TV Device
1. Test on a Google TV device (this might require HID Descriptor changes in a boot.py file see: [https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/hid-devices] to allow the "Netflix buttons"
