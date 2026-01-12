import VectorClock


def printCausalRelation(clock1, clock2): 
    time1 = clock1.getTimeNoEvent()
    time2 = clock2.getTimeNoEvent()

    if VectorClock.smallerEqual(time1, time2): 
        print(time1, "<=", time2)
    elif VectorClock.smallerEqual(time2, time1): 
        print(time2, "<=", time1)
    if VectorClock.concurrent(time1, time2): 
        print(time1, "||", time2)

def printTotalOrder(clock1, clock2): 
    time1 = clock1.getTimeNoEvent()
    time2 = clock2.getTimeNoEvent()

    order = VectorClock.totalOrder(time1, time2)    
    if (order < 0): 
        print(time1, "<", time2)
    elif (order > 0):
        print(time1, ">", time2)
    else: 
        print(time1, "==", time2)
    

p1 = VectorClock.clock(3, 0)
p2 = VectorClock.clock(3, 1)
p3 = VectorClock.clock(3, 2)

print(0, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])
p1.updateTime(p2.getTime())
print(1, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])
p2.updateTime(p1.getTime())
print(2, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])
p1.eventHappens()
print(3, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])
p3.updateTime(p2.getTime())
print(4, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])
p3.updateTime(p1.getTime())
print(5, [p1.getTimeNoEvent(), p2.getTimeNoEvent(), p3.getTimeNoEvent()])

print()

print("Causal Order:")
printCausalRelation(p1, p2)
printCausalRelation(p1, p3)
printCausalRelation(p2, p3)
print()

print("Total Order:")
printTotalOrder(p1, p2)
printTotalOrder(p1, p3)
printTotalOrder(p2, p3)
