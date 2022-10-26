from gadget_devices import ConsumerControlDevice

class UsbHandler:

    DELIMITER = "|"

    def __init__(self, name):
        self.name = name
        self.devices = [
            ConsumerControlDevice(),
            # KeyboardDevice(),
            # MouseDevice(),
        ]

    def handle_message(self, message):
        # if message == "stop":
        #    raise Exception("Stopping")
        split_message = message.split(self.DELIMITER)
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
