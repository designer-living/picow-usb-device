from board import *
import storage
import digitalio

storageFromPin = False
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
storageFromPin = not noStoragePin.value

storageFromFile = False
try:
    with open("flag.usb") as f:
        f.readlines()
    storageFromFile = True
except OSError as e:
    print(e)

enableUsb = storageFromPin or storageFromFile

if enableUsb:
    # normal boot
    print("USB drive enabled")
else:
    # don't show USB drive to host PC
    print("Disabling USB drive")
    storage.disable_usb_drive()
    # usb_cdc.disable()
    # usb_midi.disable()
    print("Disabled USB drive")
