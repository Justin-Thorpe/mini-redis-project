import asyncio
from src.client import Client

async def main():
    client = Client()
    await client.connect()

    while True:
        command = input("> ")

        if command.lower() == "exit":
            break

        parts = command.split()
        response = await client.execute(*parts)

        print(response)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())