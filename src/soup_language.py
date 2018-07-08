import copy
from plug_interface import *


class BehaviorSoup:

    def __init__(self, environment, behaviors):
        self.environment = environment
        self.behaviors = behaviors
        for behavior in behaviors:
            behavior.soup = self


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


class BehaviorSoupTransitionRelation(AbstractTransitionRelation):

    def __init__(self, soup):
        self.soup = soup

    def initial_configurations(self):
        return {self.soup.environment.memory}

    def fireable_transitions_from(self, source):
        return set(filter(lambda beh: beh.is_enabled(source), self.soup.behaviors))

    def fire_one_transition(self, source, transition):
        target = copy.deepcopy(source)
        transition.execute(target)
        return {target}


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


class BehaviorSoupRuntimeView(AbstractRuntimeView):

    def __init__(self, soup):
        self.soup = soup

    def create_configuration_item(self, type_, name, icon = None, children = []):
        result = {}
        result['type'] = type_
        result['name'] = name
        result['icon'] = icon
        result['children'] = children
        return result

    def configuration_items(self, configuration) -> list:
        items = []
        self.soup.environment.memory = configuration
        for key in self.soup.environment:
            items.append(self.create_configuration_item("variable", key + " = " + str(self.soup.environment[key])))
        return items

    def fireable_transition_description(self, transition) -> str:
        return str(transition.name)


class BehaviorSoupAtomEvaluator(AbstractAtomEvaluator):
    propositions: list

    def __init__(self, soup):
        self.soup = soup

    def register_atomic_propositions(self, propositions) -> list:
        result = []
        self.propositions = propositions
        for ap in propositions:
            result.append(len(result))
        return result

    def atomic_proposition_valuations(self, configuration) -> list:
        result = []
        self.soup.environment.memory = configuration
        for ap in self.propositions:
            try:
                result.append(eval(ap,globals(), {'e' : self.soup.environment}))
            except:
                result.append(False)
        return result