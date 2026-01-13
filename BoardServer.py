#!/usr/bin/env python

import asyncio
import json
import sys
import websockets
from websockets.asyncio.server import serve
from VectorClock import clock

# Storage in which the messages of the message board are stored.
storage = None
# Optional mutex object used for remote mutual exclusion
mutex_obj = None
leader_obj = None
# Vector clock for timestamping messages
vector_clock = None
# Optional sequencer object for generating sequence numbers
sequencer_obj = None

# Port number on which the server has to be started. 
port = -1 # Changed in function startServer


#########################################################
# Stub calling the methods on one storage object 
# depending on the type of message received.  
#########################################################
async def stub(request):
   command = request.get("COMMAND", "").upper()
   print(f"STUB received command: {command}")
   message = request.get("MESSAGE", "")
   index =  request.get("INDEX")
   id = request.get("MYID", -1)
   seq_num = request.get("SEQNUM")
   
   # Update vector clock if timestamp is present in request
   if vector_clock is not None and "TIME" in request:
       vector_clock.updateTime(request["TIME"])
   
   # Determine if this is a server-to-server or client-to-server request
   is_server_request = "TIME" in request
   
   try:
       if command == 'PUT':
           if seq_num is not None:
               result = await storage.put(message, id, seq_num)
           else:
               result = await storage.put(message, id)
           if is_server_request:
               return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return result

       elif command == 'GETBOARD':
           board = await storage.getBoard(id)
           if is_server_request:
               return {"RESULT": "OK", "BOARD": board, "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return board
       
       elif command == 'GET':
           result = await storage.get(index, id)
           if is_server_request:
               return {"RESULT": "OK", "MESSAGE": result, "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return result
       
       elif command == 'GETNUM':
           result = await storage.getNum(id)
           if is_server_request:
               return {"RESULT": "OK", "NUM": result, "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return result
       
       elif command == 'MODIFY':
           if seq_num is not None:
               await storage.modify(index, message, id, seq_num)
           else:
               await storage.modify(index, message, id)
           if is_server_request:
               return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return 'DONE'
       
       elif command == 'DELETE':
           if seq_num is not None:
               await storage.delete(index, id, seq_num)
           else:
               await storage.delete(index, id)
           if is_server_request:
               return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return 'DONE'
       
       elif command == 'DELETEALL':
           if seq_num is not None:
               await storage.deleteAll(id, seq_num)
           else:
               await storage.deleteAll(id)
           if is_server_request:
               return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return 'DONE'
       
       elif command == 'ACQUIRE':
           # Acquire the mutex if available
           if mutex_obj is None:
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           try:
               result = await mutex_obj.acquire()
               if is_server_request:
                   return {"RESULT": "OK" if result else "BUSY", "ACQUIRED": result, "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return result
           except Exception as e:
               print(f"Mutex acquire error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"

       elif command == 'RELEASE':
           # Release the mutex if available
           if mutex_obj is None:
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           try:
               await mutex_obj.release()
               if is_server_request:
                   return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return 'DONE'
           except Exception as e:
               print(f"Mutex release error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"

       elif command == 'AREYOUALIVE':
           # Simple health check - always returns YES
           if is_server_request:
               return {"RESULT": "OK", "ALIVE": "YES", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return "YES"

       elif command == 'ELECTION':
           # Call election method on leader election object
           if leader_obj is None:
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           try:
               result = await leader_obj.election()
               if is_server_request:
                   return {"RESULT": "OK", "RESPONSE": result, "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return result
           except Exception as e:
               print(f"Election error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"

       elif command == 'SETCOORDINATOR':
           # Call setCoordinator method on leader election object
           if leader_obj is None:
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           try:
               coordinatorID = request.get("COORDINATORID")
               if coordinatorID is None:
                   if is_server_request:
                       return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
                   else:
                       return "ERROR"
               await leader_obj.setCoordinator(coordinatorID)
               if is_server_request:
                   return {"RESULT": "OK", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return 'DONE'
           except Exception as e:
               print(f"SetCoordinator error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"

       elif command == 'GETSEQUENCENUMBER':
           # Get sequence number from sequencer object
           if sequencer_obj is None:
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           try:
               seq_num = await sequencer_obj.getSequenceNumber()
               if is_server_request:
                   return {"RESULT": "OK", "SEQNUM": seq_num, "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return seq_num
           except Exception as e:
               print(f"GetSequenceNumber error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"

       elif command == 'SYNCHRONIZE':
           # Synchronize with another server
           print(f"SYNCHRONIZE command received")
           other_server_id = request.get("OTHERSERVERID")
           print(f"  other_server_id: {other_server_id}, type: {type(other_server_id)}")
           print(f"  senderID: {id}")
           
           if other_server_id is None:
               print(f"  ERROR: other_server_id is None")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           
           # Check if storage has synchronize method
           if not hasattr(storage, 'synchronize'):
               print(f"  ERROR: storage object does not have synchronize method")
               print(f"  storage type: {type(storage)}")
               print(f"  storage methods: {dir(storage)}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
           
           try:
               print(f"  Calling storage.synchronize({other_server_id}, {id})")
               result = await storage.synchronize(other_server_id, id)
               print(f"  Result: {result}")
               if is_server_request:
                   return {"RESULT": result, "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return result
           except Exception as e:
               print(f"Synchronize error: {e}")
               if is_server_request:
                   return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
               else:
                   return "ERROR"
 
       else:
           if is_server_request:
               return {"RESULT": "UNKNOWN", "TIME": vector_clock.getTime() if vector_clock else []}
           else:
               return "A-ERR"
   except Exception as e:
       print(f"Exception in stub: {e}")
       import traceback
       traceback.print_exc()
       if is_server_request:
           return {"RESULT": "ERROR", "TIME": vector_clock.getTime() if vector_clock else []}
       else:
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
def startServer(portToUse, storageToUse, serverID=0, mutex=None, leader=None, vClock=None, sequencerParam=None): 
    global port
    global storage
    global myID, mutex_obj, leader_obj, vector_clock, sequencer_obj
    
    port = portToUse
    storage = storageToUse
    mutex_obj = mutex
    leader_obj = leader
    vector_clock = vClock
    sequencer_obj = sequencerParam
    
    asyncio.run(serverMain())
    