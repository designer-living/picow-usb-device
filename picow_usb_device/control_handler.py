import storage
import supervisor
import microcontroller
from os import remove as delete_file


class ControlMessageHandler:

    DONE = "DONE\n".encode()

    def __init__(self):
        self.message_handlers = {
            'SOFT_RESET' : self.soft_reset,
            'HARD_RESET' : self.hard_reset,
            'SHOW_BOOT_OUT': self.show_boot_out,
            'USB_STATUS': self.usb_status,
            'USB_ON': self.usb_on,
            'USB_OFF': self.usb_off,
        }

    def soft_reset(self, message):
        supervisor.reload()
        return self.DONE

    def hard_reset(self, message):
        microcontroller.reset()
        return self.DONE

    def show_boot_out(self, message):
        with open("boot_out.txt") as f:
            m = f.read()
            return m.encode()

    def usb_status(self, message):
        try:
            with open("flag.usb") as f:
                f.readlines()
            return "USB_ENABLED\n".encode()
        except OSError as e:
            return "USB_DISABLED\n".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def usb_on(self, message):
        try:
            storage.remount("/", False)
            f = open('flag.usb', 'w')
            f.close()
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def usb_off(self, message):
        try:
            storage.remount("/", False)
            delete_file('flag.usb')
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def can_handle(self, message):
        print("Can Handle?", message,  message in self.message_handlers)
        return message in self.message_handlers

    def handle_message(self, message):
        print(message)
        handler = self.message_handlers.get(message)
        if handler is not None:
            return handler(message)
        return None
