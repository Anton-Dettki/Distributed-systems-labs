import asyncio

class storage: 
    def __init__(self, proxy): 
        self.proxy = proxy
        # Cache for non-idempotent operations: key=(server_id, seq_num), value=response
        self.response_cache = {}
        # Track highest sequence number per server for cache cleanup
        self.highest_seq_per_server = {}

    def _get_cache_key(self, server_id, sequence_number):
        """Generate cache key from server ID and sequence number."""
        return (server_id, sequence_number)
    
    def _cleanup_old_cache_entries(self, server_id, current_seq):
        """Remove old cache entries from previous sequence numbers."""
        # Update highest sequence number for this server
        if server_id not in self.highest_seq_per_server:
            self.highest_seq_per_server[server_id] = current_seq
        else:
            old_highest = self.highest_seq_per_server[server_id]
            self.highest_seq_per_server[server_id] = max(old_highest, current_seq)
            
            # Remove entries older than current - 10 (keep a small window)
            keys_to_remove = []
            for (cached_server_id, cached_seq) in self.response_cache.keys():
                if cached_server_id == server_id and cached_seq < current_seq - 10:
                    keys_to_remove.append((cached_server_id, cached_seq))
            
            for key in keys_to_remove:
                del self.response_cache[key]

    async def put(self, message, server_id=-1, sequenceNumber=None): 
        # put() is not idempotent - check cache for duplicates
        if sequenceNumber is not None:
            cache_key = self._get_cache_key(server_id, sequenceNumber)
            
            # Check if we've seen this request before
            if cache_key in self.response_cache:
                print(f"Duplicate put detected (server={server_id}, seq={sequenceNumber}), returning cached response")
                return self.response_cache[cache_key]
            
            # First time seeing this request - execute it
            response = await self.proxy.put(message, server_id)
            
            # Cache the response
            self.response_cache[cache_key] = response
            self._cleanup_old_cache_entries(server_id, sequenceNumber)
            
            return response
        else:
            # No sequence number - just forward (shouldn't happen with AtLeastOnceProxy)
            return await self.proxy.put(message, server_id)
    async def modify(self, index, message, server_id=-1, sequenceNumber=None):
        # modify() is idempotent - just forward
        return await self.proxy.modify(index, message, server_id)
        
    async def delete(self, index, server_id=-1, sequenceNumber=None):
        # delete() is not idempotent - check cache for duplicates
        if sequenceNumber is not None:
            cache_key = self._get_cache_key(server_id, sequenceNumber)
            
            # Check if we've seen this request before
            if cache_key in self.response_cache:
                print(f"Duplicate delete detected (server={server_id}, seq={sequenceNumber}), returning cached response")
                return self.response_cache[cache_key]
            
            # First time seeing this request - execute it
            response = await self.proxy.delete(index, server_id)
            
            # Cache the response
            self.response_cache[cache_key] = response
            self._cleanup_old_cache_entries(server_id, sequenceNumber)
            
            return response
        else:
            # No sequence number - just forward (shouldn't happen with AtLeastOnceProxy)
            return await self.proxy.delete(index, server_id)
            
    async def deleteAll(self, server_id=-1, sequenceNumber=None):
        # deleteAll() is idempotent - just forward
        return await self.proxy.deleteAll(server_id)

    async def get(self, index, server_id=-1): 
        # get() is idempotent - just forward
        return await self.proxy.get(index, server_id)
            
    async def getNum(self, server_id=-1):
        # getNum() is idempotent - just forward
        return await self.proxy.getNum(server_id)
        
    async def getBoard(self, server_id=-1):
        # getBoard() is idempotent - just forward
        return await self.proxy.getBoard(server_id)
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