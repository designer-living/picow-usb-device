import storage
import supervisor
import microcontroller
from os import remove as delete_file


class ControlMessageHandler:

    DONE = "DONE\n".encode()

    def __init__(self):
        pass

    def handle_message(self, message):
        print(message)

        if message == "SOFT_RESET":
            supervisor.reload()
            return self.DONE

        elif message == "HARD_RESET":
            microcontroller.reset()
            return self.DONE

        elif message == "SHOW_BOOT_OUT":
            with open("boot_out.txt") as f:
                m = f.read()
                return m.encode()

        elif message == "USB_STATUS":
            try:
                with open("flag.usb") as f:
                    f.readlines()
                return "USB_ENABLED\n".encode()
            except OSError as e:
                return "USB_DISABLED\n".encode()
            except Exception as e:
                return f"{e}\n".encode()

        elif message == "USB_ON":
            try:
                storage.remount("/", False)
                f = open('flag.usb', 'w')
                f.close()
                return self.DONE
            except Exception as e:
                return f"{e}\n".encode()

        elif message == "USB_OFF":
            try:
                storage.remount("/", False)
                delete_file('flag.usb')
                return self.DONE
            except Exception as e:
                return f"{e}\n".encode()
        return None
