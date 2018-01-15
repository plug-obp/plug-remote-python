import struct
import remote  

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
    if value > 100:
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
    remote.CONF_SIZE: 1,
    remote.TRANSITION_SIZE: 1,
    remote.INITIAL_CONFIGURATIONS: initial_configurations,
    remote.FIREABLE_TRANSITIONS_FROM: fireable_transitions_from,
    remote.FIRE_TRANSITION: fire_transition
}
