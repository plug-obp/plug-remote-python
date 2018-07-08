from abc import abstractmethod


class AbstractTransitionRelation:
    module: object

    @abstractmethod
    def initial_configurations(self) -> set:
        pass

    @abstractmethod
    def fireable_transitions_from(self, source) -> set:
        pass

    @abstractmethod
    def fire_one_transition(self, source, transition) -> set:
        pass


class AbstractRuntimeView:
    module: object

    @abstractmethod
    def configuration_items(self, configuration) -> list:
        pass

    @abstractmethod
    def fireable_transition_description(self, transition) -> str:
        pass


class AbstractAtomEvaluator:
    module: object

    @abstractmethod
    def register_atomic_propositions(self, propositions) -> list:
        pass

    @abstractmethod
    def atomic_proposition_valuations(self, configuration) -> list:
        pass


class LanguageModule:
    transition_relation: AbstractTransitionRelation
    runtime_view: AbstractRuntimeView
    atom_evaluator: AbstractAtomEvaluator

    def __init__(self, transition_relation, runtime_view, atom_evaluator):
        self.transition_relation = transition_relation
        self.transition_relation.module = self
        self.runtime_view = runtime_view
        self.runtime_view.module = self
        self.atom_evaluator = atom_evaluator
        self.atom_evaluator.module = self