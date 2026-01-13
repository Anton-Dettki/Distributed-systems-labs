import BoardProxy

# Test if synchronize works
proxy = BoardProxy.storage(10000)

print("Testing synchronize call to server 0...")
try:
    result = proxy.synchronize(1)
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
