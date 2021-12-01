import socket

import config
from pexpect.popen_spawn import PopenSpawn


wrapee_path = "./agent.py"


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


def reader(socket, read_size=4):
    buffer = ""
    while True:
        new_data = socket.recv(read_size).decode()
        buffer += new_data

        if config.separator in buffer:
            data, _, buffer = buffer.partition(config.separator)
            yield data


def exchange_message(child_process, data_in):
    child_process.sendline(data_in)
    data_out = child_process.readline().decode().strip()
    return data_out


def main():
    wrapped = PopenSpawn(wrapee_path)
    assert exchange_message(wrapped, str(2)) == "True"
    assert exchange_message(wrapped, str(3)) == "True"
    assert exchange_message(wrapped, str(4)) == "False"
    assert exchange_message(wrapped, str(5)) == "True"
    assert exchange_message(wrapped, str(6)) == "False"

    sock = socket.socket()
    sock.connect(config.server_address)

    while True:
        for data in reader(sock):
            result = exchange_message(wrapped, data)
            print(f"{data} {result}")
            send(sock, result)


if __name__ == "__main__":
    main()
