from socket import socket, AF_INET, SOCK_DGRAM
from time import time

def to_milliseconds(seconds: float):
    return seconds * 1000.0

def listen(hostname, port):
    server_socket = socket(AF_INET, SOCK_DGRAM)

    server_address = (hostname, port)
    server_socket.bind(server_address)

    while True:
        # Receive a message.
        received, client_address = server_socket.recvfrom(4096)
        turnpoint = time()

        # Send back immediately.
        sent = str(turnpoint)
        server_socket.sendto(sent.encode(), client_address)

        # Do the logging (make analytics).
        received = received.decode()
        start = float(received)

        arrival_time = to_milliseconds(turnpoint - start)

        print(f'Message arrived in {arrival_time:.2f} ms')
    
if __name__ == '__main__':
    listen('', 6969)