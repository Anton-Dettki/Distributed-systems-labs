import asyncio

class storage: 
    def __init__(self, proxy): 
        self.proxy = proxy
        self._update_queue = asyncio.Queue()
        self._update_task_started = False
        self._update_task = None
        self._retry_delay = 1.0  # Retry delay in seconds

    async def put(self, message, sequenceNumber=None): 
        try:
            result = await self.proxy.put(message, sequenceNumber)
            # If successful, return result immediately
            if not (isinstance(result, dict) and result.get("RESULT") == "ERROR"):
                return result
            # If error, queue for retry
            await self._update_queue.put(("PUT", message, sequenceNumber))
            self._ensure_update_task()
            return result
        except Exception as e:
            # If exception, queue for retry
            print(f"PUT failed with exception, queueing for retry: {e}")
            await self._update_queue.put(("PUT", message, sequenceNumber))
            self._ensure_update_task()
            return {"RESULT": "ERROR"}
      
    async def modify(self, index, message, sequenceNumber=None): 
        try:
            result = await self.proxy.modify(index, message, sequenceNumber)
            if not (isinstance(result, dict) and result.get("RESULT") == "ERROR"):
                return result
            await self._update_queue.put(("MODIFY", index, message, sequenceNumber))
            self._ensure_update_task()
            return result
        except Exception as e:
            print(f"MODIFY failed with exception, queueing for retry: {e}")
            await self._update_queue.put(("MODIFY", index, message, sequenceNumber))
            self._ensure_update_task()
            return {"RESULT": "ERROR"}
        
    async def delete(self, index, sequenceNumber=None): 
        try:
            result = await self.proxy.delete(index, sequenceNumber)
            if not (isinstance(result, dict) and result.get("RESULT") == "ERROR"):
                return result
            await self._update_queue.put(("DELETE", index, sequenceNumber))
            self._ensure_update_task()
            return result
        except Exception as e:
            print(f"DELETE failed with exception, queueing for retry: {e}")
            await self._update_queue.put(("DELETE", index, sequenceNumber))
            self._ensure_update_task()
            return {"RESULT": "ERROR"}
            
    async def deleteAll(self, sequenceNumber=None): 
        try:
            result = await self.proxy.deleteAll(sequenceNumber)
            if not (isinstance(result, dict) and result.get("RESULT") == "ERROR"):
                return result
            await self._update_queue.put(("DELETEALL", sequenceNumber))
            self._ensure_update_task()
            return result
        except Exception as e:
            print(f"DELETEALL failed with exception, queueing for retry: {e}")
            await self._update_queue.put(("DELETEALL", sequenceNumber))
            self._ensure_update_task()
            return {"RESULT": "ERROR"}

    def _ensure_update_task(self):
        """Start the background update task if not already started."""
        if not self._update_task_started:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return
            self._update_task = loop.create_task(self._update_task_proc())
            self._update_task_started = True
    
    async def _update_task_proc(self):
        """Background coroutine that processes queued update operations with retry logic."""
        while True:
            item = await self._update_queue.get()
            if not item:
                continue
            
            # Process the operation with retry until successful
            success = False
            while not success:
                try:
                    result = await self._execute_operation(item)
                    # Check if operation was successful (not ERROR)
                    if isinstance(result, dict) and result.get("RESULT") == "ERROR":
                        print(f"Operation failed, retrying in {self._retry_delay}s: {item[0]}")
                        await asyncio.sleep(self._retry_delay)
                    else:
                        success = True
                        print(f"Operation successful: {item[0]}")
                except Exception as e:
                    print(f"Exception during operation, retrying in {self._retry_delay}s: {e}")
                    await asyncio.sleep(self._retry_delay)
    
    async def _execute_operation(self, item):
        """Execute a single operation from the queue."""
        operation = item[0]
        
        if operation == "PUT":
            _, message, sequenceNumber = item
            return await self.proxy.put(message, sequenceNumber)
        
        elif operation == "MODIFY":
            _, index, message, sequenceNumber = item
            return await self.proxy.modify(index, message, sequenceNumber)
        
        elif operation == "DELETE":
            _, index, sequenceNumber = item
            return await self.proxy.delete(index, sequenceNumber)
        
        elif operation == "DELETEALL":
            _, sequenceNumber = item
            return await self.proxy.deleteAll(sequenceNumber)
        
        return {"RESULT": "ERROR"}

    async def get(self, index): 
        return await self.proxy.get(index)
            
    async def getNum(self): 
        return await self.proxy.getNum()
        
    async def getBoard(self): 
        return await self.proxy.getBoard()
        
    async def acquire(self):
        return await self.proxy.acquire()
        
    async def release(self): 
        return await self.proxy.release() 
        
    async def areYouAlive(self):
        return await self.proxy.areYouAlive()
        
    async def election(self):
        return await self.proxy.election()
        
    async def setCoordinator(self, coordinatorID):
        return await self.proxy.setCoordinator(coordinatorID)
        
    async def getSequenceNumber(self):
        return await self.proxy.getSequenceNumber()

    async def close(self): 
        await self.proxy.close()