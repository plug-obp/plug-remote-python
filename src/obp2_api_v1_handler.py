import obp2_api_handler as api
import obp2_byte_array_module as bam
from obp2_io_helpers import Marshaller, Unmarshaller


class APIHandlerV1(api.ApiHandler):
    module: bam.ByteArrayLanguageModule

    def __init__(self, module, socket):
        super(APIHandlerV1, self).__init__(socket)
        if isinstance(module, bam.ByteArrayLanguageModule):
            self.module = module
        else:
            self.module = bam.ByteArrayLanguageModule(module)

    def handle_initial(self):
        configurations = self.module.transition_relation.initial()
        Marshaller.write_buffers(configurations, self.client_socket)

    def handle_actions(self):
        source = Unmarshaller.read_buffer(self.client_socket)
        actions = self.module.transition_relation.actions(source)
        Marshaller.write_buffers(actions, self.client_socket)

    def handle_execute(self):
        source = Unmarshaller.read_buffer(self.client_socket)
        action = Unmarshaller.read_buffer(self.client_socket)

        result = self.module.transition_relation.execute(source, action)
        # TODO: the future API should support <Payload, Target>*, now we have only Target* Payload
        targets = list(map(lambda f: f[0], result))
        Marshaller.write_buffers(targets, self.client_socket)

        payload = list(result)[0][1]
        Marshaller.write_buffer(payload, self.client_socket)

    def handle_register_atomic_propositions(self):
        propositions = Unmarshaller.read_string_array(self.client_socket)
        indices = self.module.atom_evaluator.register_atomic_propositions(propositions)
        Marshaller.write_int_array(indices, self.client_socket)

    def handle_atomic_proposition_valuations(self):
        source = Unmarshaller.read_buffer(self.client_socket)
        result = self.module.atom_evaluator.atomic_proposition_valuations(source)
        Marshaller.write_boolean_array(result, self.client_socket)

    def handle_extended_atomic_proposition_valuations(self):
        source = Unmarshaller.read_buffer(self.client_socket)
        action = Unmarshaller.read_buffer(self.client_socket)
        payload = Unmarshaller.read_buffer(self.client_socket)
        target = Unmarshaller.read_buffer(self.client_socket)

        result = self.module.atom_evaluator.extended_atomic_proposition_valuations(source, action, payload, target)
        Marshaller.write_boolean_array(result, self.client_socket)

    def handle_project_configuration(self):
        source = Unmarshaller.read_buffer(self.client_socket)
        tree_item = self.module.projector.project_configuration(source)
        Marshaller.write_int(1, self.client_socket)
        Marshaller.write_tree_item(tree_item, self.client_socket)

    def handle_project_action(self):
        action = Unmarshaller.read_buffer(self.client_socket)
        tree_item = self.module.projector.project_action(action)
        Marshaller.write_string(tree_item.name, self.client_socket)

    def handle_project_payload(self):
        action = Unmarshaller.read_buffer(self.client_socket)
        tree_item = self.module.projector.project_payload(action)
        Marshaller.write_tree_item(tree_item, self.client_socket)



