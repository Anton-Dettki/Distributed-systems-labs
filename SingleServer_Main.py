import AsyncBoardStorage
import BoardServer
import logging
import sys

# Configure logging of websockets
logging.basicConfig(
    format= "%(asctime)s %(message)s",
    level=logging.DEBUG,
)

storage = AsyncBoardStorage.storage() # Storage directly containing the data. 

if len(sys.argv) > 1: # A parameter was given to the program 
        port = int(sys.argv[1]) # Assume the first parameter is the port number
else: 
        port = 10000    # If no parameter is given, use default port.

BoardServer.startServer(port, storage)