from concurrent.futures import ThreadPoolExecutor, as_completed

class ConcurrentProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers

    def process_items(self, items, process_func, on_error=None):
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            future_to_item = {
                executor.submit(process_func, item, i): (item, i) 
                for i, item in enumerate(items)
            }
            
            for future in as_completed(future_to_item):
                item, index = future_to_item[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    if on_error:
                        on_error(item, str(e))
        
        if results:
            return set().union(*results)
        return set()