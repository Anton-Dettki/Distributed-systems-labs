#!/usr/bin/env python

import asyncio
import json
import sys
import websockets
from websockets.asyncio.server import serve

# Storage in which the messages of the message board are stored.
storage = None

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
def startServer(portToUse, storageToUse, serverID=0): 
    global port
    global storage
    global myID
    
    port = portToUse
    storage = storageToUse
    
    asyncio.run(serverMain())
    