import BoardProxy
import os
import sys
import threading 
import time


numberMessagesPerServer = 0                  # Number of messages to be sent to each server.
serverPorts   = [10000, 10001, 10002, 10003] # Ports of the server to which messages shall be uploaded.

serverProxies = [BoardProxy.storage(port) for port in serverPorts] # Create Proxies for each server.

# Thread function to upload messages to one server. 
def uploadToServer(serverIndex): 
    myPort = serverPorts[serverIndex]
    myProxy = serverProxies[serverIndex]
    
    for i in range(numberMessagesPerServer): 
        message = str(serverIndex) + "." + str(i)  # Create messages such as "2.3"
        print("Sending", message, "to", myPort)
        myProxy.put(message)
      

# Extract parameter für number of messages to be sent to the server
if len(sys.argv) > 1:       # Was a parameter given to the program?
    numberMessagesPerServer = int(sys.argv[1]) # Then: Assume the first parameter is number of packets to sent for each server
else: 
    numberMessagesPerServer = 4 # Otherwise use default value.

#**************************************************************************
#***************** Delete all messages from all servers *******************
#**************************************************************************
      
# Delete all available data from the servers
for proxy in serverProxies:
    proxy.deleteAll()
time.sleep(1) # Wait some time.
                
#**************************************************************************
#******************** Upload messages to each server **********************
#**************************************************************************

print("Starting upload")   
     
startTimeUpload = time.time() # Time before uploading to measure time for uploading 
#Start threads
threads = [None for i in range(len(serverProxies))]
for i in range(len(serverProxies)): 
   threads[i] = threading.Thread(target=uploadToServer, args=(i,)) 
   threads[i].start()

# Wait for threads to terminate    
for i in range(len(serverProxies)): 
   threads[i].join()

endTimeUpload = time.time() # Time after uploading to measure time for uploading 
   
time.sleep(1) # Wait some time.         

#**************************************************************************
#*********************** Synchronize the servers **************************
#**************************************************************************

startTimeSynchronization = time.time() # Time before synchronizing servers
   
#---------------------------------------------------#   
# Synchronize all servers with each other           #
# To ensure all 4 servers have all 16 messages,     #
# we synchronize pairs to form a complete graph:    #
# - Server 0 with 1, 2, 3                           #
# - Server 1 with 2, 3                              #
# - Server 2 with 3                                 #
#---------------------------------------------------#   

print("\n=== Synchronizing all servers ===\n")

# Synchronize server 0 with servers 1, 2, and 3
print("Synchronizing server 0 with server 1...")
result = serverProxies[0].synchronize(1)
print(f"Result: {result}")

print("Synchronizing server 0 with server 2...")
result = serverProxies[0].synchronize(2)
print(f"Result: {result}")

print("Synchronizing server 0 with server 3...")
result = serverProxies[0].synchronize(3)
print(f"Result: {result}")

# Synchronize server 1 with servers 2 and 3
print("\nSynchronizing server 1 with server 2...")
result = serverProxies[1].synchronize(2)
print(f"Result: {result}")

print("Synchronizing server 1 with server 3...")
result = serverProxies[1].synchronize(3)
print(f"Result: {result}")

# Synchronize server 2 with server 3
print("\nSynchronizing server 2 with server 3...")
result = serverProxies[2].synchronize(3)
print(f"Result: {result}")

print("\n=== Synchronization complete ===\n")

endTimeSynchronization = time.time() # Time after synchronizing servers
   
time.sleep(3) # Wait some time.         


#**************************************************************************
#************ Download and display messages from all servers **************
#**************************************************************************
# Do this only if the total number of message to display is not too big. 
if (numberMessagesPerServer * len(serverProxies) <= 25): # Not too many message to be displayed?
    boards = [s.getBoard() for s in serverProxies] # Retrieve boards from all servers
    maxlen = max([len(b) for b in boards]) # Maximum length of one of the boards
    maxlenMessage =  max([len(str(message)) for board in boards for message in board]) # Maximum no of characters to draw a message
    fillerString   = "-" * maxlenMessage # String to be displayed if a message is missing in a message board. 

    print("Server:\t\t", end="")  
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

#**************************************************************************
#**************************** Display times  ******************************
#**************************************************************************

print("Time for uploading:", (endTimeUpload - startTimeUpload) * 1000, "ms")
print("Time for synchronization:", (endTimeSynchronization - startTimeSynchronization) * 1000, "ms")

# Close all proxies
for proxy in serverProxies: 
    board = proxy.close()
    
