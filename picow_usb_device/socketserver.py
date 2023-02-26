try:
    from typing import Any, Callable
except ImportError:
    pass
from errno import EAGAIN, ECONNRESET
import time


class SocketServer:
    """A basic socket-based server."""

    def __init__(self, socket_source: Any, buffer_size: int = 1024) -> None:
        """Create a server, and get it ready to run.
        :param socket_source: An object that is a source of sockets.
          This could be a `socketpool` in CircuitPython or
          the `socket` module in CPython.
        """
        self._buffer = bytearray(buffer_size)
        self.routes = {}
        self._socket_source = socket_source
        self._sock = None
        self._connections = []
        self._message_processor = None

    def message_processor(self):
        """Decorator used to add a message_processor.
        Example::
            @server.message_processor()
            def message_processor_func(message):
                raw_text = message.decode("utf8")
                print("Received a message of length", len(raw_text), "bytes")
                response = raw_text
                return response
        """

        def message_processor_decorator(func: Callable) -> Callable:
            self._message_processor = func
            return func

        return message_processor_decorator

    def serve_forever(self, host: str, port: int = 80) -> None:
        """Wait for connections at the given host and port. Does not return.
        :param str host: host name or IP address
        :param int port: port
        """
        self.start(host, port)

        while True:
            try:
                self.poll()
                time.sleep(0.001)
            except OSError:
                continue

    def start(self, host: str, port: int) -> None:
        """
        Start the socket server at the given host and port. Requires calling
        poll() in a while loop to handle incoming requests.
        :param str host: host name or IP address
        :param int port: port
        :param str root: root directory to serve files from
        """
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_STREAM
        )
        self._sock.setblocking(False)  # non-blocking socket
        self._sock.bind((host, port))
        self._sock.listen(10)
        self._send_buffer = list()

    def poll(self):
        """
        Call this method inside your main event loop to get the server to
        check for new incoming client requests. When a request comes in,
        the application callable will be invoked.
        """
        for conn in self._connections:
            still_open = self._poll_incoming_messages(conn)
            if not still_open:
                self._connections.remove(conn)
#        for message in self._send_buffer:
#            for conn in self._connections:
#                self._send(conn, message)
        self._poll_incoming_connections()

    def send(self, message):
        self._send_buffer.append(message)

    def _send(self, conn, buf):  # pylint: disable=no-self-use
        bytes_sent = 0
        bytes_to_send = len(buf)
        view = memoryview(buf)
        while bytes_sent < bytes_to_send:
            try:
                bytes_sent += conn.send(view[bytes_sent:])
            except OSError as exc:
                if exc.errno == EAGAIN:
                    continue
                if exc.errno == ECONNRESET:
                    return

    def _poll_incoming_messages(self, conn):
        try:
            numbytes, _ = conn.recvfrom_into(self._buffer)
            received_message = self._buffer[: numbytes]
            if numbytes == 0:
                # Connection has been closed by the other end.
                return False
            if self._message_processor:
                response = self._message_processor(received_message)
            else:
                raise Exception("No message processor specified")
            if response:
                self._send(conn, response)
            return True

        except OSError as ex:
            # handle EAGAIN and ECONNRESET
            if ex.errno == EAGAIN:
                # there is no data available right now, try again later.
                return True
            if ex.errno == ECONNRESET:
                # connection reset by peer, close the connection.
                return False
            raise

    def _poll_incoming_connections(self):
        try:
            connection, client_address = self._sock.accept()
            # if connection is not None:
            # print("Connection from ", client_address)
            connection.setblocking(False)
            self._connections.append(connection)
        except OSError as ex:
            # handle EAGAIN and ECONNRESET
            if ex.errno == EAGAIN:
                # there is no data available right now, try again later.
                return
            if ex.errno == ECONNRESET:
                # connection reset by peer, try again later.
                return
            raise

    @property
    def request_buffer_size(self) -> int:
        """
        The maximum size of the incoming request buffer. If the default size isn't
        adequate to handle your incoming data you can set this after creating the
        server instance.
        Default size is 1024 bytes.
        Example::
            server = HTTPServer(pool)
            server.request_buffer_size = 2048
            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return len(self._buffer)

    @request_buffer_size.setter
    def request_buffer_size(self, value: int) -> None:
        self._buffer = bytearray(value)
