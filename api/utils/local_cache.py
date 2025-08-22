
daily_cache = {}

# 3. Define the decorator for caching

def cache_until_midnight(func):
    """
    A decorator that caches the result of a function until midnight.
    The cache key is based on the function name and the current date.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate a cache key based on the function name and the current date string (e.g., '2025-08-21')
        today_str = datetime.now().strftime('%Y-%m-%d')
        cache_key = f"{func.__name__}:{today_str}"

        # If the key exists in our cache, it means we have a valid, same-day response
        if cache_key in daily_cache:
            print(f"Returning CACHED response for key: {cache_key}")
            return daily_cache[cache_key]

        # If not in cache, execute the function to get a fresh response
        print(f"Cache miss for key: {cache_key}. Fetching new data...")
        result = func(*args, **kwargs)

        # Store the new response in the cache with today's key
        daily_cache[cache_key] = result
        
        
        keys_to_delete = [key for key in daily_cache if not key.endswith(today_str)]
        for key in keys_to_delete:
            del daily_cache[key]
        print("Old cache keys cleaned up.")
            
        return result

    return wrapper