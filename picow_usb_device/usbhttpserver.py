from adafruit_httpserver import HTTPServer, HTTPResponse

from usb_handler import UsbHandler

EMPTY_STRING = ""
MESSAGE_DELIMITER = ord("\n")
TRIM_CHAR = "\r"

class UsbHttpServer:

    def __init__(self, pool, name, handler, buffer_size=None):
        self.server = HTTPServer(pool)
        self.handler = handler
        self.name = name
        if buffer_size is not None:
            self.server.request_buffer_size = buffer_size

        @self.server.route("/")
        def base(request):  # pylint: disable=unused-argument
            """Default reponse is /index.html"""
            return HTTPResponse(filename="/html/index.html")

        @self.server.route("/KEY_UP")
        @self.server.route("/KEY_DOWN")
        @self.server.route("/KEY_LEFT")
        @self.server.route("/KEY_RIGHT")
        @self.server.route("/KEY_ENTER")
        @self.server.route("/KEY_HOMEPAGE")
        @self.server.route("/KEY_BACK")
        @self.server.route("/KEY_MENU")
        @self.server.route("/KEY_PLAYPAUSE")
        @self.server.route("/KEY_MUTE")
        def key_mute(request):  # pylint: disable=unused-argument
            # print(request)
            self.handler.handle_message(f"press|{request.path.split('/')[1]}")
            # print("handled")
            return HTTPResponse(filename="/html/index.html")


    def start(self, host, port):
        print(f"Starting {self.name} on {host}:{port}")
        self.server.start(host, port)


    def poll(self):
        self.server.poll()



