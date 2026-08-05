#!/usr/bin/env python3

import socketserver

# Reference: https://docs.python.org/3/library/socketserver.html#examples

class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # send intro
        self.wfile.write(b"Please say hello.\n")

        # read response
        data = self.rfile.readline().strip().decode()

        # win
        if data == "hello":
            # Files will be templated prior to the docker image being built
            # so you can still use standard pico style randomization.
            self.wfile.write(b"You are so polite, here's a flag\n{{flag}}\n")

        # lose
        else:
            msg = "I politely asked for 'hello'. You sent '{}'. How rude.\n"
            self.wfile.write(msg.format(data).encode('utf-8'))

def main():
    HOST, PORT = "0.0.0.0", 5555
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()
