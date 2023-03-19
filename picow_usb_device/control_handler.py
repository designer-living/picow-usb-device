import json
import storage
import supervisor
import microcontroller
import re


class ControlMessageHandler:
    DONE = "DONE\n".encode()

    def __init__(self):
        self.message_handlers = {
            'HELP': self.help,
            'SOFT_RESET': self.soft_reset,
            'HARD_RESET': self.hard_reset,
            'SHOW_BOOT_OUT': self.show_boot_out,
            'USB_STATUS': self.usb_status,
            'USB_ON': self.usb_on,
            'USB_OFF': self.usb_off,
            'WATCHDOG_ON': self.watchdog_on,
            'WATCHDOG_OFF': self.watchdog_off,
            'CONFIG': self.read_config,
            'WRITE_CONFIG': self.write_config,
            'SETTINGS.TOML': self.settings_toml,
            'WEBFLOW_ON': self.webflow_on,
            'WEBFLOW_OFF': self.webflow_off,
        }
        self.config = {}
        self.read_config("")

    def help(self, message):
        resp = "\n".join(self.message_handlers.keys())
        return f"{resp}\n"

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
            self.config["USB_ENABLED"] = True
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def usb_off(self, message):
        try:
            self.config["USB_ENABLED"] = False
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def watchdog_on(self, message):
        try:
            self.config["WATCHDOG_ENABLED"] = True
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def watchdog_off(self, message):
        try:
            self.config["WATCHDOG_ENABLED"] = False
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            return self.DONE
        except Exception as e:
            return f"{e}\n".encode()

    def read_config(self, message):
        try:
            with open("config.json") as f:
                self.config = json.load(f)
            return f"{self.config}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def write_config(self, message):
        # TODO make it so we can write any config by passing it in the message
        try:
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            return f"{self.config}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def settings_toml(self, message):
        try:
            with open("settings.toml") as f:
                self.config = f.read()
            return f"{self.config}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def webflow_on(self, message):
        try:
            storage.remount("/", False)
            with open("settings.toml") as f:
                settings_toml = f.read()
            settings_toml = settings_toml.replace('#CIRCUITPY_WEB_API_PASSWORD=', 'CIRCUITPY_WEB_API_PASSWORD=')
            with open("settings.toml", "w") as f:
                f.write(settings_toml)
            return f"{settings_toml}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def webflow_off(self, message):
        try:
            storage.remount("/", False)
            with open("settings.toml") as f:
                settings_toml = f.read()
            settings_toml = settings_toml.replace('CIRCUITPY_WEB_API_PASSWORD=', '#CIRCUITPY_WEB_API_PASSWORD=')
            with open("settings.toml", "w") as f:
                f.write(settings_toml)
            return f"{settings_toml}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def can_handle(self, message):
        # print("Can Handle?", message,  message in self.message_handlers)
        return message in self.message_handlers

    def handle_message(self, message):
        # print(message)
        handler = self.message_handlers.get(message)
        if handler is not None:
            return handler(message)
        return None
