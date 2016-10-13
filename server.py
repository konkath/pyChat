import socket
import sys
from threading import Thread

clients = []


def handle_client(connection):
    while True:
        try:
            print(sys.stdout, 'client connected')
            while True:
                data = connection.recv(4096)
                print(sys.stdout, 'received ', data)
                if data:
                    connection.sendall(data)
                else:
                    break
        finally:
            # TODO clean thread from clients array
            connection.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('', int(sys.argv[1]))
    sock.bind(server_address)
    sock.listen()

    while True:
        print(sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()

        thread = Thread(target=handle_client, args=(connection, ))
        thread.start()
        clients.append(thread)


main()
