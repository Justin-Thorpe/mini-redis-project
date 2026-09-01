'''
Responsible for interpreting commands.

Validate command names
Validate argument counts
Call storage methods
Return results or errors
'''

import asyncio
from protocol import ProtocolHandler

class Client:
    def __init__(self,  host='127.0.0.1', port=6379):
        self._host = host
        self._port = port
        self._protocol = ProtocolHandler()
        self._reader = None
        self._writer = None

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)

    async def execute(self, *args):
        await self._protocol.write_response(self._writer, args)
        return await self._protocol.handle_request(self._writer)

    async def ping(self, key):
        return await self.execute('PING', key)

    async def get(self, key):
        return await self.execute('GET', key)

    async def set(self, key, value):
        return await self.execute('SET', key, value)
    
    async def delete(self, key):
        return await self.execute('DELETE', key)
    
    async def flush(self):
        return await self.execute('FLUSH')