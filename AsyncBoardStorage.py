from functools import cmp_to_key
import json
import os

class storage:
    def __init__(self, comperatorForElements=None, checkpointing=False, serverID=None):
        self.messages = []
        self.compareFunc = comperatorForElements
        self.checkpointing = checkpointing
        self.serverID = serverID
        
        # Load checkpoint if checkpointing is enabled
        if self.checkpointing and self.serverID is not None:
            self._load_checkpoint()

    def _get_checkpoint_filename(self):
        """Generate the checkpoint filename based on server ID"""
        return f"checkpoint_{self.serverID}.json"
    
    def _load_checkpoint(self):
        """Load the message board from the checkpoint file if it exists"""
        filename = self._get_checkpoint_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    self.messages = json.load(f)
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                self.messages = []
    
    def _write_checkpoint(self):
        """Write the current message board to the checkpoint file"""
        if self.checkpointing and self.serverID is not None:
            filename = self._get_checkpoint_filename()
            try:
                with open(filename, 'w') as f:
                    json.dump(self.messages, f, indent=2)
            except Exception as e:
                print(f"Error writing checkpoint: {e}")

    async def put(self, message, server_id=0, sequenceNumber=None):
        self.messages.append(message)
        # Sort messages if comparison function is provided
        if self.compareFunc is not None:
            self.messages.sort(key=cmp_to_key(self.compareFunc))
        # Write checkpoint after update
        self._write_checkpoint()

    async def get(self, index, server_id=0):
        index = int(index)
        if 0 <= index < len(self.messages):
            return self.messages[index]
        else:
            raise ValueError("Index is unknown.")

    async def getNum(self, server_id=0):
        return len(self.messages)

    async def getBoard(self, server_id=0):
        return self.messages

    async def modify(self, index, message, server_id=0, sequenceNumber=None):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages[index] = message
            # Re-sort messages if comparison function is provided
            # (timestamp might have changed the order)
            if self.compareFunc is not None:
                self.messages.sort(key=cmp_to_key(self.compareFunc))
            # Write checkpoint after update
            self._write_checkpoint()
        else:
            raise ValueError("Index is unknown.")

    async def delete(self, index, server_id=0, sequenceNumber=None):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages.pop(index)
            # Write checkpoint after update
            self._write_checkpoint()
        else:
            raise ValueError("Index is unknown.")

    async def deleteAll(self, server_id=0, sequenceNumber=None):
        self.messages.clear()
        # Write checkpoint after update
        self._write_checkpoint()

    async def close(self):
        pass
