import socket
import sys
from asyncio.tasks import sleep
from threading import Thread
import json
from lab1.json_header import Header

clients = []
message_que = []


class ClientHandler:
    handled_que_size = 0
    connection = None
    p = 23
    g = 5
    a = None
    b = 15
    s = None

    def __init__(self, connection):
        self.connection = connection
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

        print(sys.stderr, 'params exchanged')

    def wait_for_msg(self):
        try:
            while True:
                data = json.loads(self.connection.recv(4096).decode())
                print(sys.stdout, 'received ', data)

                correct_msg = False
                if Header.a.value in data:
                    # TODO
                    correct_msg = True

                if Header.enc.value in data:
                    # TODO
                    correct_msg = True

                if Header.msg.value in data:
                    if Header.who.value in data:
                        message_que.append([data[Header.who.value], data[Header.msg.value]])
                    else:
                        message_que.append([None, data[Header.msg.value]])
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
                    print(sys.stdout, 'sending', message_que[self.handled_que_size])
                    msg = message_que[self.handled_que_size][1]
                    who = message_que[self.handled_que_size][0]

                    if who:
                        json_msg = json.dumps({Header.msg.value: msg, Header.who.value: who}).encode()
                    else:
                        json_msg = json.dumps({Header.msg.value: msg}).encode()

                    self.connection.sendall(bytes(json_msg))
                    self.handled_que_size += 1
        finally:
            print(sys.stderr, 'finally send_msg')


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('', int(sys.argv[1]))
    sock.bind(server_address)
    sock.listen()

    while True:
        print(sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()

        thread = Thread(target=ClientHandler, args=(connection, ))
        thread.start()
        clients.append(thread)

main()
