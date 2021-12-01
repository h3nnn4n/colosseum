import socket
import sys

import config


def send(socket, msg):
    msg += config.separator
    msg = msg.encode()
    msglen = len(msg)
    totalsent = 0
    while totalsent < msglen:
        sent = socket.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


def client_thread(sock):
    n = 2

    while True:
        n += 1
        send(sock, str(n))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(config.server_address)
    server.listen()

    while True:
        (clientsocket, address) = server.accept()
        ct = client_thread(clientsocket)
        ct.run()


if __name__ == "__main__":
    main()
