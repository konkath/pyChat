import socket
import sys
from threading import Thread


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (sys.argv[1], int(sys.argv[2]))
        self.sock.connect(server_address)

        thread = Thread(target=self.get_msg)
        thread.start()

        self.send_msg()

        # TODO join thread
        print('ending init')
        self.sock.close()

    def send_msg(self):
        print(sys.stdout, 'You are now chatting, say hello!')

        try:
            while True:
                message = input()
                self.sock.sendall(bytes(message, 'utf-8'))
        finally:
            print(sys.stderr, 'finally send_msg')

    def get_msg(self):
        while True:
            data = self.sock.recv(4096)
            print(sys.stdout, str(data))

Client()
