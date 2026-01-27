import AsyncBoardProxy
import AsyncBoardStorage
import AtLeastOnceProxy
import AtMostOnceFilter
import BoardServer
import InformAllOtherServersWithClock
import logging
import LossyWebsocket
import sys
import VectorClock

# Ports of the servers of the cluster
serverPorts = [10000, 10001, 10002, 10003]

# Parameters: ID of cluster to be started, e.g. 0, 1, 2, 3
if len(sys.argv) < 2: # If ID of cluster is not given, then terminate program
        print("StartClusterInformingEachOther.py <ID of server>")
        exit(1)

serverID = int(sys.argv[1]) # Id of this server provided as parameter
port = serverPorts[serverID]

# Configure logging of websockets
#logging.basicConfig(
#    format= str(serverID) + " %(asctime)s %(message)s", level=logging.DEBUG,
#)

# Create object of logical clock
logicalClock = VectorClock.clock(len(serverPorts), serverID)

# Create proxies for the other servers
serversToInformAboutChanges = [AsyncBoardProxy.storage(serverPorts[id], serverID, logicalClock, websocketconnect=LossyWebsocket.connect) for id in range(len(serverPorts))]

# Wrap each proxy with a proxy object that implements at least once semantics
serversToInformAboutChanges = [AtLeastOnceProxy.storage(serversToInformAboutChanges[id]) for id in range(len(serverPorts))]

# Create storage containing data of this server. 
localStorage = AsyncBoardStorage.storage(InformAllOtherServersWithClock.storage.compareMessages) 

# Create object with distribution algorithm 
distributionAlgorithm = InformAllOtherServersWithClock.storage(localStorage, serversToInformAboutChanges, serverID, logicalClock)    

# Creates a AtMostOnceFilter that removes duplicate operations received by the stub
filter = AtMostOnceFilter.storage(distributionAlgorithm)

# Start server
BoardServer.startServer(port, filter, serverID=serverID, vClock=logicalClock)