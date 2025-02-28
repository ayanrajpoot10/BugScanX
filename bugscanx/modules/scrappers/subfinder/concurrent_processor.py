import asyncio

class ConcurrentProcessor:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent

    async def process_items(self, items, process_func, on_error=None):
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results = [None] * len(items)
        tasks = {}

        async def process_item(index, item):
            async with semaphore:
                try:
                    result = await process_func(item, index)
                    if result:
                        results[index] = result if isinstance(result, (list, set)) else [result]
                except Exception as e:
                    if on_error:
                        on_error(item, str(e))

        for i, item in enumerate(items):
            tasks[i] = asyncio.create_task(process_item(i, item))

        for future in asyncio.as_completed(tasks.values()):
            await future

        return set(item for sublist in results if sublist for item in sublist)