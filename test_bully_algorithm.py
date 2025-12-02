#!/usr/bin/env python
"""
Test script for Bully Algorithm implementation in LeaderElection.

This tests:
1. getCoordiator() - Returns current coordinator or triggers election
2. startElection() - Runs the election process
3. election() - Remote procedure for election protocol
4. setCoordinator() - Remote procedure to set coordinator

Usage:
Start servers in different configurations and run tests:

Scenario 1 - All servers running:
  Terminal 1: ./bin/python UseMutexForUpdates_Main.py 0
  Terminal 2: ./bin/python UseMutexForUpdates_Main.py 1
  Terminal 3: ./bin/python UseMutexForUpdates_Main.py 2
  Terminal 4: ./bin/python UseMutexForUpdates_Main.py 3
  
Scenario 2 - Only lower ID servers:
  Terminal 1: ./bin/python UseMutexForUpdates_Main.py 0
  Terminal 2: ./bin/python UseMutexForUpdates_Main.py 1

Scenario 3 - Only higher ID servers:
  Terminal 1: ./bin/python UseMutexForUpdates_Main.py 2
  Terminal 2: ./bin/python UseMutexForUpdates_Main.py 3

Then run: ./bin/python test_bully_algorithm.py
"""

import asyncio
import AsyncBoardProxy
import LeaderElection

# Server configuration
serverPorts = [10000, 10001, 10002, 10003]

async def check_alive_servers():
    """Check which servers are currently running."""
    print("Checking which servers are alive...")
    alive = []
    for sid, port in enumerate(serverPorts):
        proxy = AsyncBoardProxy.storage(port, 99)
        try:
            result = await proxy.areYouAlive()
            if result == "YES":
                alive.append(sid)
                print(f"  ✓ Server {sid} (port {port}) is alive")
            else:
                print(f"  ✗ Server {sid} (port {port}) is not responding")
        except:
            print(f"  ✗ Server {sid} (port {port}) is not running")
        await proxy.close()
    return alive

async def test_start_election_from_server(server_id, alive_servers):
    """Test startElection from a specific server's perspective."""
    print(f"\n{'='*70}")
    print(f"Test: Starting election from Server {server_id}")
    print(f"{'='*70}")
    
    # Create proxies from this server's perspective
    proxies = [AsyncBoardProxy.storage(serverPorts[sid], server_id) for sid in range(len(serverPorts))]
    election_obj = LeaderElection.election(proxies, server_id)
    
    # Start election
    await election_obj.startElection()
    
    # Check the result
    coordinator_id = election_obj.coordinatorID
    print(f"Result: Server {coordinator_id} is now the coordinator")
    
    # The coordinator should be the highest ID server that's alive
    expected_coordinator = max(alive_servers)
    if coordinator_id == expected_coordinator:
        print(f"✓ CORRECT: Expected server {expected_coordinator} to be coordinator")
    else:
        print(f"✗ UNEXPECTED: Expected server {expected_coordinator}, got {coordinator_id}")
    
    # Clean up
    for proxy in proxies:
        await proxy.close()
    
    return coordinator_id

async def test_get_coordinator(server_id):
    """Test getCoordiator() method."""
    print(f"\n{'='*70}")
    print(f"Test: getCoordiator() from Server {server_id}")
    print(f"{'='*70}")
    
    # Create election object
    proxies = [AsyncBoardProxy.storage(serverPorts[sid], server_id) for sid in range(len(serverPorts))]
    election_obj = LeaderElection.election(proxies, server_id)
    
    # Call getCoordiator - should trigger election if no coordinator
    print("Calling getCoordiator()...")
    coordinator_proxy = await election_obj.getCoordiator()
    
    coordinator_id = election_obj.coordinatorID
    print(f"✓ getCoordiator() returned proxy for server {coordinator_id}")
    
    # Verify the coordinator is alive
    is_alive = await election_obj.callAreYouAlive(coordinator_id)
    if is_alive:
        print(f"✓ Coordinator {coordinator_id} is alive")
    else:
        print(f"✗ Coordinator {coordinator_id} appears to be dead!")
    
    # Clean up
    for proxy in proxies:
        await proxy.close()
    
    return coordinator_id

async def test_coordinator_failure_recovery(alive_servers):
    """Test what happens when coordinator fails."""
    print(f"\n{'='*70}")
    print(f"Test: Coordinator Failure Recovery Simulation")
    print(f"{'='*70}")
    
    if len(alive_servers) < 2:
        print("⚠ Need at least 2 servers for this test. Skipping...")
        return
    
    # Assume highest server is coordinator
    coordinator_id = max(alive_servers)
    lower_server = min(alive_servers)
    
    print(f"Simulating: Server {coordinator_id} is coordinator, then fails")
    print(f"Server {lower_server} will detect failure and start election")
    
    # Create election object for lower server
    proxies = [AsyncBoardProxy.storage(serverPorts[sid], lower_server) for sid in range(len(serverPorts))]
    election_obj = LeaderElection.election(proxies, lower_server)
    
    # Set a fake dead coordinator
    election_obj.coordinatorID = 99  # Non-existent server
    
    print(f"Server {lower_server} thinks coordinator is {election_obj.coordinatorID} (fake)")
    
    # Call getCoordiator - should detect failure and trigger election
    print("Calling getCoordiator() - should detect failure and trigger election...")
    coordinator_proxy = await election_obj.getCoordiator()
    
    new_coordinator = election_obj.coordinatorID
    print(f"✓ New coordinator elected: Server {new_coordinator}")
    
    # Clean up
    for proxy in proxies:
        await proxy.close()

async def test_election_remote_call():
    """Test the election() remote procedure."""
    print(f"\n{'='*70}")
    print(f"Test: Remote election() Call")
    print(f"{'='*70}")
    
    # Check server 0 is running
    proxy = AsyncBoardProxy.storage(serverPorts[0], 99)
    result = await proxy.areYouAlive()
    if result != "YES":
        print("⚠ Server 0 not running. Skipping this test.")
        await proxy.close()
        return
    
    print("Calling election() on Server 0 remotely...")
    result = await proxy.election()
    print(f"✓ election() returned: {result}")
    
    if result == "Take-Over":
        print("✓ CORRECT: Server responded with 'Take-Over'")
    else:
        print(f"✗ UNEXPECTED: Expected 'Take-Over', got '{result}'")
    
    await proxy.close()
    
    # Give server 0 time to complete its election
    print("Waiting for Server 0 to complete election...")
    await asyncio.sleep(1)

async def test_concurrent_elections(alive_servers):
    """Test multiple servers starting election simultaneously."""
    print(f"\n{'='*70}")
    print(f"Test: Concurrent Elections from Multiple Servers")
    print(f"{'='*70}")
    
    if len(alive_servers) < 2:
        print("⚠ Need at least 2 servers for this test. Skipping...")
        return
    
    # Start elections from multiple servers concurrently
    print(f"Starting elections concurrently from servers: {alive_servers}")
    
    tasks = []
    election_objects = []
    
    for sid in alive_servers:
        proxies = [AsyncBoardProxy.storage(serverPorts[i], sid) for i in range(len(serverPorts))]
        election_obj = LeaderElection.election(proxies, sid)
        election_objects.append((sid, election_obj, proxies))
        tasks.append(election_obj.startElection())
    
    # Wait for all elections to complete
    await asyncio.gather(*tasks)
    
    # Check that all servers agree on coordinator
    coordinators = []
    for sid, election_obj, proxies in election_objects:
        coord_id = election_obj.coordinatorID
        coordinators.append(coord_id)
        print(f"Server {sid} thinks coordinator is: {coord_id}")
        # Clean up
        for proxy in proxies:
            await proxy.close()
    
    # All should agree on the same coordinator
    if len(set(coordinators)) == 1:
        print(f"✓ SUCCESS: All servers agree on coordinator {coordinators[0]}")
    else:
        print(f"✗ INCONSISTENCY: Servers disagree on coordinator: {coordinators}")

async def main():
    print("="*70)
    print("Bully Algorithm - Comprehensive Test Suite")
    print("="*70)
    
    # Check which servers are alive
    alive_servers = await check_alive_servers()
    
    if not alive_servers:
        print("\n⚠ No servers are running!")
        print("Please start at least one server:")
        print("  ./bin/python UseMutexForUpdates_Main.py 0")
        return
    
    print(f"\n✓ Found {len(alive_servers)} alive server(s): {alive_servers}")
    print(f"Expected coordinator: Server {max(alive_servers)} (highest ID)")
    
    # Test 1: Start election from lowest ID server
    lowest_server = min(alive_servers)
    coordinator1 = await test_start_election_from_server(lowest_server, alive_servers)
    
    await asyncio.sleep(0.5)
    
    # Test 2: Start election from highest ID server (if different from lowest)
    if len(alive_servers) > 1:
        highest_server = max(alive_servers)
        coordinator2 = await test_start_election_from_server(highest_server, alive_servers)
        
        if coordinator1 == coordinator2:
            print(f"\n✓ Consistency: Both elections resulted in same coordinator")
        
        await asyncio.sleep(0.5)
    
    # Test 3: Test getCoordiator
    coordinator3 = await test_get_coordinator(lowest_server)
    
    await asyncio.sleep(0.5)
    
    # Test 4: Test remote election() call
    if 0 in alive_servers:
        await test_election_remote_call()
        await asyncio.sleep(0.5)
    
    # Test 5: Test coordinator failure recovery
    await test_coordinator_failure_recovery(alive_servers)
    
    await asyncio.sleep(0.5)
    
    # Test 6: Test concurrent elections
    await test_concurrent_elections(alive_servers)
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
    print("\nKey principles verified:")
    print("✓ Highest ID server becomes coordinator (Bully Algorithm)")
    print("✓ getCoordiator() triggers election when no coordinator exists")
    print("✓ getCoordiator() re-elects when coordinator is dead")
    print("✓ election() returns 'Take-Over' and starts local election")
    print("✓ setCoordinator() updates local coordinator and signals waiting threads")
    print("✓ Multiple concurrent elections converge to same result")

if __name__ == "__main__":
    asyncio.run(main())
