import socket
import sys
from asyncio.tasks import sleep
from random import randint
from threading import Thread
import json

from lab1.coder import get_secret, get_closest_prime
from lab1.enums import Header, Encode
from lab1.msg_helper import handle_resp_message, prepare_message_to_send, receive_message

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
    thread_stop = False
    handled_que_size = 0
    sock = None
    encode = None
    smallest_generator = 2
    smallest_prime = 256
    largest_prime = 1000000
    smallest_b = 2
    largest_b = 100
    p = None
    g = None
    a = None    # Server don't have this
    b = None
    s = None
    id = None

    def __init__(self, connection, thread_id):
        self.sock = connection
        self.id = thread_id
        self.encode = Encode.none.value

        try:
            self.exchange_params()
        except ConnectionAbortedError:
            self.sock.close()
            return

        print(sys.stdout, 'client connected')
        thread = Thread(target=self.wait_for_msg)
        thread.start()

        self.send_msg()

        self.thread_stop = True
        thread.join()

        self.sock.close()

    def randomize_secrets(self):
        self.p = get_closest_prime(randint(self.smallest_prime, self.largest_prime))
        self.g = randint(self.smallest_generator, self.p - 1)
        self.b = randint(self.smallest_b, self.largest_b)

    def exchange_params(self):
        self.randomize_secrets()

        while True:     # Wait for proper initialization
            data = receive_message(self.sock)
            if Header.req.value in data:
                json_msg = json.dumps({Header.p.value: self.p, Header.g.value: self.g}).encode()
                self.sock.sendall(bytes(json_msg))
                break

        json_msg = json.dumps({Header.b.value: get_secret(self.p, self.g, self.b)}).encode()
        self.sock.sendall(bytes(json_msg))

        while True:     # wait for a
            data = receive_message(self.sock)
            if Header.a.value in data:
                self.a = data[Header.a.value]

                if self.a < 1:
                    print(sys.stderr, "Got wrong parameter - closing connection")
                    raise ConnectionAbortedError
                break

        try:
            self.s = get_secret(self.p, self.a, self.b)
        except ArithmeticError:
            print(sys.stderr, "Got wrong secret - closing connection")
            raise ConnectionAbortedError

        print(sys.stderr, 'params exchanged', self.s)

    def refresh_secret(self):
        self.randomize_secrets()

        json_msg = json.dumps({Header.p.value: self.p, Header.g.value: self.g,
                               Header.b.value: get_secret(self.p, self.g, self.b)}).encode()
        self.sock.sendall(bytes(json_msg))

        data = receive_message(self.sock)
        if Header.a.value in data:
            self.a = data[Header.a.value]

            if self.a < 1:
                print(sys.stderr, "Got wrong parameter - closing connection")
                raise ConnectionAbortedError

        try:
            self.s = get_secret(self.p, self.a, self.b)
        except ArithmeticError:
            print(sys.stderr, "Got wrong secret - closing connection")
            raise ConnectionAbortedError

        print(sys.stderr, 'recalculated secret', self.s)

    def wait_for_msg(self):
        while True:
            try:
                data = receive_message(self.sock)
            except ConnectionError:
                print(sys.stderr, "Connection error - client has left conversation")
                return

            print(sys.stdout, 'received ', data)

            correct_msg = False
            if Header.req.value in data:
                correct_msg = True

                try:
                    self.refresh_secret()
                except ConnectionAbortedError:
                    return

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

    def send_msg(self):
        while True:
            if self.handled_que_size == len(message_que):
                sleep(0.2)  # seconds
            else:
                if message_que[self.handled_que_size].id != self.id:
                    msg = message_que[self.handled_que_size].msg
                    who = message_que[self.handled_que_size].who
                    print(sys.stdout, 'sending [' + who + ']: ' + msg)

                    try:
                        self.sock.sendall(prepare_message_to_send(self.encode, self.s, msg, who))
                    except ConnectionResetError:
                        print(sys.stderr, "Cant send message - client have left conversation")
                        return

                self.handled_que_size += 1

            # file descriptor == -1 means socket is closed
            if self.thread_stop or self.sock.fileno() == -1:
                return


def server_quit(sock):
    while True:
        cmd = input()

        if "/q" in cmd:
            sock.close()

            for client in clients:
                print('closing')
                client[0].close()
                client[1].join()
            return


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('', int(sys.argv[1]))
    sock.bind(server_address)
    sock.listen()

    leave_thread = Thread(target=server_quit, args=(sock, ))
    leave_thread.start()

    thread_id = 0
    print(sys.stderr, 'waiting for a connection')
    while True:
        try:
            connection, client_address = sock.accept()
        except OSError:
            print(sys.stdout, 'Closing server')
            break

        thread = Thread(target=ClientHandler, args=(connection, thread_id, ))
        thread.start()
        clients.append([connection, thread])
        thread_id += 1

    leave_thread.join()

main()
