import asyncio

class RateLimiter:
    def __init__(self, requests_per_second: float):
        self.delay = 1.0 / requests_per_second
        self.last_request = 0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            if now - self.last_request < self.delay:
                await asyncio.sleep(self.delay - (now - self.last_request))
            self.last_request = now
