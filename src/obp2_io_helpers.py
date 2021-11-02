import struct


class Marshaller:
    @staticmethod
    def write_int(value, stream):
        message = bytearray(4)
        struct.pack_into("<i", message, 0, value)
        stream.send(message)

    @staticmethod
    def write_buffers(buffers, stream):
        Marshaller.write_int(len(buffers), stream)
        for buffer in buffers:
            Marshaller.write_buffer(buffer, stream)

    @staticmethod
    def write_buffer(buffer, stream):
        Marshaller.write_int(len(buffer), stream)
        stream.send(buffer)

    @staticmethod
    def write_int_array(array, stream):
        length = len(array)
        message = bytearray(4+length*4)
        struct.pack_into("<i", message, 0, length)
        current = 4
        for value in array:
            struct.pack_into("<i", message, current, value)
            current += 4
        stream.send(message)

    @staticmethod
    def write_boolean_array(array, stream):
        length = len(array)
        message = bytearray(4 + length)
        struct.pack_into("<i", message, 0, length)
        current = 4
        for value in array:
            try:
                struct.pack_into("B", message, current, value)
            except:
                struct.pack_into("B", message, current, False)
            current += 1
        stream.send(message)

    @staticmethod
    def write_string(string, stream):
        if string is None:
            Marshaller.write_int(-1, stream)
        else:
            raw = string.encode("utf-8")
            Marshaller.write_int(len(raw), stream)
            stream.send(raw)

    @staticmethod
    def write_tree_item(tree_item, stream):
        Marshaller.write_string("", stream)
        Marshaller.write_string(tree_item.name, stream)
        Marshaller.write_string("", stream)

        children = tree_item.children if (tree_item.children is not None) else []
        Marshaller.write_int(len(children), stream)
        for child in children:
            Marshaller.write_tree_item(child, stream)


class Unmarshaller:
    @staticmethod
    def read_int(stream) -> int:
        return int(struct.unpack("<i", stream.recv(4))[0])

    @staticmethod
    def read_buffer(stream) -> bytearray:
        size = Unmarshaller.read_int(stream)
        return stream.recv(size)

    @staticmethod
    def read_string(stream):
        size = Unmarshaller.read_int(stream)
        raw_string = bytearray(size)
        stream.recv_into(raw_string)
        return raw_string.decode("utf-8")

    @staticmethod
    def read_string_array(stream):
        size = Unmarshaller.read_int(stream)
        array = []
        for _ in range(0, size):
            array.append(Unmarshaller.read_string(stream))
        return array