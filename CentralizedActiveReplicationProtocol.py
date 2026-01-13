import asyncio

class storage: 
    def __init__(self, messageBoard, proxies, myID, leaderElection, sequencerProxy=None): 
        self.messageBoard = messageBoard
        self.proxies = proxies
        self.myID = myID
        self.leaderElection = leaderElection
        self.sequencerProxy = sequencerProxy  # Proxy to coordinator with sequencer
        self._update_queue = asyncio.PriorityQueue()
        self._update_task_started = False
        self._update_task = None
        self._next_expected_seq = 1  # Track next expected sequence number (sequencer starts at 1)

    async def put(self, message, senderID=0, sequenceNumber=None): 
        print(f"PUT called: message={message}, senderID={senderID}, sequenceNumber={sequenceNumber}, myID={self.myID}")
        
        # Check if this is from a client (senderID == -1) or from another server
        if senderID == -1:
            # Client call: get sequence number from sequencer and forward to all servers
            print(f"Client call detected, getting sequence number from sequencer")
            if self.sequencerProxy is None:
                print("ERROR: No sequencer proxy available")
                return 'ERROR'
            
            try:
                seq_num = await self.sequencerProxy.getSequenceNumber()
                print(f"Got sequence number: {seq_num}")
            except Exception as e:
                print(f"Failed to get sequence number: {e}")
                return 'ERROR'
            
            # Forward to all other servers with sequence number
            for i, proxy in enumerate(self.proxies):
                if i == self.myID:
                    continue
                try:
                    await proxy.put(message, seq_num)
                except Exception as e:
                    print(f"Failed to forward PUT to server {i}: {e}")
            
            # Enqueue for local execution with sequence number as priority
            await self._update_queue.put((seq_num, "PUT", message))
            self._ensure_update_task()
            return 'QUEUED'
        else:
            # Server-to-server call: enqueue with sequence number
            print(f"Server-to-server call detected, enqueueing with sequence number {sequenceNumber}")
            await self._update_queue.put((sequenceNumber, "PUT", message))
            self._ensure_update_task()
            return 'DONE'
        
    async def get(self, index, senderID=0): 
        return await self.messageBoard.get(index)
            
    async def getNum(self, senderID=0): 
        return await self.messageBoard.getNum()
        
    async def getBoard(self, senderID=0): 
        return await self.messageBoard.getBoard()
        
    async def modify(self, index, message, senderID=0, sequenceNumber=None): 
        print(f"MODIFY called: index={index}, message={message}, senderID={senderID}, sequenceNumber={sequenceNumber}")
        
        if senderID == -1:
            # Client call: get sequence number and forward to all servers
            if self.sequencerProxy is None:
                return 'ERROR'
            
            try:
                seq_num = await self.sequencerProxy.getSequenceNumber()
                print(f"Got sequence number: {seq_num}")
            except Exception as e:
                print(f"Failed to get sequence number: {e}")
                return 'ERROR'
            
            # Forward to all other servers
            for i, proxy in enumerate(self.proxies):
                if i == self.myID:
                    continue
                try:
                    await proxy.modify(index, message, seq_num)
                except Exception as e:
                    print(f"Failed to forward MODIFY to server {i}: {e}")
            
            # Enqueue for local execution
            await self._update_queue.put((seq_num, "MODIFY", index, message))
            self._ensure_update_task()
            return 'QUEUED'
        else:
            # Server-to-server call
            await self._update_queue.put((sequenceNumber, "MODIFY", index, message))
            self._ensure_update_task()
            return 'DONE'
        
    async def delete(self, index, senderID=0, sequenceNumber=None): 
        print(f"DELETE called: index={index}, senderID={senderID}, sequenceNumber={sequenceNumber}")
        
        if senderID == -1:
            # Client call: get sequence number and forward to all servers
            if self.sequencerProxy is None:
                return 'ERROR'
            
            try:
                seq_num = await self.sequencerProxy.getSequenceNumber()
                print(f"Got sequence number: {seq_num}")
            except Exception as e:
                print(f"Failed to get sequence number: {e}")
                return 'ERROR'
            
            # Forward to all other servers
            for i, proxy in enumerate(self.proxies):
                if i == self.myID:
                    continue
                try:
                    await proxy.delete(index, seq_num)
                except Exception as e:
                    print(f"Failed to forward DELETE to server {i}: {e}")
            
            # Enqueue for local execution
            await self._update_queue.put((seq_num, "DELETE", index))
            self._ensure_update_task()
            return 'QUEUED'
        else:
            # Server-to-server call
            await self._update_queue.put((sequenceNumber, "DELETE", index))
            self._ensure_update_task()
            return 'DONE'
            
    async def deleteAll(self, senderID=0, sequenceNumber=None): 
        print(f"DELETEALL called: senderID={senderID}, sequenceNumber={sequenceNumber}")
        
        if senderID == -1:
            # Client call: get sequence number and forward to all servers
            if self.sequencerProxy is None:
                return 'ERROR'
            
            try:
                seq_num = await self.sequencerProxy.getSequenceNumber()
                print(f"Got sequence number: {seq_num}")
            except Exception as e:
                print(f"Failed to get sequence number: {e}")
                return 'ERROR'
            
            # Forward to all other servers
            for i, proxy in enumerate(self.proxies):
                if i == self.myID:
                    continue
                try:
                    await proxy.deleteAll(seq_num)
                except Exception as e:
                    print(f"Failed to forward DELETEALL to server {i}: {e}")
            
            # Enqueue for local execution
            await self._update_queue.put((seq_num, "DELETEALL"))
            self._ensure_update_task()
            return 'QUEUED'
        else:
            # Server-to-server call
            await self._update_queue.put((sequenceNumber, "DELETEALL"))
            self._ensure_update_task()
            return 'DONE'
    
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
        """Background coroutine that processes queued update operations in sequence number order."""
        while True:
            item = await self._update_queue.get()
            if not item:
                continue

            # Extract sequence number (first element) and operation
            seq_num = item[0]
            op = item[1]
            
            print(f"Processing item with sequence number {seq_num}, expected: {self._next_expected_seq}")
            
            # Check if this is the expected sequence number
            if seq_num != self._next_expected_seq:
                print(f"Sequence number {seq_num} is not expected (waiting for {self._next_expected_seq}), re-queueing")
                # Put back into queue and wait
                await self._update_queue.put(item)
                await asyncio.sleep(0.1)  # Wait before trying again
                continue
            
            # This is the expected sequence number, execute the operation
            print(f"Executing operation {op} with sequence number {seq_num}")
            
            try:
                if op == "PUT":
                    message = item[2]
                    await self.messageBoard.put(message, self.myID, seq_num)
                    print(f"PUT executed: {message}")
                            
                elif op == "MODIFY":
                    index = item[2]
                    message = item[3]
                    await self.messageBoard.modify(index, message, self.myID, seq_num)
                    print(f"MODIFY executed: index={index}, message={message}")
                            
                elif op == "DELETE":
                    index = item[2]
                    await self.messageBoard.delete(index, self.myID, seq_num)
                    print(f"DELETE executed: index={index}")
                            
                elif op == "DELETEALL":
                    await self.messageBoard.deleteAll(self.myID, seq_num)
                    print(f"DELETEALL executed")
                
                # Increment expected sequence number after successful execution
                self._next_expected_seq += 1
                print(f"Operation completed, next expected sequence number: {self._next_expected_seq}")
                
            except Exception as e:
                print(f"Error executing operation {op}: {e}")
                # Still increment to avoid getting stuck
                self._next_expected_seq += 1
        
    async def close(self): 
        self.messageBoard.close()
        for proxy in self.proxies:
            proxy.close()