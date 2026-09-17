import asyncio
from src.protocol import CommandError
from src.client import Client

async def main():
    client = Client()

    try:
        await client.connect()
    except ConnectionRefusedError:
        print("Could not connect to server")
        return

    while True:
        command = input("> ")

        if command.lower() == "exit":
            break
        
        parts = command.split()

        try:
            response = await client.execute(*parts)
            print(response)

        except CommandError as error:
            print(error)
    

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())