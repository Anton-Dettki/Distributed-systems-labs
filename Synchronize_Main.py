import AsyncBoardProxy
import AsyncBoardStorage
import BoardServer
import Synchronize
import logging
import sys
import VectorClock

# Ports of the servers of the cluster
serverPorts = [10000, 10001, 10002, 10003]

# Parameters: ID of cluster to be started, e.g. 0, 1, 2, 3
if len(sys.argv) < 2: # If ID of cluster is not given, then terminate program
        print("Synchronize_Main.py <ID of server>")
        exit(1)

serverID = int(sys.argv[1]) # Id of this server provided as parameter
port = serverPorts[serverID]

# Configure logging of websockets
logging.basicConfig(
    format= str(serverID) + " %(asctime)s %(message)s", level=logging.DEBUG,
)

# Create object of logical clock
logicalClock = VectorClock.clock(len(serverPorts), serverID)

# Create proxies for the other servers
serversToInformAboutChanges = [AsyncBoardProxy.storage(serverPorts[id], serverID, logicalClock) for id in range(len(serverPorts))]

# Create storage containing data of this server with sorting by timestamps
localStorage = AsyncBoardStorage.storage(Synchronize.storage.compareMessages) 

# Create object with distribution algorithm 
storage = Synchronize.storage(localStorage, serversToInformAboutChanges, serverID, logicalClock)    

# Start server
BoardServer.startServer(port, storage, serverID=serverID, vClock=logicalClock)
