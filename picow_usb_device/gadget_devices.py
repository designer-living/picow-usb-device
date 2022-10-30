import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from keys import KEYS_CONSUMER_CONTROL, KEYS_KEYBOARD, KEYBOARD_MODIFIER_KEYS, MOUSE_BUTTONS

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

from adafruit_hid.mouse import Mouse


class ConsumerControlDevice:

    def __init__(self):
        self.device = ConsumerControl(usb_hid.devices)

    def can_handle(self, key_state, key):
        """
        Ask the gadget if it can handle this message_type/message.
        returns True if it can handle it or False if this gadget can't
        handle this message.
        """
        return key_state in ["up", "down", "press"] and key in KEYS_CONSUMER_CONTROL

    def handle(self, key_state, key):
        if key_state == "press":
            key_to_send = KEYS_CONSUMER_CONTROL.get(key)
            self.device.send(key_to_send)
        elif key_state == "down":
            key_to_send = KEYS_CONSUMER_CONTROL.get(key)
            self.device.press(key_to_send)
        elif key_state == "up":
            self.device.release()


class KeyboardDevice:

    def __init__(self):
        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)  # We're in the US :)

    def can_handle(self, key_state, key):
        return key_state in ["up", "down", "press"] and (key in KEYS_KEYBOARD or key in KEYBOARD_MODIFIER_KEYS)

    def handle(self, key_state, key):
        key_to_send = KEYS_KEYBOARD.get(key, None)
        if key_to_send is None:
            key_to_send = KEYBOARD_MODIFIER_KEYS.get(key, None)

        if key_to_send is None:
            print(f"Unknown key {key}")
            return False

        if key_state == "press":
            self.keyboard.send(key_to_send)
        elif key_state == "down":
            self.keyboard.press(key_to_send)
        elif key_state == "up":
            self.keyboard.release(key_to_send)


class MouseDevice:

    DELIMITER = "|"

    def __init__(self):
        self.device = Mouse(usb_hid.devices)

    def can_handle(self, key_state, key):
        if key_state == "rel":
            return True
        elif key_state in ["up", "down", "press"] and key in MOUSE_BUTTONS:
            return True
        return False

    def handle(self, key_state, key):
        if key_state == "press":
            key_to_send = MOUSE_BUTTONS.get(key)
            self.device.click(key_to_send)
        elif key_state == "down":
            key_to_send = MOUSE_BUTTONS.get(key)
            self.device.press(key_to_send)
        elif key_state == "up":
            key_to_send = MOUSE_BUTTONS.get(key)
            self.device.release(key_to_send)
        elif key_state == "rel":
            split_message = key.split(self.DELIMITER)
            if len(split_message) != 2:
                print(f"Unexpected message: {key}")
            else:
                self.device.move(x=int(split_message[0]), y=int(split_message[1]))

