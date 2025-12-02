import asyncio

class storage:
    def __init__(self, asyncLocalStorage, serverList, myId, coordinatorId):
        self.asyncLocalStorage = asyncLocalStorage
        self.serverList = serverList
        self.myId = myId
        self.coordinatorId = coordinatorId
        self.lock = asyncio.Lock()

    def _is_coordinator(self):
        return self.myId == self.coordinatorId

    def _is_from_client(self, server_id):
        return server_id == -1 or server_id == self.myId

    def _is_from_coordinator(self, server_id):
        return server_id == self.coordinatorId

    async def _broadcast_to_all_servers(self, operation, *args):
        async with self.lock:
            tasks = []
            for server_id, proxy in enumerate(self.serverList):
                method = getattr(proxy, operation)
                tasks.append(method(*args))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _forward_to_coordinator(self, operation, *args):
        coordinator_proxy = self.serverList[self.coordinatorId]
        method = getattr(coordinator_proxy, operation)
        await method(*args)

    async def put(self, message, server_id=-1):
        if self._is_from_coordinator(server_id):
            await self.asyncLocalStorage.put(message, server_id)
        elif self._is_from_client(server_id):
            if self._is_coordinator():
                await self._broadcast_to_all_servers('put', message)
            else:
                await self._forward_to_coordinator('put', message)

    async def get(self, index, server_id=-1):
        return await self.asyncLocalStorage.get(index, server_id)

    async def getNum(self, server_id=-1):
        return await self.asyncLocalStorage.getNum(server_id)

    async def getBoard(self, server_id=-1):
        return await self.asyncLocalStorage.getBoard(server_id)

    async def modify(self, index, message, server_id=-1):
        if self._is_from_coordinator(server_id):
            await self.asyncLocalStorage.modify(index, message, server_id)
        elif self._is_from_client(server_id):
            if self._is_coordinator():
                await self._broadcast_to_all_servers('modify', index, message)
            else:
                await self._forward_to_coordinator('modify', index, message)

    async def delete(self, index, server_id=-1):
        if self._is_from_coordinator(server_id):
            await self.asyncLocalStorage.delete(index, server_id)
        elif self._is_from_client(server_id):
            if self._is_coordinator():
                await self._broadcast_to_all_servers('delete', index)
            else:
                await self._forward_to_coordinator('delete', index)

    async def deleteAll(self, server_id=-1):
        if self._is_from_coordinator(server_id):
            await self.asyncLocalStorage.deleteAll(server_id)
        elif self._is_from_client(server_id):
            if self._is_coordinator():
                await self._broadcast_to_all_servers('deleteAll')
            else:
                await self._forward_to_coordinator('deleteAll')

    async def close(self):
        await self.asyncLocalStorage.close()

        for proxy in self.serverList:
            await proxy.close()
