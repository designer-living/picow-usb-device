import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from keys import keys_consumer_control

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
        return key in keys_consumer_control 
     
    def handle(self, key_state, key):
        if key_state == "press":
            key_to_send = keys_consumer_control.get(key)
            self.device.send(key_to_send)
        elif key_state == "down":
            key_to_send = keys_consumer_control.get(key)
            self.device.press(key_to_send)
        else:
            self.device.release()
            
class KeyboardDevice:
    
    def __init__(self):
        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)  # We're in the US :)

    def can_handle(self, key_state, key):
        return False
     
    def handle(self, key_state, key):
        pass
        
class MouseDevice:
    
    def __init__(self):
        self.device = Mouse(usb_hid.devices)

    def can_handle(self, key_state, key):
        return False
     
    def handle(self, key_state, key):
        pass
