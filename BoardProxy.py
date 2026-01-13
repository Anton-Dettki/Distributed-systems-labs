# Information on the websocket-client is available at 
# https://websocket-client.readthedocs.io/en/latest/

import asyncio
import json
from websockets.asyncio.client import connect

class storage: 
    def __init__(self, port): 
        self.port = port
       
    async def doOperation(self, request):
       print("doing operations")
       try:
           async with connect(f"ws://localhost:{self.port}") as websocket:
               await websocket.send(json.dumps(request))
               res = await websocket.recv()
               return json.loads(res)
       except Exception as e:
           print(f"Conn error: {e}")
           return "ERROR"
           
    def put(self, message): 
        req = {"COMMAND": "PUT", "MESSAGE": message}
        return asyncio.run(self.doOperation(req))
       
    def get(self, index):
        req = {"COMMAND": "GET", "INDEX": index}
        return asyncio.run(self.doOperation(req))

    def getNum(self): 
        req = {"COMMAND": "GETNUM"}
        return asyncio.run(self.doOperation(req))
        
    def getBoard(self): 
        req = {"COMMAND": "GETBOARD"}
        return asyncio.run(self.doOperation(req))
        
    def modify(self, index, message): 
        req = {"COMMAND": "MODIFY", "INDEX": index, "MESSAGE": message}
        return asyncio.run(self.doOperation(req))
        
    def delete(self, index): 
        req = {"COMMAND": "DELETE", "INDEX": index}
        return asyncio.run(self.doOperation(req))

    def deleteAll(self): 
        req = {"COMMAND": "DELETEALL"}
        return asyncio.run(self.doOperation(req))
    
    def synchronize(self, otherServerId):
        req = {"COMMAND": "SYNCHRONIZE", "OTHERSERVERID": otherServerId}
        return asyncio.run(self.doOperation(req))
        
    def close(self): 
        pass
        