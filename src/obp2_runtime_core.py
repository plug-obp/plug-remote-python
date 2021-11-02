from abc import abstractmethod


class OBP2LanguageService:
    module: object


class OBP2TransitionRelation(OBP2LanguageService):

    # (initial : set C)
    @abstractmethod
    def initial(self):
        pass

    # (actions : C → set A)
    @abstractmethod
    def actions(self, source):
        pass

    # (execute : C → A → set CxP)
    @abstractmethod
    def execute(self, source, action):
        pass


class TreeItem:
    name: str
    children: list

    def __init__(self, name, children=None):
        self.name = name
        self.children = children

    def __str__(self):
        r = "" + self.name + " ["
        for child in self.children:
            r += str(child)
        r += "]"
        return r


class OBP2TreeProjector(OBP2LanguageService):

    @abstractmethod
    def project_configuration(self, configuration) -> TreeItem:
        pass

    @abstractmethod
    def project_action(self, action) -> TreeItem:
        pass

    @abstractmethod
    def project_payload(self, payload) -> TreeItem:
        pass


class OBP2AtomEvaluator(OBP2LanguageService):

    @abstractmethod
    def register_atomic_propositions(self, propositions) -> list:
        pass

    @abstractmethod
    def atomic_proposition_valuations(self, configuration) -> list:
        pass

    @abstractmethod
    def extended_atomic_proposition_valuations(self, source, action, payload, target) -> list:
        pass


class OBP2Marshaller(OBP2LanguageService):

    @abstractmethod
    def serialize_configuration(self, configuration) -> bytes:
        pass

    @abstractmethod
    def deserialize_configuration(self, bytes):
        pass

    @abstractmethod
    def serialize_action(self, action) -> bytes:
        pass

    @abstractmethod
    def deserialize_action(self, bytes):
        pass

    @abstractmethod
    def serialize_payload(self, payload) -> bytes:
        pass

    @abstractmethod
    def deserialize_payload(self, bytes):
        pass


class OBP2LanguageModule:
    transition_relation: OBP2TransitionRelation
    projector: OBP2TreeProjector
    atom_evaluator: OBP2AtomEvaluator
    marshaller: OBP2Marshaller

    def __init__(self, transition_relation, projector, atom_evaluator, marshaller):
        self.transition_relation = transition_relation
        self.transition_relation.module = self
        self.projector = projector
        self.projector.module = self
        self.atom_evaluator = atom_evaluator
        self.atom_evaluator.module = self
        self.marshaller = marshaller
        self.marshaller.module = self

