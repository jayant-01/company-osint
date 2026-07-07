import asyncio


class Throttle:

    def __init__(self, rate=5):

        self.semaphore = asyncio.Semaphore(rate)

    async def run(self, coro):

        async with self.semaphore:

            return await coro