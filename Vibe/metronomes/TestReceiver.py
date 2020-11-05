#
# TEST SOCKET RECEIVER
# Written by: Brach Knutson
#

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 9999))

try:
    while True:
        data = sock.recv(1024)
        string = data.decode()
        if len(string) > 0:
            print("recv'd: " + string)

except KeyboardInterrupt:
    print("Interrupted; stopping")