import redis
import os
import json
from typing import Any, Optional, Callable


class RedisClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance of the client exists."""
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        if hasattr(self, 'pool'): # Avoid re-initialization
            return
            
        try:
            # Create a connection pool. This is more efficient than creating a new
            # connection for every request.
            self.pool = redis.BlockingConnectionPool(
                host=config.get("REDIS_HOST", os.getenv("REDIS_HOST", "localhost")),
                port=int(config.get("REDIS_PORT", os.getenv("REDIS_PORT", 6379))),
                db=int(config.get("REDIS_DB", os.getenv("REDIS_DB", 0))),
                password=config.get("REDIS_PASSWORD", os.getenv("REDIS_PASSWORD")),
                max_connections=config.get("REDIS_MAX_CONNECTIONS", 10),
                timeout=config.get("REDIS_TIMEOUT", 5)
            )
            self.client = redis.Redis(connection_pool=self.pool, decode_responses=True)
            # Ping the server to check the connection
            self.client.ping()
            print("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")
            self.pool = None
            self.client = None
            raise

    def close_connection(self):
        """Closes the connection pool."""
        if self.pool:
            self.pool.disconnect()
            print("Redis connection pool disconnected.")

    ## --- Key-Value (String) Operations ---
    def set_value(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Sets a key-value pair. `ex` is the expiry time in seconds."""
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            print(f"Error setting value for key '{key}': {e}")
            return False

    def get_value(self, key: str) -> Optional[str]:
        """Gets the value for a given key."""
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Error getting value for key '{key}': {e}")
            return None

    def delete_key(self, key: str) -> int:
        """Deletes a key. Returns the number of keys deleted."""
        try:
            return self.client.delete(key)
        except Exception as e:
            print(f"Error deleting key '{key}': {e}")
            return 0
            
    ## --- Hash Operations ---
    def set_hash_field(self, name: str, key: str, value: Any) -> int:
        """Sets a field in a hash."""
        return self.client.hset(name, key, value)

    def get_hash_field(self, name: str, key: str) -> Optional[str]:
        """Gets a field from a hash."""
        return self.client.hget(name, key)

    def get_all_hash_fields(self, name: str) -> dict:
        """Gets all fields and values from a hash."""
        return self.client.hgetall(name)

    ## --- List Operations (for Queues/Stacks) ---
    def list_push(self, key: str, value: Any, to_right: bool = True):
        """Pushes a value to a list (LPUSH or RPUSH)."""
        if to_right:
            return self.client.rpush(key, value)
        return self.client.lpush(key, value)

    def list_pop(self, key: str, from_right: bool = True) -> Optional[str]:
        """Pops a value from a list (LPOP or RPOP)."""
        if from_right:
            return self.client.rpop(key)
        return self.client.lpop(key)

    ## --- Set Operations ---
    def set_add(self, key: str, *values: Any) -> int:
        """Adds one or more members to a set."""
        return self.client.sadd(key, *values)

    def set_members(self, key: str) -> set:
        """Gets all members of a set."""
        return self.client.smembers(key)
        
    def set_is_member(self, key: str, value: Any) -> bool:
        """Checks if a value is a member of a set."""
        return self.client.sismember(key, value)
        
    ## --- JSON Operations ---
    def set_json(self, key: str, data: dict, path: str = '$') -> bool:
        """Sets a JSON document."""
        try:
            return self.client.json().set(key, path, data)
        except Exception as e:
            print(f"Error setting JSON for key '{key}': {e}")
            return False

    def get_json(self, key: str, path: str = '$') -> Optional[dict]:
        """Gets a JSON document."""
        try:
            return self.client.json().get(key, path)
        except Exception as e:
            print(f"Error getting JSON for key '{key}': {e}")
            return None
            
    ## --- Publish/Subscribe Operations ---
    def publish_message(self, channel: str, message: str) -> int:
        """Publishes a message to a channel."""
        return self.client.publish(channel, message)

    def subscribe_to_channel(self, channel: str, handler_function: Callable):
        """
        Subscribes to a channel and processes messages.
        NOTE: This is a blocking operation.
        """
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        print(f"👂 Subscribed to channel '{channel}'. Waiting for messages...")
        for message in pubsub.listen():
            if message['type'] == 'message':
                handler_function(message['data'])
