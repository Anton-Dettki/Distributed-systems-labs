import json

class clock: 
    def __init__(self, numberServers, myID): 
        """
        Initializes a vector clock object. 
        Parameter numberServers is the total number of servers that are communicating. 
        Parameter myID is the ID of the server on which the object is created. 
                       It must be in the range 0 <= myID < numberServers. 
        """
        self.numberServers = numberServers
        self.myID = myID
        
        self.clock = [0 for _ in range(numberServers)]
        
        
    def print(self):
        """
        Prints the current time as a list.
        """
        print(self.clock)
        
    def eventHappens(self):
        """ 
        Signals that an event has happened on the local server. 
        This increases its element in the time vector. 
        """
        self.clock[self.myID] += 1
        """ Do something? """
        
    def getTimeNoEvent(self):
        """
        Returns the current time as list of the time values per server. 
        This does not change the time. 
        """
        return self.clock
        
        
    def getTime(self):
        """
        Returns the current time as list of the time values per server. 
        This triggers an event increasing the time for the local server. 
        """
        self.eventHappens()
        return self.clock
        
    def updateTime(self, timeFromOtherServer): 
        """
        updates the local time after receiving a time
        timestamp from another server. The time stamp vector is given to the method as list.
        """
        self.clock[self.myID] += 1
        
        for i in range(self.numberServers):
            if i != self.myID:
                self.clock[i] = max(self.clock[i], timeFromOtherServer[i])
        
        
        
def equal(time1, time2): 
    """
    Determines for two times if time1 is the same as time2. 
    Parameter time1: First time. It is a list as returned from getTime() or getTimeNoEvent. 
    Parameter time2: Second time. It is a list as returned from getTime() or getTimeNoEvent. 
    Both times must be lists have the same length.
    """
    return time1 == time2
    
    
def smallerEqual(time1, time2): 
    """
    Determines for two times if time1 is causally smaller or equal than time2. 
    Parameter time1: First time. It is a list as returned from getTime() or getTimeNoEvent. 
    Parameter time2: Second time. It is a list as returned from getTime() or getTimeNoEvent .
    Both times must be lists have the same length.
    """
    # time1 <= time2 if for all i: time1[i] <= time2[i]
    for i in range(len(time1)):
        if time1[i] > time2[i]:
            return False
    return True

def concurrent(time1, time2): 
    """
    Determines for two times if time1 is causally concurrent to time2. 
    Parameter time1: First time. It is a list as returned from getTime() or getTimeNoEvent. 
    Parameter time2: Second time. It is a list as returned from getTime() or getTimeNoEvent. 
    Both times must be lists have the same length.
    """
    return not smallerEqual(time1, time2) and not smallerEqual(time2, time1)
    
def totalOrder(time1, time2): 
    """
    Defines a total order for times. 
    Total order means, that two times are equal or one time is smaller than the other. 
    The function gets two times and compares it.
    Parameter time1: First time. It is a list as returned from getTime() or getTimeNoEvent. 
    Parameter time2: Second time. It is a list as returned from getTime() or getTimeNoEvent. 
    Returns -1 if time1 < time2
             0 if time1 == time2
             1 if time1 > time2 
    """
    if equal(time1, time2):
        return 0
    
    if smallerEqual(time1, time2):
        return -1
    if smallerEqual(time2, time1):
        return 1
    
    for i in range(len(time1)):
        if time1[i] < time2[i]:
            return -1
        elif time1[i] > time2[i]:
            return 1
    
    return 0

