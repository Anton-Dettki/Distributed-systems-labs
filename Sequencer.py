class sequencer: 
    def __init__(self): 
        self.counter = 0
        
    async def getSequenceNumber(self): 
        """
        Returns the next sequence number. 
        The first call of this function returns 1. The second call returns 2, and so on. 
        """
        self.counter += 1
        return self.counter