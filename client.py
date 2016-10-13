import socket
import sys
from time import sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (sys.argv[1], int(sys.argv[2]))
sock.connect(server_address)

try:
    print(sys.stdout, 'You are now chatting, say hello!')
    while True:

        message = input()
        sock.send(bytes(message, 'utf-8'))

        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(4096)
            amount_received += len(data)
            print(sys.stdout, 'received ', str(data))

        sleep(1)
finally:
    print(sys.stderr, 'closing socket')
    sock.close()
