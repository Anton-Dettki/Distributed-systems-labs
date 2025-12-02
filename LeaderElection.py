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
        self.coordinatorID = None  # Current coordinator ID
        self.coordinator_event = asyncio.Event()  # Event to signal when new coordinator is elected
        self.coordinator_event.set()  # Initially set (no election in progress)
        
    async def getCoordiator(self): 
        """
        Returns the proxy of the coordinator.
        If there is no coordinator, a new coordinator is elected 
        and the function waits for that.
        Hence it always returns the proxy of a coordinator. 
        """
        # Check if current coordinator is alive
        if self.coordinatorID is not None:
            is_alive = await self.callAreYouAlive(self.coordinatorID)
            if is_alive:
                return self.proxies[self.coordinatorID]
        
        # No coordinator or coordinator is dead - start election
        self.coordinator_event.clear()
        await self.startElection()
        
        # Wait for election to complete
        await self.coordinator_event.wait()
        
        return self.proxies[self.coordinatorID]

    async def startElection(self):
        """
        This function starts the election process. 
        When this coroutines ends, a new coordinator has been elected. 
        """
        print(f"Server {self.myID}: Starting election...")
        
        # Check if there are servers with higher ID
        higher_servers = [sid for sid in range(self.myID + 1, len(self.proxies))]
        
        if not higher_servers:
            # No higher servers - I am the coordinator
            print(f"Server {self.myID}: No higher servers, I am the new coordinator")
            await self.callSetCoordinatorInAllServers(self.myID)
            return
        
        # Call election() on all servers with higher ID
        print(f"Server {self.myID}: Calling election on higher servers: {higher_servers}")
        tasks = [self.callElection(sid) for sid in higher_servers]
        results = await asyncio.gather(*tasks)
        
        # Check if any server responded with "Take-Over"
        took_over = False
        for sid, result in zip(higher_servers, results):
            if result == "Take-Over":
                print(f"Server {self.myID}: Server {sid} responded with Take-Over")
                took_over = True
                break
        
        if took_over:
            # A higher server took over - wait for setCoordinator to be called
            print(f"Server {self.myID}: Waiting for new coordinator announcement...")
            self.coordinator_event.clear()
            await self.coordinator_event.wait()
        else:
            # No higher server responded - I am the coordinator
            print(f"Server {self.myID}: No higher servers responded, I am the new coordinator")
            await self.callSetCoordinatorInAllServers(self.myID)
        
    async def callAreYouAlive(self, serverID): 
        """
        Calls the function areYouAlive() on the server with the serverID.
        Parameter serverID: ID of the server to check if it is alive. 
        Returns True if the server is alive and False otherwise. 
        """
        try:
            proxy = self.proxies[serverID]
            result = await proxy.areYouAlive()
            # Check if the response is "YES"
            return result == "YES"
        except Exception as e:
            # Server not available or error occurred
            return False
            
    async def callElection(self, serverID): 
        """
        Calls the the function election() on the a server with the serverID.
        Parameter serverID: ID of the server in which the method shall be called. 
        Returns the response of the server if the server responded and False otherwise. 
        """        
        try:
            proxy = self.proxies[serverID]
            result = await proxy.election()
            # Return the response from the server
            return result
        except Exception as e:
            # Server not available or error occurred
            return False

    async def callSetCoordinator(self, serverID, coordinatorID): 
        """
        Calls the the function setCoordinator() on the a server with the serverID.
        Parameter serverID: ID of the server in which the method shall be called. 
        Parameter coordinatorID: ID of the new coordinator to be announce. 
        Returns True if this was successfull or False if a ConnectionRefusedError was thrown.
        """
        try:
            proxy = self.proxies[serverID]
            result = await proxy.setCoordinator(coordinatorID)
            # Check if the operation was successful
            return result == "DONE"
        except Exception as e:
            # Server not available or error occurred
            return False

        
    async def callSetCoordinatorInAllServers(self, coordinatorID): 
        """ 
        Informs all servers about the new coordinator. 
        Parameter coordinatorID: ID of the new coordinator to be announce. 
        The function is implemented by calling setCoordinator() on all servers.
        """
        # First, set coordinator locally
        await self.setCoordinator(coordinatorID)
        
        # Then call setCoordinator on all other servers concurrently
        tasks = []
        for serverID in range(len(self.proxies)):
            if serverID != self.myID:  # Skip ourselves
                task = self.callSetCoordinator(serverID, coordinatorID)
                tasks.append(task)
        
        # Wait for all calls to complete (some may fail, that's ok)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
    
    ########################################################
    # Methods to be called from other servers via the stub #
    ########################################################
        
    async def election(self):
        """
        Called from other servers to start the election process. 
        Always retuns "Take-Over".
        """
        print(f"Server {self.myID}: election() called from another server")
        # Start our own election process in the background (don't wait for it)
        asyncio.create_task(self.startElection())
        return "Take-Over"
        
    async def setCoordinator(self, coordinatorID):
        """
        Called from to coordinator to inform the server about that it is coordinator. 
        Parameter coordinatorID: ID of the new coordinator. 
        """
        print(f"Server {self.myID}: setCoordinator({coordinatorID}) called")
        self.coordinatorID = coordinatorID
        # Signal that we have a new coordinator
        self.coordinator_event.set()
