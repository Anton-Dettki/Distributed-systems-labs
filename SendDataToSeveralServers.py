import BoardProxy
import os
import sys
import threading 
import time


numberMessagesPerServer = 0                  # Number of messages to be sent to each server.
# serverPorts   = [10000] # Ports of the server to which messages shall be uploaded.
# serverPorts   = [10000, 10001, 10002, 10003] # Ports of the server to which messages shall be uploaded.
# serverPorts   = [10000, 10001, 10002] # Ports of the server to which messages shall be uploaded.
serverPorts   = [10001, 10002] # Ports of the server to which messages shall be uploaded.

serverProxies = [BoardProxy.storage(port) for port in serverPorts] # Create Proxies for each server.

def uploadToServer(serverIndex): 
    myPort = serverPorts[serverIndex]
    myProxy = serverProxies[serverIndex]
    
    for i in range(numberMessagesPerServer): 
        message = str(serverIndex) + "." + str(i)  # Create messages such as "2.3"
        print("Sending", message, "to", myPort)
        myProxy.put(message)
      

if len(sys.argv) > 1:       # A parameter was given to the program ...
    numberMessagesPerServer = int(sys.argv[1]) # Assume the first parameter is number of packets to sent for each server
else: 
    numberMessagesPerServer = 4 # Otherwise use default value.

      
# Delete all available data from the servers
sp = serverProxies[0]
sp.deleteAll()
#while sp.getNum() > 0: 
#    sp.delete(0)
time.sleep(3) # Wait some time, so that the deletes are propagated to all servers.         
                
print("Starting upload")        
startTime = time.time() # Time before uploading to measure time for uploading 

#Start threads
threads = [None for i in range(len(serverProxies))]
for i in range(len(serverProxies)): 
   threads[i] = threading.Thread(target=uploadToServer, args=(i,)) 
   threads[i].start()

# Wait for threads to terminate    
for i in range(len(serverProxies)): 
   threads[i].join()

endTime = time.time() # Time after uploading to measure time for uploading 
   
time.sleep(1) # Wait 1 second to allow all servers to synchronize.        
   
   
# Query and display the message boards from each server.
# Do this only if the total number of message to display is not too big. 
if (numberMessagesPerServer * len(serverProxies) <= 25): # Not too many message to be displayed?
    boards = [s.getBoard() for s in serverProxies] # Retrieve boards from all servers
    maxlen = max([len(b) for b in boards]) # Maximum length of one of the boards
    maxlenMessage =  max([len(str(message)) for board in boards for message in board]) # Maximum no of characters to draw a message
    fillerString   = "-" * maxlenMessage # String to be displayed if a message is missing in a message board. 

    print("Server:", end="")  
    for port in serverPorts:
        print(("{0: <"+ str(maxlenMessage)+"}").format(str(port)), end="\t");
    print()        

    for index in range(maxlen): 
        print(f'{index:>5}', ":", end="")
        for board in boards: 
            if index < len(board): # Display only if there is an element with the index in the board. 
                v = board[index]
                # print(f'{v:>10}', end="")
                print(v, "\t", end="")
            else: 
                print(fillerString, "\t", end="")
        print()

print("Time for uploading:", (endTime - startTime) * 1000, "ms")

# Close all proxies
for proxy in serverProxies: 
    board = proxy.close()
    
