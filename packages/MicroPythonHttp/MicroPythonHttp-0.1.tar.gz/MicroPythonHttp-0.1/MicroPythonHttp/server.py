import socket
import os
import sys


def handle_request(client_socket):
    request = client_socket.recv(1024).decode("utf-8")
    headers = request.split("\n")
    filename = headers[0].split()[1]

    if filename == "/":
        filename = "/index.html"

    try:
        with open(os.getcwd() + filename, "rb") as f:
            content = f.read()
            response = "HTTP/1.1 200 OK\n".encode() + content
    except FileNotFoundError:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/404.html", "rb") as f:
            content = f.read()
            response = "HTTP/1.1 404 NOT FOUND\n\n".encode() + content

    client_socket.send(response)
    client_socket.close()


class Server:

    def __init__(self, port=8080):
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", self.port))
        server_socket.listen(5)
        print("Server running on port 8080...")

        while True:
            client_socket, addr = server_socket.accept()
            handle_request(client_socket)

    if __name__ == "__main__":
        try:
            start()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            sys.exit(0)
