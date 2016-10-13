import socket
import sys
from threading import Thread
import json
from lab1.json_header import Header


class Client:
    sock = None

    def __init__(self):
        self.init_connection()

        thread = Thread(target=self.get_msg)
        thread.start()

        self.send_msg()

        # TODO join thread
        print('ending init')
        self.sock.close()

    def init_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (sys.argv[1], int(sys.argv[2]))
        self.sock.connect(server_address)

    def send_msg(self):
        print(sys.stdout, 'You are now chatting, say hello!')

        try:
            while True:
                message = input()
                json_msg = json.dumps({Header.msg.value: message}).encode()
                self.sock.sendall(bytes(json_msg))
        finally:
            print(sys.stderr, 'finally send_msg')

    def get_msg(self):
        while True:
            data = json.loads(self.sock.recv(4096)).decode()

            correct_msg = False
            if Header.p.value in data:
                correct_msg = True
                # TODO

            if Header.g.value in data:
                correct_msg = True
                # TODO

            if Header.b.value in data:
                correct_msg = True
                # TODO

            if Header.msg.value in data:
                print(sys.stdout, data)
                correct_msg = True

            if not correct_msg:
                print(sys.stderr, 'unknown header')

Client()
