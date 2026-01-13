import AsyncBoardProxy
import AsyncBoardStorage
import BoardServer
import CentralizedActiveReplicationProtocol
import LeaderElection
import Sequencer
import logging
import sys


# Ports of the servers of the cluster
serverPorts = [10000, 10001, 10002, 10003]
IdOfCoordinator = 0

# Parameters: ID of cluster to be started, e.g. 0, 1, 2, 3
if len(sys.argv) < 2: # If ID of cluster is not given, then terminate program
        print("CentralizedActiveReplicationProtocol_Main <ID of server>")
        exit(1)

serverID = int(sys.argv[1]) # Id of this server provided as parameter
port = serverPorts[serverID]

# Configure logging of websockets
logging.basicConfig(
    format= str(serverID) + " %(asctime)s %(message)s", #level=logging.DEBUG,
)

# Create proxies for all servers
otherServersOfCluster = [AsyncBoardProxy.storage(serverPorts[id], serverID) for id in range(len(serverPorts))]

# Create storage containing data of this server. 
localStorage = AsyncBoardStorage.storage() 

# Create object with protocol for leader election
leaderElection = LeaderElection.election(otherServersOfCluster, serverID)

# Create sequencer proxy (assuming coordinator runs sequencer)
sequencerProxy = AsyncBoardProxy.storage(serverPorts[IdOfCoordinator], serverID)

# Create object with centralized active replication protocol
storage = CentralizedActiveReplicationProtocol.storage(localStorage, otherServersOfCluster, serverID, leaderElection, sequencerProxy)

# Create sequencer object (if this is the coordinator)
sequencer = Sequencer.sequencer()

# Start server
BoardServer.startServer(port, storage, serverID, sequencerParam=sequencer, leader=leaderElection)
