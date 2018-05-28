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

CONFIGURATION_ITEMS = "configuration_items"
FIREABLE_TRANSITION_DESCRIPTION = "fireable_transition_description"

def create_configuration_item(type_, name, icon = None, children = []):
    result = {}
    result['type'] = type_
    result['name'] = name
    result['icon'] = icon
    result['children'] = children
    return result

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

def send_ints(connected_socket, ints):
    """Sends an array of integers"""
    count = len(ints)
    message = bytearray(4+count*4)
    struct.pack_into("<i", message, 0, count)
    current = 4
    for value in ints:
        struct.pack_into("<i", message, current, value)
        current += 4
    connected_socket.send(message)

def send_valuations(connected_socket, valuations):
    """Sends valuations for atomic propositions"""
    count = len(valuations)
    message = bytearray(4+count)
    struct.pack_into("<i", message, 0, count)
    current = 4
    for value in valuations:
        try:
            struct.pack_into("B", message, current, value)
        except:
            struct.pack_into("B", message, current, False)
        current += 1
    connected_socket.send(message)

def send_string(connected_socket, string):
    """Sends a string in UTF-8"""
    if (string == None):
        data = bytearray(4)
        struct.pack_into("<i", data, 0, -1)
        connected_socket.send(data)
    else:
        raw = string.encode("utf-8")
        raw_count = len(raw)
        data = bytearray(4)
        struct.pack_into("<i", data, 0, raw_count)
        connected_socket.send(data)
        connected_socket.send(raw)

def send_configuration_item(connected_socket, item):
    """Sends one configuration item"""
    send_string(connected_socket, item.get("type", ""))
    send_string(connected_socket, item.get("name", ""))
    send_string(connected_socket, item.get("icon", ""))

    children = item.get("children", [])
    send_configuration_items(connected_socket, children)
    
def send_configuration_items(connected_socket, items):
    """Sends configuration items"""
    message = bytearray(4)
    struct.pack_into("<i", message, 0, len(items))
    connected_socket.send(message)
    for child in items:
        send_configuration_item(connected_socket, child)

def handle_request(connected_socket, model):
    """Reads first 2 bytes from request to identify the request"""
    header = bytearray(2)
    connected_socket.recv_into(header)
    unpacked = struct.unpack("<BB", header)
    #print "Received " + str(unpacked)
    if unpacked[0] == 1:
        if unpacked[1] == 1:
            send_configurations(connected_socket, model, model[INITIAL_CONFIGURATIONS](model))

        elif unpacked[1] == 2:
            configuration = receive_configuration(connected_socket, model)
            result = model[FIREABLE_TRANSITIONS_FROM](configuration, model)
            send_transitions(connected_socket, model, result)

        elif unpacked[1] == 3:
            configuration = receive_configuration(connected_socket, model)
            transition = receive_transition(connected_socket, model)
            result = model[FIRE_TRANSITION](configuration, transition, model)
            send_configurations(connected_socket, model, result)

        elif unpacked[1] == 4:
            propositions = receive_atomic_propositions(connected_socket)
            result = model.get(REGISTER_ATOMIC_PROPOSITIONS, lambda ps, m: [])(propositions, model)
            send_ints(connected_socket, result)

        elif unpacked[1] == 5:
            configuration = receive_configuration(connected_socket, model)
            result = model.get(ATOMIC_PROPOSITION_VALUATIONS, lambda c, m: [])(configuration, model)
            send_valuations(connected_socket, result)

        elif unpacked[1] == 10:
            configuration = receive_configuration(connected_socket, model)
            result = model.get(CONFIGURATION_ITEMS, lambda c,m: [])(configuration, model)
            send_configuration_items(connected_socket, result)

        elif unpacked[1] == 11:
            transition = receive_transition(connected_socket, model)
            result = model.get(FIREABLE_TRANSITION_DESCRIPTION, lambda t,m: str(t))(transition, model)
            send_string(connected_socket, result)

        else:
            print 'Unknown request: ' + unpacked[1]
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
