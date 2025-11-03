import time
import BoardProxy

proxy = BoardProxy.storage(10000)


def firstDownload():
    print('starting mass download')
    startTime = time.time()
    messages = proxy.getBoard()
    for msg in messages:
        print('Message: ', msg)
    endTime = time.time()
    print('Time to download: ', (endTime - startTime) * 1000 , ' ms')

def secondDownload():
    print('Starting one by one download')
    startTime = time.time()
    messages = {}
    n = proxy.getNum()
    for i in range(0, n):
        messages[i] = proxy.get(i)
    print(messages)
    endTime = time.time()
    print('Time to download one after another: ', (endTime - startTime) * 1000 , ' ms')
    
    
secondDownload()