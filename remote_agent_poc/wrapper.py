import socket

from pexpect.popen_spawn import PopenSpawn


wrapee_path = "./agent.py"


def exchange_message(child_process, data_in):
    # print(f"sending {data_in.strip()}")
    child_process.sendline(data_in)
    data_out = child_process.readline().decode().strip()
    # print(f"got {data_out}")
    return data_out


def main():
    wrapped = PopenSpawn(wrapee_path)
    assert exchange_message(wrapped, str(2)) == "True"
    assert exchange_message(wrapped, str(3)) == "True"
    assert exchange_message(wrapped, str(4)) == "False"
    assert exchange_message(wrapped, str(5)) == "True"
    assert exchange_message(wrapped, str(6)) == "False"

    # server_address = ("localhost", 10000)
    # s = socket.connect(server_address)


if __name__ == "__main__":
    main()
