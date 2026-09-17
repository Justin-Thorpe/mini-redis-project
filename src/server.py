'''
Responsible for networking and coordinating the other components.

Create TCP socket
Bind to ip and an available port
Listen for connections
Accept a client
Read request
Parse request
Execute command
Send response
Continue accepting commands
'''

import asyncio

from src.protocol import ProtocolHandler, Disconnect, CommandError, Error

class Server:
    def __init__(self, host="127.0.0.1", port=6379):
        self._host = host
        self._port = port
        self._server = None
        self._protocol = ProtocolHandler()
        self._kv = {}
        self._commands = self.get_commands()

    async def handle_connection(self, reader, writer):
        try:
            while True:
                try:
                    data = await self._protocol.handle_request(reader)
                except Disconnect:
                    break

                try:
                    resp = self.get_response(data)
                except CommandError as exc:
                    resp = Error(exc.args[0])

                await self._protocol.write_response(writer, resp)
                
        except (
            ConnectionResetError,
            BrokenPipeError,
            asyncio.IncompleteReadError
        ):
            pass

        finally:
            writer.close()
            await writer.wait_closed()

    def get_commands(self):
        return {
            "PING": self.ping,
            "GET": self.get,
            "SET": self.set,
            "DEL": self.delete,
            "FLUSH": self.flush
        }

    def get_response(self, data):
        if not data:
            raise CommandError("Empty command")
        
        if not isinstance(data, list):
            data = data.split()

        command = data[0].upper()
        if command not in self._commands:
            raise CommandError(f"Unrecognizd Command: {command}")

        try:
            return self._commands[command](*data[1:])
        except TypeError:
            raise CommandError(f"Wrong number of args for {command}")

    def ping(self):
        return "PONG"

    def get(self, key):
        return self._kv.get(key)

    def set(self, key, value):
        self._kv[key] = value
        return 1

    def delete(self, key):
        if key in self._kv:
            del self._kv[key]
            return 1
        return 0

    def flush(self):
        kvlen = len(self._kv)
        self._kv.clear()
        return kvlen

    async def run(self):
        self._server = await asyncio.start_server(self.handle_connection, self._host, self._port)
        async with self._server:
            await self._server.serve_forever()
