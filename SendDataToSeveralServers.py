import BoardProxy
import os
import sys
import threading 
import time


numberMessagesPerServer = 0                  
serverPorts   = [10000, 10001, 10002, 10003]

serverProxies = [BoardProxy.storage(port) for port in serverPorts] 

def uploadToServer(serverIndex): 
    myPort = serverPorts[serverIndex]
    myProxy = serverProxies[serverIndex]
    
    for i in range(numberMessagesPerServer): 
        message = str(serverIndex) + "." + str(i)  
        print("Sending", message, "to", myPort)
        myProxy.put(message)
      

if len(sys.argv) > 1:      
    numberMessagesPerServer = int(sys.argv[1]) 
else: 
    numberMessagesPerServer = 4 

      
sp = serverProxies[0]
sp.deleteAll()

time.sleep(3)       
                
print("Starting upload")        
startTime = time.time()


threads = [None for i in range(len(serverProxies))]
for i in range(len(serverProxies)): 
   threads[i] = threading.Thread(target=uploadToServer, args=(i,)) 
   threads[i].start()

for i in range(len(serverProxies)): 
   threads[i].join()

endTime = time.time() 
   
time.sleep(1)
   
   
if (numberMessagesPerServer * len(serverProxies) <= 25): 
    print("Server: ", end="")  
    for port in serverPorts:
        print(f'{port:>10}', end="");
    print()        
    boards = [s.getBoard() for s in serverProxies]
    maxlen = max([len(b) for b in boards])
    for index in range(maxlen): 
        print(f'{index:>5}', ":", end="")
        for board in boards: 
            if index < len(board): 
                v = board[index]
                if isinstance(v, list) and len(v) == 2:
                    display_val = v[1]
                else:
                    display_val = v
                print(f'{display_val:>10}', end="")
        print()

print("Time for uploading:", (endTime - startTime) * 1000, "ms")

for proxy in serverProxies: 
    board = proxy.close()
    
