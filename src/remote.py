"""Import sockets"""
import socket
import struct

CONF_SIZE = "conf_size"
TRANSITION_SIZE = "transition_size"
INITIAL_CONFIGURATIONS = "initial_configurations"
FIREABLE_TRANSITIONS_FROM = "fireable_transitions_from"
FIRE_TRANSITION = "fire_transition"

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


def handle_request(connected_socket, model):
    """Reads first 2 bytes from request to identify the request"""
    header = bytearray(2)
    connected_socket.recv_into(header)
    unpacked = struct.unpack("<cc", header)
    print "Received " + str(unpacked)
    if unpacked[0] == b'\x01':
        if unpacked[1] == b'\x01':
            send_configurations(connected_socket, model, model[INITIAL_CONFIGURATIONS]())

        elif unpacked[1] == b'\x02':
            configuration = receive_configuration(connected_socket, model)
            result = model[FIREABLE_TRANSITIONS_FROM](configuration)
            send_transitions(connected_socket, model, result)

        elif unpacked[1] == b'\x03':
            configuration = receive_configuration(connected_socket, model)
            transition = receive_transition(connected_socket, model)
            result = model[FIRE_TRANSITION](configuration, transition)
            print "Next configurations are " + str(result)
            send_configurations(connected_socket, model, result)

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


######################
## Model to execute ##
######################

def decode_configuration(raw):
    value = struct.unpack("b", raw)
    return value[0]

def encode_configuration(value):
    raw = struct.pack("b", value)
    return raw

def initial_configurations():
    print "[Initial Configurations]"
    return [encode_configuration(0)]

def fireable_transitions_from(configuration):
    value = decode_configuration(configuration)
    print "[Fireable Transitions From '" + str(value) + "']"
    if value > 10:
        return [b'\x02']
    else:
        return [b'\x01']

def fire_transition(configuration, transition):
    value = decode_configuration(configuration)
    print "[Fire transition from '" + str(value) + "']"
    if transition == b'\x01':
        return [encode_configuration(value+1)]
    elif transition == b'\x02':
        return [encode_configuration(0)]
    else:
        return [configuration]

MODEL = {
    CONF_SIZE: 1,
    TRANSITION_SIZE: 1,
    INITIAL_CONFIGURATIONS: initial_configurations,
    FIREABLE_TRANSITIONS_FROM: fireable_transitions_from,
    FIRE_TRANSITION: fire_transition
}

#################
## Start model ##
#################
run(1234, MODEL)
