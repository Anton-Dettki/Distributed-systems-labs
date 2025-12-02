#!/usr/bin/env python
"""
Quick test for LeaderElection helper methods.
Simple version - just checks the basics.

Start at least one server first:
  ./bin/python UseMutexForUpdates_Main.py 0
"""

import asyncio
import AsyncBoardProxy
import LeaderElection

async def quick_test():
    print("Quick Test - LeaderElection Helper Methods\n")
    
    # Setup
    serverPorts = [10000, 10001, 10002, 10003]
    proxies = [AsyncBoardProxy.storage(port, 99) for port in serverPorts]
    election = LeaderElection.election(proxies, 99)
    
    # Test 1: Check which servers are alive
    print("1. Checking servers...")
    for i in range(4):
        alive = await election.callAreYouAlive(i)
        print(f"   Server {i}: {'ALIVE' if alive else 'dead'}")
    
    # Test 2: Call election on server 0
    print("\n2. Calling election on server 0...")
    result = await election.callElection(0)
    print(f"   Result: {result}")
    
    # Test 3: Set coordinator to server 0
    print("\n3. Setting coordinator to server 0...")
    success = await election.callSetCoordinator(0, 0)
    print(f"   Success: {success}")
    
    # Test 4: Broadcast coordinator
    print("\n4. Broadcasting coordinator ID 0 to all servers...")
    await election.callSetCoordinatorInAllServers(0)
    print("   Done!")
    
    # Cleanup
    for proxy in proxies:
        await proxy.close()
    
    print("\n✓ Test complete!")

if __name__ == "__main__":
    asyncio.run(quick_test())
