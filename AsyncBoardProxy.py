# Information on the websocket-client is available at 
# https://websocket-client.readthedocs.io/en/latest/

import asyncio
import json
from websockets.asyncio import client
from VectorClock import clock

class storage: 
    def __init__(self, port, myId, vectorClock=None, websocketconnect=client.connect): 
        self.port = port
        self.myId = myId
        self.websocket = None
        self.vectorClock = vectorClock  # Vector clock object for timestamps
        self.websocketconnect = websocketconnect  # Configurable connect function
       
    async def doOperation(self, request):
       print("doing operations")
       request["MYID"] = self.myId
       
       # Add timestamp to request if vector clock is available
       if self.vectorClock is not None:
           request["TIME"] = self.vectorClock.getTime()
       
       try:
           if self.websocket is None:
               self.websocket = await self.websocketconnect(f"ws://localhost:{self.port}")
           await self.websocket.send(json.dumps(request,))
           res = await self.websocket.recv()
           response = json.loads(res)
           
           # Update vector clock from response if available
           if self.vectorClock is not None and isinstance(response, dict) and "TIME" in response:
               self.vectorClock.updateTime(response["TIME"])
           
           return response
       except Exception as e:
           print(f"Conn error: {e}")
           try:
               self.websocket = await self.websocketconnect(f"ws://localhost:{self.port}")
               await self.websocket.send(json.dumps(request))
               res = await self.websocket.recv()
               response = json.loads(res)
               
               # Update vector clock from response if available
               if self.vectorClock is not None and isinstance(response, dict) and "TIME" in response:
                   self.vectorClock.updateTime(response["TIME"])
               
               return response
           except Exception as retry_e:
               print(f"Retry conn error: {retry_e}")
               return {"RESULT": "ERROR"}
           
    async def put(self, message, sequenceNumber=None): 
        req = {"COMMAND": "PUT", "MESSAGE": message}
        if sequenceNumber is not None:
            req["SEQNUM"] = sequenceNumber
        return await self.doOperation(req)
       
    async def get(self, index):
        req = {"COMMAND": "GET", "INDEX": index}
        return await self.doOperation(req)

    async def getNum(self): 
        req = {"COMMAND": "GETNUM"}
        return await  self.doOperation(req)
        
    async def getBoard(self): 
        req = {"COMMAND": "GETBOARD"}
        return await self.doOperation(req)
        
    async def modify(self, index, message, sequenceNumber=None): 
        req = {"COMMAND": "MODIFY", "INDEX": index, "MESSAGE": message}
        if sequenceNumber is not None:
            req["SEQNUM"] = sequenceNumber
        return await self.doOperation(req)
        
    async def delete(self, index, sequenceNumber=None): 
        req = {"COMMAND": "DELETE", "INDEX": index}
        if sequenceNumber is not None:
            req["SEQNUM"] = sequenceNumber
        return await self.doOperation(req)

    async def deleteAll(self, sequenceNumber=None): 
        req = {"COMMAND": "DELETEALL"}
        if sequenceNumber is not None:
            req["SEQNUM"] = sequenceNumber
        return await self.doOperation(req)
        
    async def close(self): 
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def acquire(self):
        """Request acquiring the remote mutex. Returns True/False or "ERROR"."""
        req = {"COMMAND": "ACQUIRE"}
        return await self.doOperation(req)

    async def release(self):
        """Request releasing the remote mutex. Returns result or "ERROR"."""
        req = {"COMMAND": "RELEASE"}
        return await self.doOperation(req)

    async def areYouAlive(self):
        """Check if the remote server is alive. Returns "YES" or "ERROR"."""
        req = {"COMMAND": "AREYOUALIVE"}
        return await self.doOperation(req)

    async def getSequenceNumber(self):
        """Request a sequence number from the server. Returns sequence number or "ERROR"."""
        req = {"COMMAND": "GETSEQUENCENUMBER"}
        return await self.doOperation(req)

    async def election(self):
        """Start election process on the remote server. Returns response or "ERROR"."""
        req = {"COMMAND": "ELECTION"}
        return await self.doOperation(req)

    async def setCoordinator(self, coordinatorID):
        """Set the coordinator on the remote server. Returns response or "ERROR"."""
        req = {"COMMAND": "SETCOORDINATOR", "COORDINATORID": coordinatorID}
        return await self.doOperation(req)
        