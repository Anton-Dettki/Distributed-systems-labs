#!/usr/bin/env python
"""
Test script for areYouAlive, election, and setCoordinator methods.

Usage:
1. Start a server first:
   ./bin/python UseMutexForUpdates_Main.py 0

2. Run this test:
   ./bin/python test_leader_election_methods.py
"""

import asyncio
import AsyncBoardProxy

async def test_methods():
    print("=" * 60)
    print("Testing Leader Election Methods")
    print("=" * 60)
    
    # Test with server on port 10000 (assuming it's running)
    port = 10000
    print(f"\nConnecting to server on port {port}...")
    proxy = AsyncBoardProxy.storage(port, myId=99)  # Use ID 99 for test client
    
    # Test 1: areYouAlive
    print("\n--- Test 1: areYouAlive() ---")
    try:
        result = await proxy.areYouAlive()
        print(f"✓ areYouAlive() returned: {result}")
        if result == "YES":
            print("  Server is alive!")
        else:
            print(f"  Unexpected response: {result}")
    except Exception as e:
        print(f"✗ areYouAlive() failed: {e}")
    
    # Test 2: election
    print("\n--- Test 2: election() ---")
    try:
        result = await proxy.election()
        print(f"✓ election() returned: {result}")
    except Exception as e:
        print(f"✗ election() failed: {e}")
    
    # Test 3: setCoordinator
    print("\n--- Test 3: setCoordinator(2) ---")
    try:
        result = await proxy.setCoordinator(2)
        print(f"✓ setCoordinator(2) returned: {result}")
    except Exception as e:
        print(f"✗ setCoordinator(2) failed: {e}")
    
    # Test 4: Test with non-running server
    print("\n--- Test 4: Calling methods on non-running server (port 19999) ---")
    dead_proxy = AsyncBoardProxy.storage(19999, myId=99)
    
    try:
        result = await dead_proxy.areYouAlive()
        print(f"areYouAlive() on dead server returned: {result}")
    except Exception as e:
        print(f"areYouAlive() on dead server raised exception: {type(e).__name__}")
    
    try:
        result = await dead_proxy.election()
        print(f"election() on dead server returned: {result}")
    except Exception as e:
        print(f"election() on dead server raised exception: {type(e).__name__}")
    
    # Clean up
    await proxy.close()
    await dead_proxy.close()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_methods())
