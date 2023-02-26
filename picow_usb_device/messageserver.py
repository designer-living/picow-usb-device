from socketserver import SocketServer
from usb_handler import UsbHandler

EMPTY_STRING = ""
MESSAGE_DELIMITER = ord("\n")
TRIM_CHAR = "\r"

class MessageServer:

    def __init__(self, pool, name, handler, buffer_size=None):
        self.server = SocketServer(pool)
        self.message = EMPTY_STRING
        self.handler = handler
        self.name = name

        @self.server.message_processor()
        def process(received_message):
            try:
                for letter in received_message:
                    if letter == MESSAGE_DELIMITER:
                        message_to_handle = self.message
                        if len(self.message) > 1 and self.message[-1] == TRIM_CHAR:
                            message_to_handle = self.message[:-1]
                        # print(name, message_to_handle)
                        resp = self.handler.handle_message(message_to_handle)
                        self.message = EMPTY_STRING
                        return resp
                    else:
                        self.message = self.message + chr(letter)
            except Exception as e:
                # print(name)
                # print(e)
                # Reset the message if we have an error as it could be corrupt
                self.message = EMPTY_STRING
            return None
        if buffer_size is not None:
            self.server.request_buffer_size = buffer_size



    def start(self, host, port):
        print(f"Starting {self.name} on {host}:{port}")
        self.server.start(host, port)


    def poll(self):
        self.server.poll()



