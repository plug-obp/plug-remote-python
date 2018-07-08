from plug_interface import AbstractTransitionRelation


class BFS:
    close: set
    open: list
    transition_relation: AbstractTransitionRelation

    def __init__(self, transition_relation):
        self.open=[]
        self.close=set()
        self.transition_relation = transition_relation

    def initialize(self):
        self.open.extend(self.transition_relation.initial_configurations())
        self.close.update(self.open)

    def at_end(self) -> bool:
        return not self.open

    def exploration_step(self):
        source = self.open.pop()
        fireables = self.transition_relation.fireable_transitions_from(source)
        for fireable in fireables:
            targets = self.transition_relation.fire_one_transition(source, fireable)
            targets.difference_update(self.close)
            self.open.extend(targets)
            self.close.update(targets)

    def execute(self):
        self.initialize()
        while not self.at_end():
            self.exploration_step()
        print(self.close)
        print(len(self.close))