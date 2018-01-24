import struct
import remote  
import sys
from main import main


######################
## Model to execute ##
######################

ATOMS = "atoms"

def decode_configuration(raw):
    value = struct.unpack("b", raw)
    return value[0]

def encode_configuration(value):
    raw = struct.pack("b", value)
    return raw

def initial_configurations(model):
    print "[Initial Configurations]"
    return [encode_configuration(0)]

def fireable_transitions_from(configuration, model):
    value = decode_configuration(configuration)
    print "[Fireable Transitions From '" + str(value) + "']"
    if value > 5:
        return [b'\x02']
    else:
        return [b'\x01']

def fire_transition(configuration, transition, model):
    value = decode_configuration(configuration)
    print "[Fire transition from '" + str(value) + "']"
    if transition == b'\x01':
        return [encode_configuration(value+1)]
    elif transition == b'\x02':
        return [encode_configuration(0)]
    else:
        return [configuration]

def register_atomic_proposition(propositions, model):
    print "Register"
    model[ATOMS] = propositions

def atomic_proposition_valuations(configuration, model):
    result = []
    for atom in model[ATOMS]:
        result.append(eval(atom, None, {"c": configuration}))
    return result

MODEL = {
    remote.CONF_SIZE: 1,
    remote.TRANSITION_SIZE: 1,
    remote.INITIAL_CONFIGURATIONS: initial_configurations,
    remote.FIREABLE_TRANSITIONS_FROM: fireable_transitions_from,
    remote.FIRE_TRANSITION: fire_transition,
    remote.REGISTER_ATOMIC_PROPOSITIONS: register_atomic_proposition,
    remote.ATOMIC_PROPOSITION_VALUATIONS: atomic_proposition_valuations
}

if __name__ == "__main__":
    main(sys.argv[1:], MODEL)
