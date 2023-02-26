from board import *
import storage
import digitalio
import json

from config import DEFAULT_CONFIG

# If GPIO 15 is shorted we will enable storage
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
storageFromPin = not noStoragePin.value

# Default to USB enabled if we don't find the config file.
config = {"USB_ENABLED": True}

try:
    with open("config.json") as f:
        config = json.load(f)
except OSError as e:
    try:
        print("Error loading config: ", e)
        # Most likely we couldn't find the config
        print("Creating default config file")
        config = DEFAULT_CONFIG
        storage.remount(
            mount_path="/",
            readonly=False,
        )
        with open("config.json", "w") as f:
            json.dump(config, f)
        storage.remount(
            mount_path="/",
            readonly=True,
        )
    except Exception as e2:
        print("Error creating default config:", e2)

print("Config:", config)

storageFromFile = config.get("USB_ENABLED", True)

enableUsb = storageFromPin or storageFromFile

if enableUsb:
    # normal boot
    print("USB drive enabled")
    storage.enable_usb_drive()
else:
    # don't show USB drive to host PC
    print("Disabling USB drive")
    storage.disable_usb_drive()
    # usb_cdc.disable()
    # usb_midi.disable()
    print("Disabled USB drive")
