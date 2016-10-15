import socket
import sys
from threading import Thread
import json

from lab1.coder import get_secret, handle_resp_message, prepare_message_to_send
from lab1.enums import Header, Encode


class Client:
    myName = None
    sock = None
    encode = None
    p = None
    g = None
    a = 6
    b = None
    s = None

    def __init__(self):
        self.myName = sys.argv[3]
        self.encode = Encode.xor.value

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

        self.s = get_secret(self.p, self.g, self.b)
        print(sys.stderr, 'got secret', self.s)
        print(sys.stderr, 'params exchanged')

    def send_msg(self):
        print(sys.stdout, 'You are now chatting, say hello!')

        try:
            while True:
                message = input()

                if "/enc " in message:
                    splitted = message.split(" ")

                    print(splitted[1])
                    if splitted[1] in Encode.__members__:
                        self.encode = Encode[splitted[1]].value
                        json_msg = json.dumps({Header.enc.value: splitted[1]}).encode()
                        self.sock.sendall(bytes(json_msg))
                    else:
                        print(sys.stderr, 'not supported encryption')
                elif "/keys" in message:
                    json_msg = json.dumps({Header.req.value: Header.keys.value}).encode()
                    self.sock.sendall(bytes(json_msg))
                    # get_msg will handle rest of scenario
                else:
                    self.sock.sendall(prepare_message_to_send(self.encode, self.s, message, self.myName))
        finally:
            print(sys.stderr, 'finally send_msg')

    def get_msg(self):
        while True:
            data = json.loads(self.sock.recv(4096).decode())

            if Header.p.value in data or Header.g.value in data or Header.b.value in data:
                if Header.p.value in data:
                    self.p = data[Header.p.value]

                if Header.g.value in data:
                    self.g = data[Header.g.value]

                if Header.b.value in data:
                    self.b = data[Header.b.value]

                # TODO recalculate a
                json_msg = json.dumps({Header.a.value: self.a}).encode()
                self.sock.sendall(bytes(json_msg))

                self.s = get_secret(self.p, self.g, self.b)
                print(sys.stdout, 'recalculated secret: ', self.s)

            if Header.msg.value in data:
                msg = handle_resp_message(self.encode, self.s, data[Header.msg.value])
                if Header.who.value in data:
                    print(sys.stdout, '[' + data[Header.who.value] + ']: ' + str(msg))
                else:
                    print(sys.stdout, '[anon]: ' + msg)

Client()
