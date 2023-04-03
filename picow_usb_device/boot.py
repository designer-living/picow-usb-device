from board import *
import storage
import digitalio
import json
import microcontroller
from config import DEFAULT_CONFIG
from utils import *


# boot.py is the entry point for RESET (software, reset button, or power cycle)
# read and process safemode.json if desired

# NVM Safe Mode - clear it for the next Safe Mode
if microcontroller.nvm[NVM_INDEX_SAFEMODE] != SAFEMODECLEAR:
    microcontroller.nvm[NVM_INDEX_SAFEMODE] = SAFEMODECLEAR

# set up the boot dict
boot_dict = create_boot_dict()
# write dict as JSON
precode_file_write("/boot.json", json.dumps(boot_dict))  # use storage.remount()


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
        precode_file_write("config.json", json.dumps(config))
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
