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
            'USB_TOGGLE': self.usb_toggle,
            'WATCHDOG_ON': self.watchdog_on,
            'WATCHDOG_OFF': self.watchdog_off,
            'WATCHDOG_TOGGLE': self.watchdog_toggle,
            'CONFIG': self.read_config,
            'WRITE_CONFIG': self.write_config,
            'SETTINGS.TOML': self.settings_toml,
            'WEBFLOW_ON': self.webflow_on,
            'WEBFLOW_OFF': self.webflow_off,
            'WEBFLOW_TOGGLE': self.webflow_toggle,
            'ADMIN_SERVER_TOGGLE': self.admin_server_toggle,
            'SOCKET_SERVER_TOGGLE': self.socket_server_toggle,
        }
        self.settings = ""
        self.config = {}
        self.read_config("")
        self._read_settings_toml()

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
        self._read_config()
        if self.config.get("USB_ENABLED"):
            return "USB_ENABLED\n".encode()
        else:
            return "USB_DISABLED\n".encode()

    def usb_on(self, message):
        return self._write_config(
            "USB_ENABLED",
            True
        )

    def usb_off(self, message):
        return self._write_config(
            "USB_ENABLED",
            False
        )

    def usb_toggle(self, message):
        return self._toggle("USB_ENABLED")

    def watchdog_on(self, message):
        return self._write_config(
            "WATCHDOG_ENABLED",
            True
        )

    def watchdog_off(self, message):
        return self._write_config(
            "WATCHDOG_ENABLED",
            False
        )

    def watchdog_toggle(self, message):
        return self._toggle("WATCHDOG_ENABLED")

    def admin_server_toggle(self, message):
        return self._toggle("ADMIN_SERVER_ENABLED")

    def socket_server_toggle(self, message):
        return self._toggle("SOCKET_SERVER_ENABLED")

    def read_config(self, message):
        self._read_config()
        return f"{self.config}".encode()

    def write_config(self, message):
        # TODO make it so we can write any config by passing it in the message
        # try:
        #     storage.remount("/", False)
        #     with open("config.json", "w") as f:
        #         json.dump(self.config, f)
        #     return f"{self.config}".encode()
        # except Exception as e:
        #     return f"{e}\n".encode()
        return f"NOT IMPLEMENTED".encode()

    def settings_toml(self, message):
        try:
            self._read_settings_toml()
            return f"{self.settings}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def webflow_on(self, message):
        try:
            self._read_settings_toml()
            storage.remount("/", False)
            settings_toml = self.settings.replace('#CIRCUITPY_WEB_API_PASSWORD=', 'CIRCUITPY_WEB_API_PASSWORD=')
            self._write_settings_toml(settings_toml)
            self._read_settings_toml()
            return f"{settings_toml}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def webflow_off(self, message):
        try:
            self._read_settings_toml()
            storage.remount("/", False)
            settings_toml = self.settings.replace('CIRCUITPY_WEB_API_PASSWORD=', '#CIRCUITPY_WEB_API_PASSWORD=')
            self._write_settings_toml(settings_toml)
            self._read_settings_toml()
            return f"{settings_toml}".encode()
        except Exception as e:
            return f"{e}\n".encode()

    def webflow_toggle(self, message):
        if self.web_flow_enabled():
            return self.webflow_off(message)
        else:
            return self.webflow_on(message)

    def web_flow_enabled(self):
        self._read_settings_toml()
        try:
            self.settings.index("#CIRCUITPY_WEB_API_PASSWORD=")
            return False
        except ValueError:
            try:
                self.settings.index("CIRCUITPY_WEB_API_PASSWORD=")
                return True
            except ValueError:
                return False

    def can_handle(self, message):
        # print("Can Handle?", message,  message in self.message_handlers)
        return message in self.message_handlers

    def handle_message(self, message):
        # print(message)
        handler = self.message_handlers.get(message)
        if handler is not None:
            return handler(message)
        return None

    def _write_config(self, key, value):
        self._read_config()
        try:
            self.config[key] = value
            storage.remount("/", False)
            with open("config.json", "w") as f:
                json.dump(self.config, f)
            storage.remount("/", True)
            return self.DONE
        except Exception as e:
            # Reload the config if we had an error.
            self._read_config()
            return f"{e}\n".encode()

    def _read_config(self):
        try:
            with open("config.json") as f:
                self.config = json.load(f)
            return self.config
        except Exception as e:
            return f"{e}\n".encode()

    def _toggle(self, key):
        self._read_config()
        return self._write_config(key, not self.config[key])

    def _read_settings_toml(self):
        try:
            with open("settings.toml") as f:
                self.settings = f.read()
            return self.settings
        except Exception as e:
            return f"{e}\n".encode()

    def _write_settings_toml(self, settings_toml):
        with open("settings.toml", "w") as f:
            f.write(settings_toml)

