import socket
import sys
from random import randint
from threading import Thread
import json

from lab1.coder import get_secret, is_prime
from lab1.enums import Header, Encode
from lab1.msg_helper import handle_resp_message, prepare_message_to_send, receive_message


class Client:
    myName = None
    sock = None
    encode = None
    smallest_a = 2
    largest_a = 100
    p = None    # Client don't have this
    g = None    # Client don't have this
    a = None
    b = None    # Client don't have this
    s = None

    def __init__(self):
        self.myName = sys.argv[3]
        self.encode = Encode.none.value

        try:
            self.init_connection()
            self.exchange_params()
        except ConnectionAbortedError:
            self.sock.close()
            return

        thread = Thread(target=self.send_msg)
        thread.daemon = True    # thread can be daemonized as it doesn't hold any resources and it has blocking context
        thread.start()          # (reading from stdin)

        self.get_msg()
        self.sock.close()

    def init_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (sys.argv[1], int(sys.argv[2]))

        try:
            self.sock.connect(server_address)
        except ConnectionRefusedError:
            print(sys.stderr, 'Cant connect to the server - closing')
            raise ConnectionAbortedError

    def exchange_params(self):
        json_msg = json.dumps({Header.req.value: Header.keys.value}).encode()
        try:
            self.sock.sendall(bytes(json_msg))
        except ConnectionResetError:
            raise ConnectionAbortedError

        # In case server gives p and g in separate messages
        while not self.p or not self.g:
            data = receive_message(self.sock)
            if Header.p.value in data:
                self.p = data[Header.p.value]

                if not is_prime(self.p):
                    raise ConnectionAbortedError

            if Header.g.value in data:
                self.g = data[Header.g.value]

                if self.g < 1 or self.g >= self.p:
                    raise ConnectionAbortedError

        self.a = randint(self.smallest_a, self.largest_a)
        json_msg = json.dumps({Header.a.value: get_secret(self.p, self.g, self.a)}).encode()
        self.sock.sendall(bytes(json_msg))

        while not self.b:
            data = receive_message(self.sock)
            if Header.b.value in data:
                self.b = data[Header.b.value]

        self.s = get_secret(self.p, self.b, self.a)
        print(sys.stderr, 'params exchanged')

    def send_msg(self):
        print(sys.stdout, 'You are now chatting, say hello!')

        while True:
            message = input()

            try:
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
                elif "/q" in message:
                    self.sock.close()   # shouldn't terminate program like that but... exceptions will do rest
                else:
                    self.sock.sendall(prepare_message_to_send(self.encode, self.s, message, self.myName))
            except ConnectionResetError:
                print(sys.stderr, 'Server closed - closing connection')

    def check_params(self):
        if not is_prime(self.p) or self.g < 1 or self.g >= self.p or self.b < 1:
            return False

        return True

    def get_msg(self):
        while True:
            try:
                data = receive_message(self.sock)
            except ConnectionError:
                print(sys.stderr, 'Server closed connection')
                return

            if Header.p.value in data or Header.g.value in data or Header.b.value in data:
                if Header.p.value in data:
                    self.p = data[Header.p.value]

                if Header.g.value in data:
                    self.g = data[Header.g.value]

                if Header.b.value in data:
                    self.b = data[Header.b.value]

                if not self.check_params():
                    print(sys.stderr, 'Got wrong parameters - Closing connection')
                    return

                self.a = randint(self.smallest_a, self.largest_a)
                json_msg = json.dumps({Header.a.value: get_secret(self.p, self.g, self.a)}).encode()

                try:
                    self.sock.sendall(bytes(json_msg))
                except ConnectionResetError:
                    print('Server closed connection - closing')
                    return

                try:
                    self.s = get_secret(self.p, self.b, self.a)
                except ArithmeticError:
                    print(sys.stderr, 'Got wrong secret - closing connection')
                    return

                print(sys.stdout, 'recalculated secret: ', self.s)

            if Header.msg.value in data:
                msg = handle_resp_message(self.encode, self.s, data[Header.msg.value])
                if Header.who.value in data:
                    print(sys.stdout, '[' + data[Header.who.value] + ']: ' + str(msg))
                else:
                    print(sys.stdout, '[anon]: ' + msg)

Client()
