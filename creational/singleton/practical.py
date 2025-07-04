"""
Singleton Design Pattern - Real World Implementation

Real-world example: Load Balancer
A load balancer that distributes requests across multiple servers.
Only one instance should exist to maintain consistent server state.
"""

import random
import threading
from typing import List, Optional


class LoadBalancer:
    """
    A load balancer that distributes requests across multiple servers.
    Implements Singleton pattern to ensure only one instance exists.
    """
    
    _instance: Optional['LoadBalancer'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._servers: List[str] = [
                "ServerI",
                "ServerII", 
                "ServerIII",
                "ServerIV",
                "ServerV"
            ]
            self._random = random.Random()
            print("LoadBalancer instance created with servers:", self._servers)
    
    @property
    def server(self) -> str:
        """
        Simple, but effective random load balancer.
        Returns a random server from the available servers.
        """
        index = self._random.randint(0, len(self._servers) - 1)
        return self._servers[index]
    
    def add_server(self, server: str) -> None:
        """Add a new server to the load balancer."""
        if server not in self._servers:
            self._servers.append(server)
            print(f"Added server: {server}")
    
    def remove_server(self, server: str) -> None:
        """Remove a server from the load balancer."""
        if server in self._servers and len(self._servers) > 1:
            self._servers.remove(server)
            print(f"Removed server: {server}")
        else:
            print(f"Cannot remove server: {server} (not found or last server)")
    
    def get_server_count(self) -> int:
        """Get the number of available servers."""
        return len(self._servers)
    
    def get_servers(self) -> List[str]:
        """Get a copy of the current server list."""
        return self._servers.copy()


def main():
    """
    Real-world client code demonstrating load balancer usage.
    """
    print("=== Load Balancer Singleton Demo ===")
    
    # Create multiple load balancer instances
    print("\nCreating multiple LoadBalancer instances...")
    b1 = LoadBalancer()
    b2 = LoadBalancer()
    b3 = LoadBalancer()
    b4 = LoadBalancer()
    
    # Verify they are the same instance
    if b1 is b2 is b3 is b4:
        print("✓ All instances are the same object")
        print(f"Instance ID: {id(b1)}")
    else:
        print("✗ Different instances created")
    
    # Use the load balancer
    print(f"\nLoad balancer has {b1.get_server_count()} servers")
    print(f"Available servers: {b1.get_servers()}")
    
    # Distribute 10 requests
    print("\nDistributing 10 requests:")
    balancer = LoadBalancer()
    for i in range(10):
        server = balancer.server
        print(f"Request {i+1:2d} → {server}")
    
    # Add a new server
    print("\nAdding new server...")
    balancer.add_server("ServerVI")
    print(f"Now has {balancer.get_server_count()} servers")
    
    # Distribute more requests
    print("\nDistributing 5 more requests:")
    for i in range(5):
        server = balancer.server
        print(f"Request {i+1:2d} → {server}")
    
    # Remove a server
    print("\nRemoving a server...")
    balancer.remove_server("ServerII")
    print(f"Now has {balancer.get_server_count()} servers")
    
    # Final requests
    print("\nFinal 5 requests:")
    for i in range(5):
        server = balancer.server
        print(f"Request {i+1:2d} → {server}")


if __name__ == "__main__":
    main()