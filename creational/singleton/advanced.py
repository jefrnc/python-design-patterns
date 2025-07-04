"""
Singleton Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Metaclasses for clean singleton implementation
- __slots__ for memory efficiency
- Type hints for better IDE support
- Dataclass for configuration
- Context manager protocol
"""

from dataclasses import dataclass
from typing import Optional, Any, Dict, Type
import threading


class SingletonMeta(type):
    """
    Metaclass that creates singleton instances.
    Thread-safe implementation using double-checked locking.
    """
    
    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration for database connection."""
    host: str
    port: int
    username: str
    password: str
    database: str


class DatabaseConnection(metaclass=SingletonMeta):
    """
    Optimized singleton database connection using Python features.
    """
    
    __slots__ = ('_config', '_connection', '_is_connected')
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        if not hasattr(self, '_config'):
            self._config = config or DatabaseConfig(
                host="localhost",
                port=5432,
                username="user",
                password="password",
                database="mydb"
            )
            self._connection: Optional[str] = None
            self._is_connected = False
    
    def connect(self) -> None:
        """Establish database connection."""
        if not self._is_connected:
            # Simulate connection establishment
            self._connection = f"Connection to {self._config.host}:{self._config.port}/{self._config.database}"
            self._is_connected = True
            print(f"✓ Connected: {self._connection}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._is_connected:
            self._connection = None
            self._is_connected = False
            print("✓ Disconnected from database")
    
    def execute_query(self, query: str) -> str:
        """Execute a database query."""
        if not self._is_connected:
            self.connect()
        
        # Simulate query execution
        result = f"Executed: {query}"
        print(f"Query result: {result}")
        return result
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    @property
    def connection_info(self) -> str:
        return self._connection or "Not connected"
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __repr__(self) -> str:
        return f"DatabaseConnection(config={self._config}, connected={self._is_connected})"


# Alternative implementation using decorator
def singleton(cls):
    """
    Decorator-based singleton implementation.
    More Pythonic for simple cases.
    """
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class Logger:
    """
    Simple logger singleton using decorator approach.
    """
    
    __slots__ = ('_logs',)
    
    def __init__(self):
        self._logs: list[str] = []
    
    def log(self, message: str) -> None:
        """Log a message."""
        self._logs.append(message)
        print(f"LOG: {message}")
    
    def get_logs(self) -> list[str]:
        """Get all logs."""
        return self._logs.copy()
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        self._logs.clear()
        print("Logs cleared")


def main():
    """
    Demonstrate optimized singleton implementations.
    """
    print("=== Optimized Singleton Pattern Demo ===")
    
    # Test metaclass singleton
    print("\n1. Testing metaclass singleton:")
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    
    print(f"Same instance: {db1 is db2}")
    print(f"Instance ID: {id(db1)}")
    
    # Test database operations
    print("\n2. Testing database operations:")
    db1.execute_query("SELECT * FROM users")
    db2.execute_query("SELECT * FROM products")
    
    print(f"DB1 connected: {db1.is_connected}")
    print(f"DB2 connected: {db2.is_connected}")
    
    # Test context manager
    print("\n3. Testing context manager:")
    with DatabaseConnection() as db:
        db.execute_query("SELECT COUNT(*) FROM orders")
    
    print(f"After context: {db1.is_connected}")
    
    # Test decorator singleton
    print("\n4. Testing decorator singleton:")
    logger1 = Logger()
    logger2 = Logger()
    
    print(f"Same logger instance: {logger1 is logger2}")
    
    logger1.log("First message")
    logger2.log("Second message")
    
    print(f"Logger1 logs: {logger1.get_logs()}")
    print(f"Logger2 logs: {logger2.get_logs()}")
    
    # Test with configuration
    print("\n5. Testing with configuration:")
    config = DatabaseConfig(
        host="production-db",
        port=3306,
        username="prod_user",
        password="secure_pass",
        database="prod_db"
    )
    
    # Note: This will use the same instance due to singleton behavior
    db_with_config = DatabaseConnection(config)
    print(f"Same instance with config: {db_with_config is db1}")
    print(f"Config applied: {db_with_config}")


if __name__ == "__main__":
    main()