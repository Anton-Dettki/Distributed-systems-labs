import asyncio

class election: 
    def __init__(self, proxies, myID): 
        """
        Constructs a new object for leader election. 
        Parameter proxies: List with the proxies of all servers ordered by their ID (0, 1, 2, 3, ...)
        Parameter myID: ID of the server in which the object is created. 
        """
        self.proxies = proxies
        self.myID = myID
        
    async def getCoordiator(self): 
        """
        Returns the proxy of the coordinator.
        If there is no coordinator, a new coordinator is elected 
        and the function waits for that.
        Hence it always returns the proxy of a coordinator. 
        """
        return self.proxies[0] # Return the proxy of the coordinator

    async def startElection(self):
        """
        This function starts the election process. 
        When this coroutines ends, a new coordinator has been elected. 
        """
        print("startElection() not implemented.")
        
    async def callAreYouAlive(self, serverID): 
        """
        Calls the function areYouAlive() on the server with the serverID.
        Parameter serverID: ID of the server to check if it is alive. 
        Returns True if the server is alive and False otherwise. 
        """
        print("callAreYouAlive() not implemented.")
            
    async def callElection(self, serverID): 
        """
        Calls the the function election() on the a server with the serverID.
        Parameter serverID: ID of the server in which the method shall be called. 
        Returns the response of the server if the server responded and False otherwise. 
        """        
        print("callElection() not implemented.")

    async def callSetCoordinator(self, serverID, coordinatorID): 
        """
        Calls the the function setCoordinator() on the a server with the serverID.
        Parameter serverID: ID of the server in which the method shall be called. 
        Parameter coordinatorID: ID of the new coordinator to be announce. 
        Returns True if this was successfull or False if a ConnectionRefusedError was thrown.
        """
        print("callSetCoordinator() not implemented.")

        
    async def callSetCoordinatorInAllServers(self, coordinatorID): 
        """ 
        Informs all servers about the new coordinator. 
        Parameter coordinatorID: ID of the new coordinator to be announce. 
        The function is implemented by calling setCoordinator() on all servers.
        """
        print("callSetCoordinatorInAllServers() not implemented.")
        
    
    ########################################################
    # Methods to be called from other servers via the stub #
    ########################################################
        
    async def election(self):
        """
        Called from other servers to start the election process. 
        Always retuns "Take-Over".
        """
        print("election() not implemented.")
        return "Take-Over"                     
        
    async def setCoordinator(self, coordinatorID):
        """
        Called from to coordinator to inform the server about that it is coordinator. 
        Parameter coordinatorID: ID of the new coordinator. 
        """
        print("setCoordinator() not implemented.")
