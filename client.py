import socket
import sys
from threading import Thread
import json
from lab1.json_header import Header


class Client:
    myName = None
    sock = None
    p = None
    g = None
    a = 6
    b = None
    s = None

    def __init__(self):
        self.myName = sys.argv[3]
        self.init_connection()
        self.exchange_params()

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

    def exchange_params(self):
        json_msg = json.dumps({Header.req.value: Header.keys.value}).encode()
        self.sock.sendall(bytes(json_msg))

        # In case server gives p and g in separate messages
        while not self.p or not self.g:
            data = json.loads(self.sock.recv(4096).decode())
            if Header.p.value in data:
                self.p = data[Header.p.value]

            if Header.g.value in data:
                self.g = data[Header.g.value]

        json_msg = json.dumps({Header.a.value: self.a}).encode()
        self.sock.sendall(bytes(json_msg))

        while not self.b:
            data = json.loads(self.sock.recv(4096).decode())
            if Header.b.value in data:
                self.b = data[Header.b.value]

        print(sys.stderr, 'params exchanged')

    def send_msg(self):
        print(sys.stdout, 'You are now chatting, say hello!')

        try:
            while True:
                message = input()
                json_msg = json.dumps({Header.msg.value: message, Header.who.value: self.myName}).encode()
                self.sock.sendall(bytes(json_msg))
        finally:
            print(sys.stderr, 'finally send_msg')

    def get_msg(self):
        while True:
            data = json.loads(self.sock.recv(4096).decode())

            if Header.p.value in data:
                self.p = Header.p.value
                # TODO recalculate s

            if Header.g.value in data:
                self.g = Header.g.value
                # TODO recalculate s

            if Header.b.value in data:
                self.b = Header.b.value
                # TODO recalculate s

            if Header.msg.value and Header.who.value in data:
                print(sys.stdout, '[' + data[Header.who.value] + ']: ' + data[Header.msg.value])
            elif Header.msg.value in data:
                print(sys.stdout, '[anon]: ' + data[Header.msg.value])

Client()
