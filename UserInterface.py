import BoardStorage
import BoardProxy
import sys
import time

testdata = ["Hallo.",  
            "You are the best!",
            "Learn about distributed systems!",
            "Bla Bla Bla.",
            "Bla Bla BLA!",
            "The End."
           ]

def cmdPut(argv): 
    try:
        message = " ".join(argv[1:])
        storage.put(message)
    except IndexError: 
        print("Invalid message for command put. Use put <message>.")

def cmdGet(argv): 
    try:
        index = argv[1]
        message = storage.get(index)
        if isinstance(message, list) and len(message) == 2:
            print("Message", index, ":", message[0], "-", message[1])
        else:
            print("Message", index, ":", message)
    except ValueError: 
        print("Message with index", index, "is not stored on server.")
    except IndexError: 
        print("Invalid parameter for get. Use get <index>.")
    except Exception as ex: 
        print("Exception", type(ex).__name__, ex.args)

def cmdGetNum(): 
    num = storage.getNum()
    print(num, "messages in message board")    

def cmdGetBoard():
    board = storage.getBoard()
    for index in range(len(board)):
        message = board[index]
        # Display message with timestamp if it's in [timestamp, text] format
        if isinstance(message, list) and len(message) == 2:
            print(index, ":", message[0], "-", message[1])
        else:
            print(index, ":", message)

def cmdModify(argv): 
    try:
        index = argv[1]
        message = " ".join(argv[2:])
        storage.modify(index, message)
    except IndexError: 
        print("Invalid parameter for delete. Use modify <index> <message>. Use valid index.")
    except Exception as ex: 
        print("Exception", type(ex).__name__, ex.args)

def cmdDelete(argv): 
    try:
        index = argv[1]
        storage.delete(index)
    except IndexError: 
        print("Invalid parameter for delete. Use delete <index>.")
    except Exception as ex: 
        print("Exception", type(ex).__name__, ex.args)

def cmdDeleteAll(): 
    storage.deleteAll()
    
def cmdTestData(): 
    startTime = time.time()
    for message in testdata: 
        storage.put(message)
    endTime = time.time()
    print("Test message have been uploaded to server.")
    print("Upload in", (endTime - startTime) * 1000, "ms.")

def cmdHelp(): 
    print("Possible commands:")
    print("put <message>            -- Store one message")
    print("get <index>              -- Retrieve one message")
    print("getnum                   -- Retrieve number of messages in board")
    print("getboard                 -- Retrieve entire message board")
    print("modify <index> <message> -- Change the message at index")
    print("delete <index>           -- Delete the message at index")
    print("deleteall                -- Deletes all messages")
    print("testdata                 -- Upload some messages as test data")
    print("help                     -- Show this help")
    print("exit                     -- Terminate this program")   


if len(sys.argv) > 1:       # A parameter was given to the program ...
    port = int(sys.argv[1]) # Assume the first parameter is the port number of the server
    print("DOING HERE")
    storage = BoardProxy.storage(port)  
else: 
    port = 0                # If no parameter is given, use local BoardStorage
    storage = BoardStorage.storage()

cmdHelp() # Print list of possible commands

command = ""
while command != "EXIT": 
    # print(storage.messages)
    print();

    print("Your command> ", end="")
    inputLine = input()
    argv = inputLine.split()
    if len(argv) > 0: 
        command = argv[0].upper()
        
        if command == "PUT": 
            cmdPut(argv)
        elif command == "GET": 
            cmdGet(argv)
        elif command == "GETNUM": 
            cmdGetNum()
        elif command == "GETBOARD": 
            cmdGetBoard()
        elif command == "MODIFY": 
            cmdModify(argv)
        elif command == "DELETE": 
            cmdDelete(argv)
        elif command == "DELETEALL": 
            cmdDeleteAll()
        elif command == "TESTDATA":
            cmdTestData()            
        elif command == "HELP": 
            cmdHelp()
        elif command == "EXIT":
            pass
        else: 
            print("Unknown command:", argv)

storage.close()
