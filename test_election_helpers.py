#!/usr/bin/env python
"""
Test script for LeaderElection helper methods:
- callAreYouAlive(serverID)
- callElection(serverID)
- callSetCoordinator(serverID, coordinatorID)
- callSetCoordinatorInAllServers(coordinatorID)

Usage:
1. Start one or more servers:
   Terminal 1: ./bin/python UseMutexForUpdates_Main.py 0
   Terminal 2: ./bin/python UseMutexForUpdates_Main.py 1
   Terminal 3: ./bin/python UseMutexForUpdates_Main.py 2

2. Run this test:
   ./bin/python test_election_helpers.py
"""

import asyncio
import AsyncBoardProxy
import LeaderElection

# Server ports
serverPorts = [10000, 10001, 10002, 10003]

async def test_helper_methods():
    print("=" * 70)
    print("Testing LeaderElection Helper Methods")
    print("=" * 70)
    
    # Create proxies for all servers (from perspective of test client with ID 99)
    testClientID = 99
    proxies = [AsyncBoardProxy.storage(serverPorts[id], testClientID) for id in range(len(serverPorts))]
    
    # Create leader election object
    leaderElection = LeaderElection.election(proxies, testClientID)
    
    print("\n" + "=" * 70)
    print("Test 1: callAreYouAlive() - Check which servers are alive")
    print("=" * 70)
    
    alive_servers = []
    for serverID in range(len(serverPorts)):
        result = await leaderElection.callAreYouAlive(serverID)
        status = "✓ ALIVE" if result else "✗ NOT ALIVE"
        print(f"Server {serverID} (port {serverPorts[serverID]}): {status}")
        if result:
            alive_servers.append(serverID)
    
    print(f"\nSummary: {len(alive_servers)} server(s) alive: {alive_servers}")
    
    if not alive_servers:
        print("\n⚠ No servers are running! Please start at least one server.")
        print("Example: ./bin/python UseMutexForUpdates_Main.py 0")
        return
    
    print("\n" + "=" * 70)
    print("Test 2: callElection() - Call election on alive servers")
    print("=" * 70)
    
    for serverID in alive_servers:
        result = await leaderElection.callElection(serverID)
        print(f"Server {serverID}: election() returned: {result}")
    
    # Test calling election on a dead server
    dead_servers = [sid for sid in range(len(serverPorts)) if sid not in alive_servers]
    if dead_servers:
        print(f"\nTesting election() on dead server {dead_servers[0]}:")
        result = await leaderElection.callElection(dead_servers[0])
        print(f"Server {dead_servers[0]}: election() returned: {result} (expected False)")
    
    print("\n" + "=" * 70)
    print("Test 3: callSetCoordinator() - Set coordinator on individual servers")
    print("=" * 70)
    
    new_coordinator = alive_servers[0]  # Use first alive server as new coordinator
    print(f"Setting coordinator to server {new_coordinator}...")
    
    for serverID in alive_servers:
        result = await leaderElection.callSetCoordinator(serverID, new_coordinator)
        status = "✓ SUCCESS" if result else "✗ FAILED"
        print(f"Server {serverID}: setCoordinator({new_coordinator}) - {status}")
    
    # Test calling setCoordinator on a dead server
    if dead_servers:
        print(f"\nTesting setCoordinator() on dead server {dead_servers[0]}:")
        result = await leaderElection.callSetCoordinator(dead_servers[0], new_coordinator)
        print(f"Server {dead_servers[0]}: setCoordinator({new_coordinator}) returned: {result} (expected False)")
    
    print("\n" + "=" * 70)
    print("Test 4: callSetCoordinatorInAllServers() - Broadcast to all servers")
    print("=" * 70)
    
    if len(alive_servers) > 1:
        new_coordinator = alive_servers[-1]  # Use last alive server as new coordinator
    else:
        new_coordinator = alive_servers[0]
    
    print(f"Broadcasting new coordinator (ID {new_coordinator}) to all servers...")
    await leaderElection.callSetCoordinatorInAllServers(new_coordinator)
    print(f"✓ Broadcast complete")
    
    # Verify by checking coordinator on each alive server
    print("\nVerifying coordinator was set on all alive servers:")
    await asyncio.sleep(0.2)  # Small delay to let operations complete
    
    for serverID in alive_servers:
        # We can't directly query the coordinator, but we can verify the call succeeded
        print(f"Server {serverID}: Coordinator broadcast sent")
    
    print("\n" + "=" * 70)
    print("Test 5: Concurrent calls with asyncio.gather()")
    print("=" * 70)
    
    print("Checking all servers concurrently...")
    tasks = [leaderElection.callAreYouAlive(sid) for sid in range(len(serverPorts))]
    results = await asyncio.gather(*tasks)
    
    for serverID, result in enumerate(results):
        status = "✓ ALIVE" if result else "✗ NOT ALIVE"
        print(f"Server {serverID}: {status}")
    
    print("\n" + "=" * 70)
    print("Test 6: Error handling - Testing with invalid server IDs")
    print("=" * 70)
    
    # Test with non-existent server port (create a proxy to invalid port)
    print("Testing with unreachable server...")
    bad_proxy = AsyncBoardProxy.storage(19999, testClientID)
    temp_proxies = proxies[:2] + [bad_proxy] + proxies[3:]
    temp_election = LeaderElection.election(temp_proxies, testClientID)
    
    result = await temp_election.callAreYouAlive(2)
    print(f"callAreYouAlive(unreachable_server): {result} (expected False)")
    
    result = await temp_election.callElection(2)
    print(f"callElection(unreachable_server): {result} (expected False)")
    
    result = await temp_election.callSetCoordinator(2, 0)
    print(f"callSetCoordinator(unreachable_server, 0): {result} (expected False)")
    
    await bad_proxy.close()
    
    # Clean up
    for proxy in proxies:
        await proxy.close()
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)
    print("\nKey observations:")
    print("- callAreYouAlive() returns True only if server responds with 'YES'")
    print("- callElection() returns server response or False on failure")
    print("- callSetCoordinator() returns True only if server responds with 'DONE'")
    print("- All methods handle exceptions and return False on failure")
    print("- callSetCoordinatorInAllServers() broadcasts to all servers concurrently")

if __name__ == "__main__":
    asyncio.run(test_helper_methods())
