import asyncio

class storage: 
    def __init__(self, messageBoard, proxies, myID, leaderElection): 
        self.messageBoard = messageBoard
        self.proxies = proxies
        self.myID = myID
        self.leaderElection = leaderElection
        self._update_queue = asyncio.Queue()
        self._update_task_started = False
        self._update_task = None

    async def put(self, message, senderID=0): 
        print(f"PUT called: message={message}, senderID={senderID}, myID={self.myID}")
        # If senderID is -1, it's from a client (no MYID in request) - enqueue it
        if senderID == -1:
            print(f"Client call detected, enqueueing")
            await self._update_queue.put(("PUT", message))
            self._ensure_update_task()
            return 'QUEUED'
        
        # Otherwise this is a server-to-server propagation call
        # The originating server already holds the mutex, so just update local storage
        print(f"Server-to-server call detected, updating local storage")
        await self.messageBoard.put(message, senderID)
        return 'DONE'
        
    async def get(self, index, senderID=0): 
        return await self.messageBoard.get(index)
            
    async def getNum(self, senderID=0): 
        return await self.messageBoard.getNum()
        
    async def getBoard(self, senderID=0): 
        return await self.messageBoard.getBoard()
        
    async def modify(self, index, message, senderID=0): 
        if senderID == -1:
            await self._update_queue.put(("MODIFY", index, message))
            self._ensure_update_task()
            return 'QUEUED'
        
        await self.messageBoard.modify(index, message, senderID)
        return 'DONE'
        
    async def delete(self, index, senderID=0): 
        if senderID == -1:
            await self._update_queue.put(("DELETE", index))
            self._ensure_update_task()
            return 'QUEUED'
        
        await self.messageBoard.delete(index, senderID)
        return 'DONE'
            
    async def deleteAll(self, senderID=0): 
        if senderID == -1:
            await self._update_queue.put(("DELETEALL",))
            self._ensure_update_task()
            return 'QUEUED'
        
        await self.messageBoard.deleteAll(senderID)
        return 'DONE'
    
    def _ensure_update_task(self):
        """Start the background update task if not already started."""
        if not self._update_task_started:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running event loop yet
                return
            self._update_task = loop.create_task(self._update_task_proc())
            self._update_task_started = True
    
    async def _update_task_proc(self):
        """Background coroutine that processes queued update operations."""
        while True:
            item = await self._update_queue.get()
            if not item:
                continue

            op = item[0]

            # Get coordinator proxy
            try:
                coordinator = await self.leaderElection.getCoordiator()
            except Exception:
                # Re-enqueue and retry later
                await self._update_queue.put(item)
                await asyncio.sleep(0.1)
                continue

            # Acquire the mutex (retry until acquired)
            while True:
                try:
                    got = await coordinator.acquire()
                except Exception:
                    await asyncio.sleep(0.1)
                    continue
                if got:
                    break
                await asyncio.sleep(0.1)

            # We have the mutex — perform the operation
            try:
                if op == "PUT":
                    _, message = item
                    # Update local message board
                    await self.messageBoard.put(message, self.myID)

                    # Propagate to other servers (skip self)
                    for i, proxy in enumerate(self.proxies):
                        if i == self.myID:
                            continue
                        try:
                            await proxy.put(message)
                        except Exception:
                            pass
                            
                elif op == "MODIFY":
                    _, index, message = item
                    # Update local message board
                    await self.messageBoard.modify(index, message, self.myID)

                    # Propagate to other servers (skip self)
                    for i, proxy in enumerate(self.proxies):
                        if i == self.myID:
                            continue
                        try:
                            await proxy.modify(index, message)
                        except Exception:
                            pass
                            
                elif op == "DELETE":
                    _, index = item
                    # Update local message board
                    await self.messageBoard.delete(index, self.myID)

                    # Propagate to other servers (skip self)
                    for i, proxy in enumerate(self.proxies):
                        if i == self.myID:
                            continue
                        try:
                            await proxy.delete(index)
                        except Exception:
                            pass
                            
                elif op == "DELETEALL":
                    # Update local message board
                    await self.messageBoard.deleteAll(self.myID)

                    # Propagate to other servers (skip self)
                    for i, proxy in enumerate(self.proxies):
                        if i == self.myID:
                            continue
                        try:
                            await proxy.deleteAll()
                        except Exception:
                            pass
            finally:
                # Always release the mutex (best-effort)
                try:
                    await coordinator.release()
                except Exception:
                    pass
        
    async def close(self): 
        self.messageBoard.close()
        for proxy in self.proxies:
            proxy.close()