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

    async def put(self, message, server_id=-1):
        if server_id == -1:
            # Client request - add timestamp using getTime() to increment clock
            # Use copy() to avoid reference issues when clock updates later
            timestamp = self.vectorClock.getTime().copy()
            timestamped_message = [timestamp, message]
        else:
            # Server-to-server call - message already has timestamp
            timestamped_message = message
        
        await self.asyncLocalStorage.put(timestamped_message, server_id)

    async def get(self, index, server_id=-1):
        return await self.asyncLocalStorage.get(index, server_id)

    async def getNum(self, server_id=-1):
        return await self.asyncLocalStorage.getNum(server_id)

    async def getBoard(self, server_id=-1):
        return await self.asyncLocalStorage.getBoard(server_id)

    async def modify(self, index, message, server_id=-1):
        if server_id == -1:
            # Client request - get old message to preserve timestamp
            old_message = await self.asyncLocalStorage.get(index, server_id)
            
            # Preserve the timestamp, update only the text
            if isinstance(old_message, list) and len(old_message) == 2:
                timestamped_message = [old_message[0].copy() if isinstance(old_message[0], list) else old_message[0], message]
            else:
                timestamp = self.vectorClock.getTime().copy()
                timestamped_message = [timestamp, message]
        else:
            # Server-to-server call - message already has [timestamp, text]
            timestamped_message = message
        
        await self.asyncLocalStorage.modify(index, timestamped_message, server_id)

    async def delete(self, index, server_id=-1):
        await self.asyncLocalStorage.delete(index, server_id)

    async def deleteAll(self, server_id=-1):
        await self.asyncLocalStorage.deleteAll(server_id)

    async def synchronize(self, other_server_id, server_id=-1):
        """
        Synchronize this server with another server bidirectionally.
        Checks all messages in both servers and ensures both have the same messages.
        
        Args:
            other_server_id: ID of the server to synchronize with
            server_id: ID of the caller (-1 for client)
        """
        print(f"\n*** SYNCHRONIZE called on server {self.myId} ***")
        print(f"    Parameter other_server_id: {other_server_id}")
        print(f"    Parameter server_id: {server_id}")
        print(f"    Synchronizing with server {other_server_id}\n")
        
        try:
            # Get the board from the other server
            response = await self.serverList[other_server_id].getBoard()
            
            # Extract board from response (server-to-server calls return dict with RESULT and BOARD)
            if isinstance(response, dict) and "BOARD" in response:
                other_board = response["BOARD"]
            else:
                other_board = response
                
            print(f"    Retrieved {len(other_board)} messages from server {other_server_id}")
            
            # Get current local board
            local_board = await self.asyncLocalStorage.getBoard(server_id)
            print(f"    Current local board has {len(local_board)} messages")
            
            # Bidirectional synchronization:
            # 1. Add messages from other server that are missing locally
            print(f"    Checking for messages to add locally...")
            for message in other_board:
                if message not in local_board:
                    await self.asyncLocalStorage.put(message, self.myId)
                    print(f"    Added to local: {message}")
            
            # 2. Add messages from local server that are missing on the other server
            print(f"    Checking for messages to send to server {other_server_id}...")
            for message in local_board:
                if message not in other_board:
                    await self.serverList[other_server_id].put(message)
                    print(f"    Sent to server {other_server_id}: {message}")
            
            print(f"    Synchronization complete!\n")
            return "OK"
        except Exception as e:
            print(f"    Synchronization error: {e}\n")
            import traceback
            traceback.print_exc()
            return "ERROR"

    async def close(self):
        await self.asyncLocalStorage.close()

        for proxy in self.serverList:
            await proxy.close()
