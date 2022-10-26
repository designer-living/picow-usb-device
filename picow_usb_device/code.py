import socketpool
import wifi
import time

from secrets import secrets
from usb_handler import UsbHandler

# Connect to WIFI
print()
ssid = secrets['WIFI_SSID']
print("Connecting to Wifi")
wifi.radio.connect(ssid, secrets['WIFI_PASSWORD'])
print(f"Connected: IP address is {wifi.radio.ipv4_address}")


pool = socketpool.SocketPool(wifi.radio)
print("Creating server socket")
HOST = str(wifi.radio.ipv4_address)
PORT = 80  # Port to listen on
server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.bind((HOST, PORT))
server_socket.listen(10)
print(f"Accepting connections on {HOST}:{PORT}")


# A list of incoming sockets
inputs = []
EMPTY_STRING = ""
MESSAGE_DELIMITER = ord("\n")
TRIM_CHAR = "\r"

buff = bytearray(128)
message = ""
usb_handler = UsbHandler("Name")

try:
    while True:
        for s in inputs:
            try:
                numbytes = s.recvfrom_into(buff)
                received_message = buff[: numbytes[0]]
                print(f"Received {received_message}")
                for letter in received_message.decode():
                    if ord(letter) == MESSAGE_DELIMITER:
                        # Process the whole message
                        if message[-1] == TRIM_CHAR:
                            usb_handler.handle_message(message[:-1])
                        else:
                            usb_handler.handle_message(message)
                        message = EMPTY_STRING
                    else:
                        message = message + letter
            except OSError as e:
                # print("No data ", e)
                pass

        try:
            connection, client_address = server_socket.accept()
            if connection is not None:
                print("Connected by", client_address)
                connection.setblocking(False)
                inputs.append(connection)
        except OSError as e:
            # print(e)
            pass

        time.sleep(0.01)
finally:
    print("Cleaning up")
    server_socket.close()
    time.sleep(1)
    print("Clean up complete")
