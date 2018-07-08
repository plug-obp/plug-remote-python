import sys
import getopt


import functools
import socket
import struct
import pickle

from plug_interface import LanguageModule


class LanguageServer:
    port : int
    module : LanguageModule
    server_socket : socket
    transition2id: dict
    id2transition: dict

    def __init__(self, port, module):
        self.port = port
        self.module = module
        self.transition2id = {}
        self.id2transition = {}

    def create_server_socket(self):
        """Creates a a listening socket for a plug runtime on given port"""
        print("Listening on port " + str(self.port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(1)

    def listen(self):
        """Starts listening to server socket"""
        connected_socket, connected_from = self.server_socket.accept()
        print("Connected to " + str(connected_from))
        alive = self.handle_request(connected_socket)
        while alive:
            alive = self.handle_request(connected_socket)

    def start(self):
        self.create_server_socket()
        self.listen()
        self.server_socket.close()

    def send_int(self, sock, value):
        message = bytearray(4)
        struct.pack_into("<i", message, 0, value)
        sock.send(message)

    def receive_configuration(self, sock):
        size = int(struct.unpack("<i", sock.recv(4))[0])
        f = sock.makefile('rb', size)
        configuration = pickle.load(f)
        f.close()
        return configuration

    def send_configuration(self, sock, configuration):
        buffer = pickle.dumps(configuration)
        self.send_int(sock, len(buffer))
        sock.send(buffer)

    def initial_configurations(self, sock):
        configurations = self.module.transition_relation.initial_configurations()
        self.send_int(sock, len(configurations))

        for config in configurations:
            self.send_configuration(sock, config)

    def fireable_transitions_from(self, sock):
        configuration = self.receive_configuration(sock)

        fireables = self.module.transition_relation.fireable_transitions_from(configuration)

        for transition in fireables:
            id = self.transition2id.get(transition, len(self.transition2id))
            if id == len(self.transition2id):
                self.transition2id[transition] = id
                self.id2transition[id] = transition

        count = len(fireables)
        message = bytearray(4 + 4 + count*4)
        struct.pack_into("<ii", message, 0, count, 4)
        current = 8

        for transition in fireables:
            struct.pack_into("<i", message, current, self.transition2id[transition])
            current += 4
        sock.send(message)


    def fire_one_transition(self, sock):
        source = self.receive_configuration(sock)

        transitionID = int(struct.unpack("<i", sock.recv(4))[0])

        configurations = self.module.transition_relation.fire_one_transition(source, self.id2transition[transitionID])

        self.send_int(sock, len(configurations))

        for config in configurations:
            self.send_configuration(sock, config)

    def send_string(self, sock, string):
        """Sends a string in UTF-8"""
        if (string == None):
            data = bytearray(4)
            struct.pack_into("<i", data, 0, -1)
            sock.send(data)
        else:
            raw = string.encode("utf-8")
            raw_count = len(raw)
            data = bytearray(4)
            struct.pack_into("<i", data, 0, raw_count)
            sock.send(data)
            sock.send(raw)

    def send_configuration_item(self, sock, item):
        """Sends one configuration item"""
        self.send_string(sock, item.get("type", ""))
        self.send_string(sock, item.get("name", ""))
        self.send_string(sock, item.get("icon", ""))

        children = item.get("children", [])
        self.send_configuration_items(sock, children)

    def send_configuration_items(self, sock, items):
        """Sends configuration items"""
        message = bytearray(4)
        struct.pack_into("<i", message, 0, len(items))
        sock.send(message)
        for child in items:
            self.send_configuration_item(sock, child)

    def configuration_items(self, sock):
        configuration = self.receive_configuration(sock)
        self.send_configuration_items(sock, self.module.runtime_view.configuration_items(configuration))

    def fireable_transition_description(self, sock):
        transitionID = int(struct.unpack("<i", sock.recv(4))[0])
        self.send_string(sock, self.module.runtime_view.fireable_transition_description(self.id2transition[transitionID]))

    def receive_atomic_propositions(self, sock):
        """Receives atomic propositions to register"""
        raw_count = bytearray(4)
        sock.recv_into(raw_count)
        count = struct.unpack_from("<i", raw_count)[0]
        result = []
        for _ in range(0, count):
            sock.recv_into(raw_count)
            size = struct.unpack_from("<i", raw_count)[0]
            raw_proposition = bytearray(size)
            sock.recv_into(raw_proposition)
            result.append(raw_proposition.decode("utf-8"))
        return result

    def send_ints(self, sock, ints):
        """Sends an array of integers"""
        count = len(ints)
        message = bytearray(4 + count * 4)
        struct.pack_into("<i", message, 0, count)
        current = 4
        for value in ints:
            struct.pack_into("<i", message, current, value)
            current += 4
        sock.send(message)

    def register_atomic_propositions(self, sock):
        propositions = self.receive_atomic_propositions(sock)
        result = self.module.atom_evaluator.register_atomic_propositions(propositions)
        self.send_ints(sock, result)

    def send_valuations(self, sock, valuations):
        """Sends valuations for atomic propositions"""
        count = len(valuations)
        message = bytearray(4 + count)
        struct.pack_into("<i", message, 0, count)
        current = 4
        for value in valuations:
            try:
                struct.pack_into("B", message, current, value)
            except:
                struct.pack_into("B", message, current, False)
            current += 1
        sock.send(message)

    def atomic_proposition_valuations(self, sock):
        configuration = self.receive_configuration(sock)
        result = self.module.atom_evaluator.atomic_proposition_valuations(configuration)
        self.send_valuations(sock, result)

    def api(self, sock) -> dict:
        return {
            1: functools.partial(self.initial_configurations, sock),
            2: functools.partial(self.fireable_transitions_from, sock),
            3: functools.partial(self.fire_one_transition, sock),
            4: functools.partial(self.register_atomic_propositions, sock),
            5: functools.partial(self.atomic_proposition_valuations, sock),
            10: functools.partial(self.configuration_items, sock),
            11: functools.partial(self.fireable_transition_description, sock)
        }

    def handle_request(self, client_socket):
        """Reads first 2 bytes from request to identify the request"""
        header = bytearray(2)
        client_socket.recv_into(header)
        unpacked = struct.unpack("<BB", header)
        #print(unpacked.__repr__())
        if unpacked[0] == 1:
            self.api(client_socket).get(unpacked[1], "Unknown request: " + unpacked[1].__repr__())()
            return True
        else:
            print("Received EOS")
            return False


def server(soup_module):
    port = 12345
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

    LanguageServer(int(port), soup_module()).start()

#if __name__ == "__main__":

    # port = 12345
    # try:
    #     opts, _ = getopt.getopt(sys.argv[1:], "hp:", ["port="])
    # except getopt.GetoptError:
    #     print ( 'remote.py -p port' )
    #     sys.exit(2)
    #
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print ( 'remote.py -p port' )
    #         sys.exit()
    #     elif opt in ("-p", "--port"):
    #         port = arg
    #
    # print ( "Starting model on port: " + str(port) )
    #
    # LanguageServer(int(port), alice_bob_peterson()).start()

