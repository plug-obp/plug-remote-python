"""Imports"""
import struct
import remote

### Guard action model
VARIABLES = "variables"
BEHAVIOURS = "behaviours"
GUARD = "guard"
ACTION = "action"
ORIGINAL = "original"

def decode_configuration(original, raw):
    """Decode raw configuration to variables"""
    result = {}
    current = 0
    for name in original[VARIABLES].iterkeys():
        result[name] = struct.unpack_from("<i", raw, current)[0]
        current += 4
    return result

def encode_configuration(values):
    """Encode variables to raw configuration"""
    raw = bytearray(len(values)*4)
    current = 0
    for value in values.itervalues():
        struct.pack_into("<i", raw, current, value)
        current += 4
    return raw

def fireable_transitions_from(configuration, model):
    "Find fireable transitions"
    result = []
    original = model[ORIGINAL]
    behaviours = original[BEHAVIOURS]
    variables = decode_configuration(original, configuration)
    for name, behaviour in behaviours.iteritems():
        if behaviour[GUARD](variables):
            result.append(name)
    return result

def fire_transition(configuration, transition, model):
    "Fire transition"
    index = transition.decode("utf-8").strip("\x00")
    original = model[ORIGINAL]
    behaviours = original[BEHAVIOURS]
    variables = decode_configuration(original, configuration)
    behaviours[index][ACTION](variables)
    return [encode_configuration(variables)]

def init_model(variables = {}, behaviours = {}):
    return {
        VARIABLES: variables,
        BEHAVIOURS: behaviours
    }

def to_plug(model):
    """Transforms guard_action model to plug model"""
    transition_size = 0
    for name in model[BEHAVIOURS].iterkeys():
        transition_size = max(transition_size, len(name))

    return {
        ORIGINAL: model,
        remote.CONF_SIZE: len(model[VARIABLES]) * 4,
        remote.TRANSITION_SIZE: transition_size,
        remote.INITIAL_CONFIGURATIONS: lambda (model): [encode_configuration(model[ORIGINAL][VARIABLES])],
        remote.FIREABLE_TRANSITIONS_FROM: fireable_transitions_from,
        remote.FIRE_TRANSITION: fire_transition,
        remote.REGISTER_ATOMIC_PROPOSITIONS: None,
        remote.ATOMIC_PROPOSITION_VALUATIONS: None
    }
