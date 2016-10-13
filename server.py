import socket
import sys
from asyncio.tasks import sleep
from threading import Thread

clients = []
message_que = []


class ClientHandler:
    handled_que_size = 0

    def __init__(self, connection):
        self.connection = connection

        print(sys.stdout, 'client connected')
        thread = Thread(target=self.wait_for_msg)
        thread.start()

        self.send_msg()

        # TODO clean thread from clients array
        print(sys.stderr, 'end of init')
        self.connection.close()

    def wait_for_msg(self):
        try:
            while True:
                data = self.connection.recv(4096)
                print(sys.stdout, 'received ', data)

                if data:
                    message_que.append(str(data))
                else:
                    print(sys.stderr, 'break wait_for_msg')
                    break
        finally:
            print(sys.stderr, 'finally wait_for_msg')

    def send_msg(self):
        try:
            while True:
                if self.handled_que_size == len(message_que):
                    sleep(0.2)  # seconds
                else:
                    print(sys.stdout, 'sending', message_que[self.handled_que_size])
                    self.connection.sendall(bytes(message_que[self.handled_que_size], 'utf-8'))
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
