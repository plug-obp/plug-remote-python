import socket
import struct


class ApiHandler:
    client_socket: socket

    def __init__(self, client_socket):
        self.client_socket = client_socket

    def listen(self):
        try:
            alive = self.handle_request()
            while alive:
                alive = self.handle_request()
        except Exception as excptn:
            print("error: {0}".format(excptn))
        except BaseException as bexcptn:
            print("error: {0}".format(bexcptn))
        finally:
            self.client_socket.close()

    def api(self) -> dict:
        return {
            1: self.handle_initial,
            2: self.handle_actions,
            3: self.handle_execute,
            4: self.handle_register_atomic_propositions,
            5: self.handle_atomic_proposition_valuations,
            6: self.handle_extended_atomic_proposition_valuations,
            10: self.handle_project_configuration,
            11: self.handle_project_action,
            12: self.handle_project_payload,
        }

    def handle_request(self):
        """Reads first 2 bytes from request to identify the request"""
        header = bytearray(2)
        self.client_socket.recv_into(header)
        unpacked = struct.unpack("<BB", header)
        # print(unpacked.__repr__())
        if unpacked[0] == 1:
            self.api().get(unpacked[1], "Unknown request: " + unpacked[1].__repr__())()
            return True
        else:
            print("Received EOS")
            return False

    def handle_initial(self):
        pass

    def handle_actions(self):
        pass

    def handle_execute(self):
        pass

    def handle_register_atomic_propositions(self):
        pass

    def handle_atomic_proposition_valuations(self):
        pass

    def handle_extended_atomic_proposition_valuations(self):
        pass

    def handle_project_configuration(self):
        pass

    def handle_project_action(self):
        pass

    def handle_project_payload(self):
        pass
