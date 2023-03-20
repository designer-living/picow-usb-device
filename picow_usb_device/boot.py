from board import *
import storage
import digitalio
import json

from config import DEFAULT_CONFIG

# If GPIO 15 is shorted we will enable storage
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
storageFromPin = not noStoragePin.value

write_config = False
try:
    with open("config.json") as f:
        config = json.load(f)
except OSError as e:
    print("Error loading config: ", e)
    # Most likely we couldn't find the config
    print("Creating default config file")
    config = DEFAULT_CONFIG
    write_config = True

for key in DEFAULT_CONFIG.keys():
    if key not in config:
        print(f"missing {key} - set to {DEFAULT_CONFIG[key]}")
        config[key] = DEFAULT_CONFIG[key]
        write_config = True

if write_config:
    try:
        print("Saving config")
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
        print("Config saved")
    except Exception as e:
        print("Error writing config:", e)

# print("Config:", config)

storageFromFile = config.get("USB_ENABLED", True)
enableUsb = storageFromPin or storageFromFile
print(f"USB: {enableUsb}")
if enableUsb:
    # normal boot
    storage.enable_usb_drive()
    print("Enabled")
else:
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    # usb_cdc.disable()
    # usb_midi.disable()
    print("Disabled")
