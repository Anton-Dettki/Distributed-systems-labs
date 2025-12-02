class storage:
    def __init__(self):
        self.messages = []

    async def put(self, message, server_id=0):
        self.messages.append(message)

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

    async def modify(self, index, message, server_id=0):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages[index] = message
        else:
            raise ValueError("Index is unknown.")

    async def delete(self, index, server_id=0):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages.pop(index)
        else:
            raise ValueError("Index is unknown.")

    async def deleteAll(self, server_id=0):
        self.messages.clear()

    async def close(self):
        pass
