#!/usr/bin/env python

import asyncio
import json
import sys
import websockets
from websockets.asyncio.server import serve

# Storage in which the messages of the message board are stored.
storage = None
# Optional mutex object used for remote mutual exclusion
mutex_obj = None
leader_obj = None

# Port number on which the server has to be started. 
port = -1 # Changed in function startServer


#########################################################
# Stub calling the methods on one storage object 
# depending on the type of message received.  
#########################################################
async def stub(request):
   command = request.get("COMMAND", "").upper()
   message = request.get("MESSAGE", "")
   index =  request.get("INDEX")
   id = request.get("MYID", -1)
   
   try:
       if command == 'PUT':
           result = await storage.put(message, id)
           return result

       elif command == 'GETBOARD':
           board = await storage.getBoard(id)
           return board
       
       elif command == 'GET':
           result = await storage.get(index, id)
           return result
       
       elif command == 'GETNUM':
           result = await storage.getNum(id)
           return result
       
       elif command == 'MODIFY':
           await storage.modify(index, message, id)
           return 'DONE'
       
       elif command == 'DELETE':
           await storage.delete(index, id)
           return 'DONE'
       
       elif command == 'DELETEALL':
           await storage.deleteAll(id)
           return 'DONE'
       
       elif command == 'ACQUIRE':
           # Acquire the mutex if available
           if mutex_obj is None:
               return "ERROR"
           try:
               result = await mutex_obj.acquire()
               return result
           except Exception as e:
               print(f"Mutex acquire error: {e}")
               return "ERROR"

       elif command == 'RELEASE':
           # Release the mutex if available
           if mutex_obj is None:
               return "ERROR"
           try:
               await mutex_obj.release()
               return 'DONE'
           except Exception as e:
               print(f"Mutex release error: {e}")
               return "ERROR"

       elif command == 'AREYOUALIVE':
           # Simple health check - always returns YES
           return "YES"

       elif command == 'ELECTION':
           # Call election method on leader election object
           if leader_obj is None:
               return "ERROR"
           try:
               result = await leader_obj.election()
               return result
           except Exception as e:
               print(f"Election error: {e}")
               return "ERROR"

       elif command == 'SETCOORDINATOR':
           # Call setCoordinator method on leader election object
           if leader_obj is None:
               return "ERROR"
           try:
               coordinatorID = request.get("COORDINATORID")
               if coordinatorID is None:
                   return "ERROR"
               await leader_obj.setCoordinator(coordinatorID)
               return 'DONE'
           except Exception as e:
               print(f"SetCoordinator error: {e}")
               return "ERROR"
 
       else:
           return "A-ERR"
   except Exception as e:
       print(e)
       return "B-ERR"

#########################################################
# Handler for performing server tasks of one client connection
#########################################################
async def handler(websocket):
    async for msg in websocket:
        try:
            request = json.loads(msg)
            response = await stub(request)
            await websocket.send(json.dumps(response))
        except Exception as e:
            await websocket.send(json.dumps(f"ERROR: {str(e)}"))


#########################################################
# Code for starting the server 
#########################################################
async def serverMain():          
    async with websockets.serve(handler, "localhost", port):
        print(f"BoardServer running on ws://localhost:{port}")
        await asyncio.Future() 

# Called by the main module to start the server
def startServer(portToUse, storageToUse, serverID=0, mutex=None, leader=None): 
    global port
    global storage
    global myID, mutex_obj, leader_obj
    
    port = portToUse
    storage = storageToUse
    mutex_obj = mutex
    leader_obj = leader
    
    asyncio.run(serverMain())
    