import socket
import threading
import sys
import getopt

import obp2_runtime_core as core
import obp2_api_v1_handler as api


class LanguageServer:
    port: int
    server_socket: socket
    module: core.OBP2LanguageModule

    def __init__(self, module, port=1234):
        self.module = module
        self.port = port

    def start(self):
        print("Listening on port " + str(self.port))
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(5)

            while True:
                client_socket, client_address = self.server_socket.accept()
                print("Client ", str(client_address), " connected")
                api_handler = api.APIHandlerV1(self.module, client_socket)
                threading.Thread(target=api_handler.listen).start()
        finally:
            if self.server_socket is not None:
                self.server_socket.close()


def server(soup_module):
    port = 1234
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hp:", ["port="])
    except getopt.GetoptError:
        print('remote.py -p port')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('remote.py -p port')
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg

    print("Starting model on port: " + str(port))

    LanguageServer(soup_module(), int(port)).start()