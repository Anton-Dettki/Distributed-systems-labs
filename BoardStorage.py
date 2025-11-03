class storage: 
    def __init__(self): 
        self.messages = []
        
    def put(self, message): 
        self.messages = self.messages + [message]
       
    def get(self, index): 
        index = int(index)
        if index >= 0 and index < len(self.messages): 
            return self.messages[index]
        else: 
            raise ValueError("Index is unknown.")
            
    def getNum(self): 
        return len(self.messages)
        
    def getBoard(self): 
        return self.messages
        
    def modify(self, index, message): 
        index = int(index)
        self.messages[index] = message
        
    def delete(self, index): 
        index = int(index)
        self.messages = [self.messages[i] for i in range(len(self.messages)) if i != index]

    def deleteAll(self): 
        self.messages = []
        
    def close(self): 
        pass