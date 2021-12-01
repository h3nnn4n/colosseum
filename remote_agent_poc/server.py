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


def reader(socket, read_size=64):
    buffer = ""
    while True:
        new_data = socket.recv(read_size).decode()
        buffer += new_data

        if config.separator in buffer:
            data, _, buffer = buffer.partition(config.separator)
            yield data


def client_thread(sock):
    n = 2
    send(sock, str(n))

    for result in reader(sock):
        print(result)
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
