import socket

from pexpect.popen_spawn import PopenSpawn


wrapee_path = "./agent.py"


def exchange_message(child_process, data_in):
    # print(f"sending {data_in.strip()}")
    child_process.sendline(data_in)
    data_out = child_process.readline().decode()
    # print(f"got {data_out.strip()}")
    return data_out


def main():
    wrapped = PopenSpawn(wrapee_path)
    print(exchange_message(wrapped, str(2)))
    print(exchange_message(wrapped, str(3)))
    print(exchange_message(wrapped, str(4)))
    print(exchange_message(wrapped, str(5)))

    # server_address = ("localhost", 10000)
    # s = socket.connect(server_address)


if __name__ == "__main__":
    main()
