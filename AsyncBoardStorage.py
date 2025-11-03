class storage:
    def __init__(self):
        self.messages = []

    async def put(self, message):
        self.messages.append(message)

    async def get(self, index):
        index = int(index)
        if 0 <= index < len(self.messages):
            return self.messages[index]
        else:
            raise ValueError("Index is unknown.")

    async def getNum(self):
        return len(self.messages)

    async def getBoard(self):
        return self.messages

    async def modify(self, index, message):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages[index] = message
        else:
            raise ValueError("Index is unknown.")

    async def delete(self, index):
        index = int(index)
        if 0 <= index < len(self.messages):
            self.messages.pop(index)
        else:
            raise ValueError("Index is unknown.")

    async def deleteAll(self):
        self.messages.clear()

    async def close(self):
        pass
