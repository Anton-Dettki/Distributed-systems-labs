from functools import cmp_to_key

class storage:
    def __init__(self, compareFunc=None):
        self.messages = []
        self.compareFunc = compareFunc

    async def put(self, message, server_id=0, sequenceNumber=None):
        self.messages.append(message)
        # Sort messages if comparison function is provided
        if self.compareFunc is not None:
            self.messages.sort(key=cmp_to_key(self.compareFunc))

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
        else:
            raise ValueError("Index is unknown.")

    async def delete(self, index, server_id=0, sequenceNumber=None):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages.pop(index)
        else:
            raise ValueError("Index is unknown.")

    async def deleteAll(self, server_id=0, sequenceNumber=None):
        self.messages.clear()

    async def close(self):
        pass
