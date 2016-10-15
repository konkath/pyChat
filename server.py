import base64
import socket
import sys
from asyncio.tasks import sleep
from threading import Thread
import json

from lab1.coder import get_secret, handle_resp_message, prepare_message_to_send
from lab1.enums import Header, Encode

clients = []
message_que = []


class Message:
    who = None
    msg = None
    id = None

    def __init__(self, who, msg, id):
        self.who = who
        self.msg = msg
        self.id = id

    def __str__(self):
        return '[' + self.who + ']: ' + self.msg


class ClientHandler:
    handled_que_size = 0
    connection = None
    encode = None
    # 23 409 7919
    p = 409
    g = 5
    a = None
    b = 15
    s = None
    id = None

    def __init__(self, connection, thread_id):
        self.connection = connection
        self.id = thread_id
        self.encode = Encode.xor.value

        self.exchange_params()

        print(sys.stdout, 'client connected')
        thread = Thread(target=self.wait_for_msg)
        thread.start()

        self.send_msg()

        # TODO clean thread from clients array
        print(sys.stderr, 'end of init')
        self.connection.close()

    def exchange_params(self):
        data = json.loads(self.connection.recv(4096).decode())
        if Header.req.value in data:
            json_msg = json.dumps({Header.p.value: self.p, Header.g.value: self.g}).encode()
            self.connection.sendall(bytes(json_msg))
        else:
            # TODO Wrong starting request?
            pass

        json_msg = json.dumps({Header.b.value: self.b}).encode()
        self.connection.sendall(bytes(json_msg))

        data = json.loads(self.connection.recv(4096).decode())
        if Header.a.value in data:
            self.a = data[Header.a.value]
        else:
            # TODO No a?
            pass

        self.s = get_secret(self.p, self.g, self.b)
        print(sys.stderr, 'got secret', self.s)
        print(sys.stderr, 'params exchanged')

    def refresh_secret(self):
        # TODO recalculate before sending
        json_msg = json.dumps({Header.p.value: self.p, Header.g.value: self.g, Header.b.value: self.b}).encode()
        self.connection.sendall(bytes(json_msg))

        data = json.loads(self.connection.recv(4096).decode())
        if Header.a.value in data:
            self.a = data[Header.a.value]

        self.s = get_secret(self.p, self.g, self.b)
        print(sys.stderr, 'recalculated secret', self.s)

    def wait_for_msg(self):
        try:
            while True:
                data = json.loads(self.connection.recv(4096).decode())
                print(sys.stdout, 'received ', data)

                correct_msg = False
                if Header.req.value in data:
                    correct_msg = True
                    self.refresh_secret()

                if Header.enc.value in data:
                    correct_msg = True
                    if data[Header.enc.value] in Encode.__members__:
                        self.encode = Encode[data[Header.enc.value]].value
                    else:
                        print(sys.stderr, "not supported encoding")     # TODO inform client?

                if Header.msg.value in data:
                    msg = handle_resp_message(self.encode, self.s, data[Header.msg.value])
                    print(sys.stdout, 'decrypted: ', msg)

                    if Header.who.value in data:
                        message_que.append(Message(data[Header.who.value], str(msg), self.id))
                    else:
                        message_que.append(Message(None, str(msg), self.id))
                    correct_msg = True

                if not correct_msg:
                    print(sys.stderr, 'unknown header')
        finally:
            print(sys.stderr, 'finally wait_for_msg')

    def send_msg(self):
        try:
            while True:
                if self.handled_que_size == len(message_que):
                    sleep(0.2)  # seconds
                else:
                    if message_que[self.handled_que_size].id != self.id:
                        msg = message_que[self.handled_que_size].msg
                        who = message_que[self.handled_que_size].who
                        print(sys.stdout, 'sending [' + who + ']: ' + msg)

                        self.connection.sendall(prepare_message_to_send(self.encode, self.s, msg, who))
                    self.handled_que_size += 1
        finally:
            print(sys.stderr, 'finally send_msg')


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('', int(sys.argv[1]))
    sock.bind(server_address)
    sock.listen()

    thread_id = 0
    while True:
        print(sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()

        thread = Thread(target=ClientHandler, args=(connection, thread_id, ))
        thread.start()
        clients.append(thread)
        thread_id += 1

main()
