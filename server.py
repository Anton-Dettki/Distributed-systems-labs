import sys
import asyncio
import logging

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

serverPort = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
secondPort =  int(sys.argv[2]) if len(sys.argv) > 2 else None

logging.basicConfig(
format= "%(asctime)s %(message)s",
level=logging.DEBUG,
)

async def handler(websocket):
    async for message in websocket:
        if(secondPort):
            print('Opening second server connection')
            connection = await connect(f'ws://localhost:{secondPort}/')
            await connection.send('Ping')
            response = await connection.recv()    
            print(response)
            await connection.close()
            print('Closing second server connection')
        await websocket.send("Pong")

async def main():
    async with serve(handler, "localhost", serverPort):
        print('Server running on port ', serverPort)
        await asyncio.Future()

asyncio.run(main())
