class mutex:
    """A simple non-blocking mutex.

    Methods are async to integrate with the asyncio-based server, but
    acquire() is non-blocking: it immediately returns True if the mutex
    was free and acquires it, otherwise returns False. release() frees
    the mutex.
    """
    def __init__(self):
        self._acquired = False

    async def acquire(self):
        """Attempt to acquire the mutex.

        Returns:
            True if the mutex was free and is now acquired by the caller.
            False if the mutex was already acquired.
        """
        if not self._acquired:
            self._acquired = True
            return True
        return False

    async def release(self):
        """Release the mutex.

        If the mutex was not acquired, this is a no-op.
        Returns True if the mutex was released, False if it was already free.
        """
        if self._acquired:
            self._acquired = False
            return True
        return False

