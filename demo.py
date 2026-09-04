import asyncio
from src.client import Client

async def main():
    client = Client()
    await client.connect()

    print(await client.ping())

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())