#!/usr/bin/env python
"""
Simple visual demonstration of the Bully Algorithm.

Start servers: ./bin/python UseMutexForUpdates_Main.py 0 1 2 3
Run this: ./bin/python demo_bully.py
"""

import asyncio
import AsyncBoardProxy
import LeaderElection

serverPorts = [10000, 10001, 10002, 10003]

async def demo():
    print("\n" + "="*60)
    print("BULLY ALGORITHM DEMONSTRATION")
    print("="*60)
    
    # Check which servers are alive
    print("\nStep 1: Checking which servers are alive...")
    alive = []
    for sid in range(4):
        proxy = AsyncBoardProxy.storage(serverPorts[sid], 99)
        try:
            if await proxy.areYouAlive() == "YES":
                alive.append(sid)
                print(f"  Server {sid}: ALIVE ✓")
            else:
                print(f"  Server {sid}: dead ✗")
        except:
            print(f"  Server {sid}: dead ✗")
        await proxy.close()
    
    if not alive:
        print("\n⚠ No servers running! Start with:")
        print("  ./bin/python UseMutexForUpdates_Main.py 0")
        return
    
    expected_coordinator = max(alive)
    print(f"\n  Expected coordinator: Server {expected_coordinator} (highest ID)")
    
    # Run election from lowest server
    lowest = min(alive)
    print(f"\nStep 2: Server {lowest} starts election...")
    
    proxies = [AsyncBoardProxy.storage(serverPorts[i], lowest) for i in range(4)]
    election = LeaderElection.election(proxies, lowest)
    
    print(f"  Server {lowest}: Checking servers with higher IDs...")
    higher = [s for s in range(lowest+1, 4) if s in alive]
    print(f"  Higher servers: {higher if higher else 'none'}")
    
    await election.startElection()
    
    print(f"\n✓ Election complete!")
    print(f"  Coordinator: Server {election.coordinatorID}")
    
    if election.coordinatorID == expected_coordinator:
        print(f"  Result: CORRECT ✓")
    else:
        print(f"  Result: UNEXPECTED ✗")
    
    # Test getCoordiator
    print(f"\nStep 3: Testing getCoordiator()...")
    coord_proxy = await election.getCoordiator()
    print(f"  Returned proxy for server {election.coordinatorID}")
    
    # Clean up
    for p in proxies:
        await p.close()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nBully Algorithm rules:")
    print("1. Highest ID server becomes coordinator")
    print("2. Lower servers ask higher servers to take over")
    print("3. If no higher server responds, you're the coordinator")
    print("4. All servers are notified of the new coordinator")

if __name__ == "__main__":
    asyncio.run(demo())
