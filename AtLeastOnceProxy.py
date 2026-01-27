import asyncio

class storage: 
    def __init__(self, proxy, timeout=3, max_retries=5): 
        self.proxy = proxy
        self.timeout = timeout  # Timeout in seconds
        self.max_retries = max_retries  # Maximum number of retry attempts
        self.sequence_number = 0  # Sequence number for non-idempotent operations

    async def _retry_with_timeout(self, operation, *args, **kwargs):
        """
        Execute an operation with timeout and retry logic.
        Tries up to max_retries times with timeout seconds per attempt.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                async with asyncio.timeout(self.timeout):
                    result = await operation(*args, **kwargs)
                    return result
            except asyncio.TimeoutError:
                print(f"Timeout on attempt {attempt}/{self.max_retries}")
                if attempt >= self.max_retries:
                    raise  # Re-raise on final attempt
            except Exception as e:
                print(f"Error on attempt {attempt}/{self.max_retries}: {e}")
                if attempt >= self.max_retries:
                    raise  # Re-raise on final attempt
        
        # Should not reach here, but just in case
        raise Exception("Max retries exceeded")

    async def put(self, message, sequenceNumber=None): 
        # put() is not idempotent - add sequence number if not provided
        if sequenceNumber is None:
            self.sequence_number += 1
            sequenceNumber = self.sequence_number
        return await self._retry_with_timeout(self.proxy.put, message, sequenceNumber)
      
    async def modify(self, index, message, sequenceNumber=None): 
        return await self._retry_with_timeout(self.proxy.modify, index, message, sequenceNumber)
        
    async def delete(self, index, sequenceNumber=None): 
        # delete() is not idempotent - add sequence number if not provided
        if sequenceNumber is None:
            self.sequence_number += 1
            sequenceNumber = self.sequence_number
        return await self._retry_with_timeout(self.proxy.delete, index, sequenceNumber)
            
    async def deleteAll(self, sequenceNumber=None): 
        return await self._retry_with_timeout(self.proxy.deleteAll, sequenceNumber)

    async def get(self, index): 
        return await self._retry_with_timeout(self.proxy.get, index)
            
    async def getNum(self): 
        return await self._retry_with_timeout(self.proxy.getNum)
        
    async def getBoard(self): 
        return await self._retry_with_timeout(self.proxy.getBoard)
        
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
        self.proxy.close()