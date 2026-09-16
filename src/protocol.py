'''
Responsible for converting between network bytes and Python values.

Read commands from the socket
Parse commands
Serialize responses
Handle invalid requests
'''

from collections import namedtuple

class CommandError(Exception): pass
class Disconnect(Exception): pass

Error = namedtuple('Error', ('message',))

class ProtocolHandler:
    def __init__(self):
        # First byte tells server how to categorize incoming data using dispatch table (from Redis serialization protocol)
        self.handlers = {
            '+': self.handle_simple_string,
            '-': self.handle_error,
            ':': self.handle_integer,
            '$': self.handle_string,
            '*': self.handle_array,
            '%': self.handle_dict,
            '~': self.handle_set,
            '#': self.handle_boolean,
            '_': self.handle_null
        }

    async def handle_request(self, reader):
        # Parse client commands
        first_byte = (await (reader.read(1))).decode()
        if not first_byte:
            raise Disconnect()
        return await self.handlers[first_byte](reader)

    async def handle_simple_string(self, reader):
        return (await reader.readline()).rstrip(b"\r\n").decode()

    async def handle_error(self, reader):
        return Error((await reader.readline()).rstrip(b"\r\n")).decode()

    async def handle_integer(self, reader):
        return int((await reader.readline()).rstrip(b'\r\n'))

    async def handle_string(self, reader):
        length = int((await reader.readline()).rstrip(b'\r\n'))

        if length == -1:
            return None

        data = await reader.readexactly(length + 2)
        return data[:-2].decode()

    async def handle_array(self, reader):
        num_items = int((await reader.readline()).rstrip(b'\r\n'))
        return [await self.handle_request(reader) for _ in range(num_items)]

    async def handle_set(self, reader):
        num_items = int((await reader.readline()).rstrip(b'\r\n'))
        return [await self.handle_request(reader) for _ in range(num_items)]

    async def handle_dict(self, reader):
        num_items = int((reader.readline()).rstrip(b'\r\n'))
        elements = [await self.handle_request(reader) for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))

    async def handle_boolean(self, reader):
        return bool((await reader.readline()).rstrip(b'\r\n'))

    async def handle_null(self, reader):
        await reader.readline()
        return None

    async def write_response(self, writer, data):
        await self._write(writer, data)

    async def _write(self, writer, data):
        if isinstance(data, str):
            data = data.encode()

        if isinstance(data, bytes):
            writer.write(
                f"${len(data)}\r\n".encode() + 
                data
                + b"\r\n"
                )

        elif isinstance(data, int):
            writer.write(f":{data}\r\n".encode())

        elif isinstance(data, Error):
            writer.write(f"-{data.message}\r\n".encode())

        elif isinstance(data, (list, tuple)):
            writer.write(f"*{len(data)}\r\n".encode())
            for item in data:
                await self._write(writer, item)

        elif isinstance(data, (set)):
            writer.write(f"~{len(data)}\r\n".encode())
            for item in data:
                await self._write(writer, item)

        elif isinstance(data, dict):
            writer.write(f"%{len(data)}\r\n".encode())
            for key in data:
                await self._write(writer, key)
                await self._write(writer, data[key])

        elif isinstance(data, bool):
            writer.write(f"#{data}\r\n".encode())

        elif data is None:
            writer.write(b"_-1\r\n")

        else:
            raise ValueError(f"Unrecognized Type: {type(data)}")

        await writer.drain()