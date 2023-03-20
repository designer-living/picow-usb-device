from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

from usb_handler import UsbHandler

EMPTY_STRING = ""
MESSAGE_DELIMITER = ord("\n")
TRIM_CHAR = "\r"

ENABLED_BUTTON_TEMPLATE = """
                    <a class="btn-block btn btn-dark btn-lg text-light btn-outline-primary active" data-toggle="button" aria-pressed="true" href="/{URL}" role="button">
                        {BUTTON_LABEL}
                    </a>
"""
DISABLED_BUTTON_TEMPLATE = """
                    <a class="btn-block btn btn-dark btn-lg text-light btn-outline-primary" href="/{URL}" role="button">
                        {BUTTON_LABEL}
                    </a>
"""


class UsbHttpServer:

    def __init__(self, pool, name, handler, control_handler, buffer_size=None):
        self.server = HTTPServer(pool)
        self.handler = handler
        self.control_handler = control_handler
        self.name = name
        if buffer_size is not None:
            self.server.request_buffer_size = buffer_size

        @self.server.route("/")
        def index(request):  # pylint: disable=unused-argument
            serve_index_file(request)
            # """Default reponse is /index.html"""
            # with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            #     response.send_file("/html/index.html")

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
        def key_pressed(request):  # pylint: disable=unused-argument
            self.handler.handle_message(f"press|{request.path.split('/')[1]}")
            with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
                response.send_file("/html/index.html")

        @self.server.route("/ADMIN")
        def admin(request):  # pylint: disable=unused-argument
            serve_admin_file(request)

        @self.server.route("/SOFT_RESET")
        def soft_reset(request):
            self.control_handler.handle_message("SOFT_RESET")
            serve_admin_file(request)

        @self.server.route("/HARD_RESET")
        def hard_reset(request):
            self.control_handler.handle_message("HARD_RESET")
            serve_admin_file(request)

        @self.server.route("/SHOW_BOOT_OUT")
        def show_boot_out(request):
            message = self.control_handler.handle_message("SHOW_BOOT_OUT")
            serve_text(request, message)

        @self.server.route("/SHOW_CONFIG")
        def show_config(request):
            message = self.control_handler.handle_message("CONFIG")
            serve_text(request, message)

        @self.server.route("/SHOW_SETTINGS_TOML")
        def show_settings_toml(request):
            message = self.control_handler.handle_message("SETTINGS.TOML")
            serve_text(request, message)

        @self.server.route("/USB_TOGGLE")
        def usb_toggle(request):
            message = self.control_handler.handle_message("USB_TOGGLE")
            serve_admin_file(request, message)

        @self.server.route("/WATCHDOG_TOGGLE")
        def watchdog_toggle(request):
            message = self.control_handler.handle_message("WATCHDOG_TOGGLE")
            serve_admin_file(request, message)

        @self.server.route("/WEBFLOW_TOGGLE")
        def webflow_toggle(request):
            message = self.control_handler.handle_message("WEBFLOW_TOGGLE")
            serve_admin_file(request, message)

        @self.server.route("/ADMIN_SERVER_TOGGLE")
        def admin_server_reset(request):
            message = self.control_handler.handle_message("ADMIN_SERVER_TOGGLE")
            serve_admin_file(request, message)

        @self.server.route("/SOCKET_SERVER_TOGGLE")
        def socket_server_reset(request):
            message = self.control_handler.handle_message("SOCKET_SERVER_TOGGLE")
            print(message)
            serve_admin_file(request, message)

        def serve_index_file(request):
            with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
                response.send_file("/html/index.html")

        def serve_text(request, text):
            with HTTPResponse(request, content_type=MIMEType.TYPE_TXT ) as response:
                response.send(text)

        def serve_admin_file(request, message=""):
            with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
                config = control_handler.config
                web_flow_enabled = control_handler.web_flow_enabled
                replacement = {
                    "USB_TOGGLE": _get_button_html("USB_TOGGLE", "USB", config["USB_ENABLED"]),
                    "WATCHDOG_TOGGLE": _get_button_html("WATCHDOG_TOGGLE", "WATCHDOG", config["WATCHDOG_ENABLED"]),
                    "WEBFLOW_TOGGLE": _get_button_html("WEBFLOW_TOGGLE", "WEBFLOW", web_flow_enabled),
                    "ADMIN_SERVER_TOGGLE": _get_button_html("ADMIN_SERVER_TOGGLE", "Admin Server", config["ADMIN_SERVER_ENABLED"]),
                    "SOCKET_SERVER_TOGGLE": _get_button_html("SOCKET_SERVER_TOGGLE", "Socket Server", config["SOCKET_SERVER_ENABLED"]),
                    "MESSAGE": message
                }
                with open("/html/admin.html") as f:
                    admin_file = f.read()
                    admin_file = admin_file.format(**replacement)
                    response.send(admin_file)

        def _get_button_html(url, button_label, enabled):
            if enabled:
                return ENABLED_BUTTON_TEMPLATE.format(
                    URL=url,
                    BUTTON_LABEL=button_label,
                )
            else:
                return DISABLED_BUTTON_TEMPLATE.format(
                    URL=url,
                    BUTTON_LABEL=button_label,
                )

    def start(self, host, port):
        print(f"Starting {self.name} on {host}:{port}")
        self.server.start(host, port)

    def poll(self):
        self.server.poll()



