import copy
import pickle
import threading
from obp2_runtime_core import *


class BehaviorSoup:

    def __init__(self, environment, behaviors):
        self.environment = environment
        self.behaviors = behaviors
        for behavior in behaviors:
            behavior.soup = self
        self.initial = environment.memory


class Behavior:
    soup: BehaviorSoup

    def __init__(self, guard, action, name=""):
        self.guard = guard
        self.action = action
        self.name = name

    def is_enabled(self, memory):
        self.soup.environment.memory = memory
        return self.guard(self.soup.environment)

    def execute(self, memory):
        self.soup.environment.memory = memory
        self.action(self.soup.environment)
        return 'payload[' + self.name + ']'


class Memory:
    data: list

    def __init__(self, initial):
        self.data = initial

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __hash__(self):
        result = 1
        for i in self.data:
            result = hash(int(31 * result + i.__hash__()))
        return result

    def __eq__(self, other):
        if isinstance(other, Memory):
            return self.data == other.data

    def __repr__(self):
        return self.data.__repr__()


class Environment:
    memory: Memory
    symbols: dict

    def __init__(self, symbols, initial):
        self.memory = Memory(initial)
        self.symbols = symbols

    def __getitem__(self, item):
        idx = self.symbols.get(item)
        if idx is None:
            return None
        return self.memory[idx]

    def __setitem__(self, key, value):
        idx = self.symbols.get(key)
        self.memory[idx] = value

    def __repr__(self):
        return dict(map(lambda item: (item[0], self.memory[item[1]]), self.symbols.items())).__repr__()

    def __iter__(self):
        return iter(self.symbols.keys())

    def __getattr__(self, item):
        return self[item]


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class BehaviorSoupTransitionRelation(OBP2TransitionRelation):

    def __init__(self, soup):
        self.soup = soup

    @synchronized
    def initial(self):
        return {self.soup.initial}

    @synchronized
    def actions(self, source):
        return set(
            map(
                lambda t: self.soup.behaviors.index(t),
                filter(
                    lambda t: t.is_enabled(source),
                    self.soup.behaviors)))

    @synchronized
    def execute(self, source, transition):
        target = copy.deepcopy(source)
        payload = self.soup.behaviors[transition].execute(target)
        result = {(target, payload)}
        return result


class BehaviorSoupProjector(OBP2TreeProjector):

    def __init__(self, soup):
        self.soup = soup

    @synchronized
    def project_configuration(self, configuration) -> TreeItem:
        children = []
        self.soup.environment.memory = configuration
        for key in self.soup.environment:
            children.append(TreeItem(key + " = " + str(self.soup.environment[key])))
        return TreeItem("soup", children)

    @synchronized
    def project_action(self, action) -> TreeItem:
        return TreeItem(str(self.soup.behaviors[action].name))

    @synchronized
    def project_payload(self, payload) -> TreeItem:
        return TreeItem(str(payload))


class BehaviorSoupAtomEvaluator(OBP2AtomEvaluator):
    propositions: list
    source_env: Environment
    target_env: Environment

    def __init__(self, soup):
        self.soup = soup
        self.source_env = Environment(self.soup.environment.symbols, self.soup.environment.memory)
        self.target_env = Environment(self.soup.environment.symbols, self.soup.environment.memory)
        self.propositions = []

    @synchronized
    def register_atomic_propositions(self, propositions) -> list:
        result = []
        self.propositions = propositions
        for ap in self.propositions:
            result.append(len(result))
        return result

    @synchronized
    def atomic_proposition_valuations(self, configuration) -> list:
        result = []
        self.soup.environment.memory = configuration
        for ap in self.propositions:
            try:
                result.append(eval(ap, globals(), {'s': self.soup.environment}))
            except:
                result.append(False)
        return result

    @synchronized
    def extended_atomic_proposition_valuations(self, source, action, payload, target)-> list:
        result = []

        self.source_env.memory = source
        self.target_env.memory = target

        for ap in self.propositions:
            try:
                result.append(
                    eval(
                        ap,
                        globals(), {
                            's': self.source_env,
                            'a': self.soup.behaviors[action],
                            'p': payload,
                            't': self.target_env}))
            except:
                result.append(False)
        return result


class BehaviorSoupMarshaller(OBP2Marshaller):

    def serialize_configuration(self, configuration) -> bytes:
        return pickle.dumps(configuration)

    def deserialize_configuration(self, data):
        return pickle.loads(data)

    def serialize_action(self, action) -> bytes:
        return pickle.dumps(action)

    def deserialize_action(self, data):
        return pickle.loads(data)

    def serialize_payload(self, payload) -> bytes:
        return pickle.dumps(payload)

    def deserialize_payload(self, data):
        return pickle.loads(data)


def soup_language_module(soup):
    return OBP2LanguageModule(
        BehaviorSoupTransitionRelation(soup),
        BehaviorSoupProjector(soup),
        BehaviorSoupAtomEvaluator(soup),
        BehaviorSoupMarshaller()
    )