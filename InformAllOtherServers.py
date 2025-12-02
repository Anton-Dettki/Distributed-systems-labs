import asyncio

class storage:
    def __init__(self, asyncLocalStorage, serverList, myId):
        self.asyncLocalStorage = asyncLocalStorage
        self.serverList = serverList
        self.myId = myId

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
        await self.asyncLocalStorage.put(message, server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('put', message)

    async def get(self, index, server_id=-1):
        return await self.asyncLocalStorage.get(index, server_id)

    async def getNum(self, server_id=-1):
        return await self.asyncLocalStorage.getNum(server_id)

    async def getBoard(self, server_id=-1):
        return await self.asyncLocalStorage.getBoard(server_id)

    async def modify(self, index, message, server_id=-1):
        await self.asyncLocalStorage.modify(index, message, server_id)
        
        if self._should_propagate(server_id):
            await self._inform_other_servers('modify', index, message)

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
