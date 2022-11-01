from gadget_devices import ConsumerControlDevice, KeyboardDevice, MouseDevice


class UsbHandler:

    DELIMITER = "|"

    def __init__(self):
        self.devices = [
            MouseDevice(),
            ConsumerControlDevice(),
            KeyboardDevice(),
        ]

    def handle_message(self, message):
        # print(f"Handling message {message}")
        split_message = message.split(self.DELIMITER, 1)
        if len(split_message) == 1:
            key_code = split_message[0]
            key_state = "press"
            pass
        else:
            key_state = split_message[0]
            key_code = split_message[1]

        for device in self.devices:
            if device.can_handle(key_state, key_code):
                device.handle(key_state, key_code)
                break
