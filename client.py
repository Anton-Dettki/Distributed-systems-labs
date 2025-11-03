import asyncio
from websockets.asyncio.client import connect
import sys

serverPort = int(sys.argv[1]) if len(sys.argv) > 1 else 10000


async def connectToServer():
    connection = await connect(f'ws://localhost:{serverPort}/')
    await connection.send('Ping')
    response = await connection.recv()    
    print(response)

    await connection.close()


if __name__ == "__main__":
    asyncio.run(connectToServer())
    
    

