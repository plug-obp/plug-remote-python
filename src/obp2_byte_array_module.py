import obp2_runtime_core as core


class ByteArrayTransitionRelation(core.OBP2TransitionRelation):
    operand: core.OBP2LanguageModule

    def __init__(self, operand):
        self.operand = operand

    # -> set<byte[]>
    def initial(self):
        marshaller = self.operand.marshaller
        tr = self.operand.transition_relation
        return list(map(marshaller.serialize_configuration, tr.initial()))

    # -> set<byte[]>
    def actions(self, source):
        marshaller = self.operand.marshaller
        the_configuration = marshaller.deserialize_configuration(source)
        tr = self.operand.transition_relation
        return list(map(marshaller.serialize_action, tr.actions(the_configuration)))

    # -> set<byte[]>
    def execute(self, source, action):
        marshaller = self.operand.marshaller
        the_configuration = marshaller.deserialize_configuration(source)
        the_action = marshaller.deserialize_action(action)
        tr = self.operand.transition_relation

        def mapper(fanout):
            return marshaller.serialize_configuration(fanout[0]), marshaller.serialize_payload(fanout[1])
        return list(map(mapper, tr.execute(the_configuration, the_action)))


class ByteArrayTreeProjector(core.OBP2TreeProjector):
    operand: core.OBP2LanguageModule

    def __init__(self, operand):
        self.operand = operand

    def project_configuration(self, configuration) -> core.TreeItem:
        marshaller = self.operand.marshaller
        the_configuration = marshaller.deserialize_configuration(configuration)
        projector = self.operand.projector
        return projector.project_configuration(the_configuration)

    def project_action(self, action) -> core.TreeItem:
        marshaller = self.operand.marshaller
        the_action = marshaller.deserialize_action(action)
        projector = self.operand.projector
        return projector.project_action(the_action)

    def project_payload(self, payload) -> core.TreeItem:
        marshaller = self.operand.marshaller
        the_payload = marshaller.deserialize_payload(payload)
        projector = self.operand.projector
        return projector.project_payload(the_payload)


class ByteArrayAtomEvaluator(core.OBP2AtomEvaluator):
    operand: core.OBP2LanguageModule

    def __init__(self, operand):
        self.operand = operand

    def register_atomic_propositions(self, propositions) -> list:
        evaluator = self.operand.atom_evaluator
        return evaluator.register_atomic_propositions(propositions)

    def atomic_proposition_valuations(self, configuration) -> list:
        marshaller = self.operand.marshaller
        the_configuration = marshaller.deserialize_configuration(configuration)
        evaluator = self.operand.atom_evaluator
        return evaluator.atomic_proposition_valuations(the_configuration)

    def extended_atomic_proposition_valuations(self, source, action, payload, target) -> list:
        marshaller = self.operand.marshaller
        the_source = marshaller.deserialize_configuration(source)
        the_action = marshaller.deserialize_action(action)
        the_payload= marshaller.deserialize_payload(payload)
        the_target = marshaller.deserialize_configuration(target)
        evaluator = self.operand.atom_evaluator
        return evaluator.extended_atomic_proposition_valuations(the_source, the_action, the_payload, the_target)


class ByteArrayMarshaller(core.OBP2Marshaller):
    operand: core.OBP2LanguageModule

    def __init__(self, operand):
        self.operand = operand

    def serialize_configuration(self, configuration) -> bytearray:
        return configuration

    def deserialize_configuration(self, bytes):
        return bytes

    def serialize_action(self, action) -> bytearray:
        return action

    def deserialize_action(self, bytes):
        return bytes

    def serialize_payload(self, payload) -> bytearray:
        return payload

    def deserialize_payload(self, bytes):
        return bytes


class ByteArrayLanguageModule(core.OBP2LanguageModule):
    operand: core.OBP2LanguageModule

    def __init__(self, operand):
        super().__init__(
            ByteArrayTransitionRelation(operand),
            ByteArrayTreeProjector(operand),
            ByteArrayAtomEvaluator(operand),
            ByteArrayMarshaller(operand)
        )



