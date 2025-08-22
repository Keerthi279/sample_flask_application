import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os

class DatabasePool:
    """A class for managing a pool of PostgreSQL database connections."""

    def __init__(self, config):
        self.connection_pool = None
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=config.get("DB_MIN_CONN_COUNT", 1), 
                maxconn=config.get("DB_MAX_CONN_COUNT", 10), 
                user=config.get("DB_USER", os.getenv("DB_USER")),
                password=config.get("DB_PASSWORD", os.getenv("DB_PASSWORD")),
                host=config.get("DB_HOST", os.getenv("DB_HOST")),
                port=config.get("DB_PORT", os.getenv("DB_PORT", 5432)),
                database=config.get("DB_NAME", os.getenv("DB_NAME"))
            )
            print(" Database connection pool created successfully.")
        except psycopg2.OperationalError as e:
            print(f"Could not connect to the database: {e}")
            raise

    
    @contextmanager
    def get_connection(self):
        """
        A context manager to get a connection from the pool.
        Yields a connection and a cursor.
        """
        if self.connection_pool is None:
            raise ConnectionError("Database connection pool is not initialized.")

        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn, conn.cursor()
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"An error occurred: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    
    def close_all_connections(self):
        """Closes all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Database connection pool closed.")