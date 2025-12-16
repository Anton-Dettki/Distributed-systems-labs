import asyncio
from VectorClock import totalOrder

class storage:
    def __init__(self, asyncLocalStorage, serverList, myId, vectorClock):
        self.asyncLocalStorage = asyncLocalStorage
        self.serverList = serverList
        self.myId = myId
        self.vectorClock = vectorClock
    
    @staticmethod
    def compareMessages(msg1, msg2):
        """
        Compare two messages based on their timestamps.
        Messages are in format: [timestamp, text]
        Returns -1 if msg1 < msg2, 0 if equal, 1 if msg1 > msg2
        """
        if isinstance(msg1, list) and isinstance(msg2, list) and len(msg1) >= 2 and len(msg2) >= 2:
            return totalOrder(msg1[0], msg2[0])
        return 0

    def _should_propagate(self, server_id):
        return server_id == -1 or server_id == self.myId

    async def _inform_other_servers(self, operation, *args):
        tasks = []
        for server_id, proxy in enumerate(self.serverList):
            if server_id != self.myId:
                method = getattr(proxy, operation)
                tasks.append(method(*args))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def put(self, message, server_id=-1):
    
        if server_id == -1:
            # Client request - add timestamp using getTime() to increment clock
            # Use copy() to avoid reference issues when clock updates later
            timestamp = self.vectorClock.getTime().copy()
            timestamped_message = [timestamp, message]
        else:
            # message already has timestamp
            timestamped_message = message
        
        await self.asyncLocalStorage.put(timestamped_message, server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('put', timestamped_message)

    async def get(self, index, server_id=-1):
        return await self.asyncLocalStorage.get(index, server_id)

    async def getNum(self, server_id=-1):
        return await self.asyncLocalStorage.getNum(server_id)

    async def getBoard(self, server_id=-1):
        return await self.asyncLocalStorage.getBoard(server_id)

    async def modify(self, index, message, server_id=-1):
        if server_id == -1:
            # get old message to preserve timestamp
            old_message = await self.asyncLocalStorage.get(index, server_id)
            
            # Preserve the timestamp, update only the text
            if isinstance(old_message, list) and len(old_message) == 2:
                timestamped_message = [old_message[0].copy() if isinstance(old_message[0], list) else old_message[0], message]
            else:
                timestamp = self.vectorClock.getTime().copy()
                timestamped_message = [timestamp, message]
        else:
            # message already has [timestamp, text]
            timestamped_message = message
        
        await self.asyncLocalStorage.modify(index, timestamped_message, server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('modify', index, timestamped_message)

    async def delete(self, index, server_id=-1):
        await self.asyncLocalStorage.delete(index, server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('delete', index)

    async def deleteAll(self, server_id=-1):
        await self.asyncLocalStorage.deleteAll(server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('deleteAll')

    async def close(self):
        await self.asyncLocalStorage.close()

        for proxy in self.serverList:
            await proxy.close()
