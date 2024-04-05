from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, timeout
from time import time

def to_milliseconds(seconds: float):
    return seconds * 1000.0

def ping(hostname, port):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client_socket.settimeout(1.0)

    destination = (hostname, port)
    
    start = time()

    sent = str(start)
    client_socket.sendto(sent.encode(), destination)

    try:
        received, address = client_socket.recvfrom(4096)
        end = time()

        received = received.decode()
        turnpoint = float(received)

        c2s = to_milliseconds(turnpoint - start)
        s2c = to_milliseconds(end - turnpoint)

        rtt = to_milliseconds(end - start)
        print(f'client2server={c2s:.2f}, server2client={s2c:.2f} ms, total RTT={rtt:.2f} ms')
    except timeout:
        print('Request timed out.')

    client_socket.close()

if __name__ == '__main__':
    ping('localhost', 6969)