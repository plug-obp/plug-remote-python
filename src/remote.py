"""Import sockets"""
import socket
import struct

CONF_SIZE = "conf_size"
TRANSITION_SIZE = "transition_size"
INITIAL_CONFIGURATIONS = "initial_configurations"
FIREABLE_TRANSITIONS_FROM = "fireable_transitions_from"
FIRE_TRANSITION = "fire_transition"
REGISTER_ATOMIC_PROPOSITIONS = "register_atomic_propositions"
ATOMIC_PROPOSITION_VALUATIONS = "atomic_proposition_valuations"

def create_server_socket(port):
    """Creates a a listening socket for a plug runtime on given port"""
    print "Listening on port " + str(port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.bind(("", port))
    server_socket.listen(1)
    return server_socket

def receive_configuration(connected_socket, model):
    """Receives a configuration from the remote plug"""
    conf_size = model[CONF_SIZE]
    raw_conf = bytearray(conf_size)
    connected_socket.recv_into(raw_conf)
    return raw_conf

def receive_atomic_propositions(connected_socket):
    """Receives atomic propositions to register"""
    raw_count = bytearray(4)
    connected_socket.recv_into(raw_count)
    count = struct.unpack_from("<i", raw_count)[0]
    result = []
    for _ in range(0, count):
        connected_socket.recv_into(raw_count)
        size = struct.unpack_from("<i", raw_count)[0]
        raw_proposition = bytearray(size)
        connected_socket.recv_into(raw_proposition)
        result.append(raw_proposition.decode("utf-8"))
    return result

def receive_transition(connected_socket, model):
    """Receives a transition from the remote plug"""
    transition_size = model[TRANSITION_SIZE]
    raw_transition = bytearray(transition_size)
    connected_socket.recv_into(raw_transition)
    return raw_transition

def send_configurations(connected_socket, model, configurations):
    """Sends the given configurations to the remote plug"""
    count = len(configurations)
    size = model[CONF_SIZE]

    message = bytearray(4+8+size*count)
    struct.pack_into("<iq", message, 0, count, size)
    current = 12
    for configuration in configurations:
        for i in range(0, min(len(configuration), size)):
            message[current+i] = configuration[i]
        current += size
    connected_socket.send(message)

def send_transitions(connected_socket, model, transitions):
    """Sends the given transisions to the remote plug"""
    count = len(transitions)
    size = model[TRANSITION_SIZE]

    message = bytearray(4+8+size*count)
    struct.pack_into("<iq", message, 0, count, size)
    current = 12
    for transition in transitions:
        for i in range(0, min(len(transition), size)):
            message[current+i] = transition[i]
        current += size
    connected_socket.send(message)

def send_valuations(connected_socket, valuations):
    """Sends valuations for atomic propositions"""
    count = len(valuations)
    message = bytearray(4+count)
    struct.pack_into("<i", message, 0, count)
    current = 4
    for value in valuations:
        struct.pack_into("B", message, current, value)
        current += 1
    connected_socket.send(message)

def handle_request(connected_socket, model):
    """Reads first 2 bytes from request to identify the request"""
    header = bytearray(2)
    connected_socket.recv_into(header)
    unpacked = struct.unpack("<cc", header)
    #print "Received " + str(unpacked)
    if unpacked[0] == b'\x01':
        if unpacked[1] == b'\x01':
            send_configurations(connected_socket, model, model[INITIAL_CONFIGURATIONS](model))

        elif unpacked[1] == b'\x02':
            configuration = receive_configuration(connected_socket, model)
            result = model[FIREABLE_TRANSITIONS_FROM](configuration, model)
            send_transitions(connected_socket, model, result)

        elif unpacked[1] == b'\x03':
            configuration = receive_configuration(connected_socket, model)
            transition = receive_transition(connected_socket, model)
            result = model[FIRE_TRANSITION](configuration, transition, model)
            send_configurations(connected_socket, model, result)

        elif unpacked[1] == b'\x04':
            propositions = receive_atomic_propositions(connected_socket)
            model[REGISTER_ATOMIC_PROPOSITIONS](propositions, model)

        elif unpacked[1] == b'\x05':
            configuration = receive_configuration(connected_socket, model)
            result = model[ATOMIC_PROPOSITION_VALUATIONS](configuration, model)
            send_valuations(connected_socket, result)

        else:
            print 'Unknown request'
        return True
    else:
        print "Received EOS"
        return False

def start_listening(server_socket, model):
    """Starts listening to server socket"""
    connected_socket, connected_from = server_socket.accept()
    print "Connected to " + str(connected_from)
    alive = handle_request(connected_socket, model)
    while alive:
        alive = handle_request(connected_socket, model)

def run(port, model):
    """Main function"""
    server_socket = create_server_socket(port)
    start_listening(server_socket, model)
    server_socket.close()
    print "Connection closed"
