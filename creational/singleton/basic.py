"""
Singleton Design Pattern - Gang of Four Implementation

Intent: Ensure a class only has one instance, and provide a global point of access to it.

Structure:
- Singleton: defines an Instance operation that lets clients access its unique instance
"""

from typing import Optional
import threading


class Singleton:
    """
    The Singleton class defines the `get_instance` method that serves as an
    alternative to constructor and lets clients access the same instance of this
    class over and over.
    """
    
    _instance: Optional['Singleton'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls._instance is None:
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        The constructor is called every time, but since we control instance
        creation in __new__, we only initialize once.
        """
        if not hasattr(self, '_initialized'):
            self._initialized = True
            print("Singleton instance created")
    
    def some_business_logic(self) -> str:
        """
        Business logic that can be executed on the singleton instance.
        """
        return "Executing business logic on singleton instance"


def main():
    """
    The client code.
    """
    print("=== Singleton Pattern Demo ===")
    
    # Create first instance
    print("\nCreating first instance...")
    s1 = Singleton()
    print(f"First instance: {id(s1)}")
    
    # Create second instance
    print("\nCreating second instance...")
    s2 = Singleton()
    print(f"Second instance: {id(s2)}")
    
    # Test if they are the same instance
    if s1 is s2:
        print("\n✓ Both variables contain the same instance")
    else:
        print("\n✗ Variables contain different instances")
    
    # Execute business logic
    print(f"\nBusiness logic result: {s1.some_business_logic()}")


if __name__ == "__main__":
    main()