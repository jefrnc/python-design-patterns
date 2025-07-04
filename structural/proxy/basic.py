"""
Proxy Design Pattern - Gang of Four Implementation

Intent: Provide a placeholder for another object to control access to it.

Structure:
- Subject: defines the common interface for RealSubject and Proxy
- RealSubject: defines the real object that the proxy represents
- Proxy: maintains a reference to the RealSubject and controls access to it
"""

from abc import ABC, abstractmethod
from typing import Optional
import time


class Subject(ABC):
    """
    The Subject interface declares common operations for both RealSubject and
    the Proxy. As long as the client works with RealSubject using this
    interface, you'll be able to pass it a proxy instead of a real subject.
    """
    
    @abstractmethod
    def request(self, data: str) -> str:
        pass


class RealSubject(Subject):
    """
    The RealSubject contains some core business logic. Usually, RealSubjects are
    capable of doing some useful work which may also be very slow or sensitive -
    e.g. correcting input data. A Proxy can solve these issues without any
    changes to the RealSubject's code.
    """
    
    def __init__(self, name: str = "RealSubject"):
        self._name = name
        print(f"RealSubject '{self._name}' created (expensive operation)")
        time.sleep(0.1)  # Simulate expensive initialization
    
    def request(self, data: str) -> str:
        """
        Simulate some business logic that takes time to execute.
        """
        print(f"RealSubject '{self._name}': Handling request with data: {data}")
        time.sleep(0.2)  # Simulate processing time
        return f"Result from {self._name}: Processed '{data}'"


class Proxy(Subject):
    """
    The Proxy has an interface identical to the RealSubject.
    """
    
    def __init__(self, real_subject: Optional[RealSubject] = None):
        self._real_subject = real_subject
        self._cache: dict[str, str] = {}
        self._access_count = 0
    
    def request(self, data: str) -> str:
        """
        The most common applications of the Proxy pattern are lazy loading,
        caching, controlling the access, logging, etc. A Proxy can perform one
        of these things and then, depending on the result, pass the execution
        to the same method in a linked RealSubject object.
        """
        
        # Access control
        if not self._check_access():
            return "Proxy: Access denied"
        
        # Lazy initialization
        if self._real_subject is None:
            print("Proxy: Lazy initialization of RealSubject")
            self._real_subject = RealSubject("LazyLoaded")
        
        # Caching
        if data in self._cache:
            print(f"Proxy: Returning cached result for '{data}'")
            return self._cache[data]
        
        # Logging
        self._log_access(data)
        
        # Delegate to real subject
        result = self._real_subject.request(data)
        
        # Cache the result
        self._cache[data] = result
        
        return result
    
    def _check_access(self) -> bool:
        """
        Simple access control - allow only first 5 requests.
        """
        self._access_count += 1
        if self._access_count > 5:
            print("Proxy: Access limit exceeded")
            return False
        
        print(f"Proxy: Access granted (request #{self._access_count})")
        return True
    
    def _log_access(self, data: str) -> None:
        """
        Log the access to the real subject.
        """
        print(f"Proxy: Logging access to RealSubject with data: '{data}'")
    
    def get_cache_info(self) -> dict[str, str]:
        """
        Get current cache state.
        """
        return self._cache.copy()
    
    def clear_cache(self) -> None:
        """
        Clear the cache.
        """
        self._cache.clear()
        print("Proxy: Cache cleared")


class ProtectionProxy(Subject):
    """
    A protection proxy that controls access based on user credentials.
    """
    
    def __init__(self, real_subject: RealSubject, user_role: str):
        self._real_subject = real_subject
        self._user_role = user_role
        self._allowed_roles = {"admin", "user"}
    
    def request(self, data: str) -> str:
        if self._user_role not in self._allowed_roles:
            return f"ProtectionProxy: Access denied for role '{self._user_role}'"
        
        if self._user_role == "user" and "sensitive" in data.lower():
            return "ProtectionProxy: Access denied to sensitive data"
        
        print(f"ProtectionProxy: Access granted for role '{self._user_role}'")
        return self._real_subject.request(data)


class VirtualProxy(Subject):
    """
    A virtual proxy that implements lazy loading and caching.
    """
    
    def __init__(self):
        self._real_subject: Optional[RealSubject] = None
        self._is_loaded = False
    
    def request(self, data: str) -> str:
        if not self._is_loaded:
            print("VirtualProxy: Loading real subject...")
            self._real_subject = RealSubject("Virtual")
            self._is_loaded = True
        
        return self._real_subject.request(data)
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


def client_code(subject: Subject, data: str) -> None:
    """
    The client code is supposed to work with all objects (both subjects and
    proxies) via the Subject interface in order to support both real subjects
    and proxies. In real life, however, clients mostly work with their real
    subjects directly. In this case, to implement the pattern more easily, you
    can extend your proxy from the real subject's class.
    """
    result = subject.request(data)
    print(f"Client received: {result}")


def main():
    """
    The client code demonstrates different types of proxies.
    """
    print("=== Proxy Pattern Demo ===")
    
    # Direct access to real subject
    print("\n1. Direct access to RealSubject:")
    real_subject = RealSubject("Direct")
    client_code(real_subject, "test data")
    
    # Proxy with caching and access control
    print("\n2. Access through Proxy (with caching and access control):")
    proxy = Proxy()
    
    # First request - will create real subject and cache result
    client_code(proxy, "cached data")
    
    # Second request - will return cached result
    client_code(proxy, "cached data")
    
    # Different data - will process and cache
    client_code(proxy, "new data")
    
    print(f"Cache contains: {list(proxy.get_cache_info().keys())}")
    
    # Test access control
    print("\n3. Testing access control:")
    for i in range(3):
        client_code(proxy, f"request {i+4}")
    
    # Protection proxy
    print("\n4. Protection Proxy:")
    real_subject2 = RealSubject("Protected")
    
    # Admin access
    admin_proxy = ProtectionProxy(real_subject2, "admin")
    client_code(admin_proxy, "sensitive information")
    
    # User access to normal data
    user_proxy = ProtectionProxy(real_subject2, "user")
    client_code(user_proxy, "normal data")
    
    # User access to sensitive data (should be denied)
    client_code(user_proxy, "sensitive information")
    
    # Invalid role
    guest_proxy = ProtectionProxy(real_subject2, "guest")
    client_code(guest_proxy, "any data")
    
    # Virtual proxy (lazy loading)
    print("\n5. Virtual Proxy (lazy loading):")
    virtual_proxy = VirtualProxy()
    print(f"Real subject loaded: {virtual_proxy.is_loaded}")
    
    # First access triggers loading
    client_code(virtual_proxy, "lazy data")
    print(f"Real subject loaded: {virtual_proxy.is_loaded}")
    
    # Subsequent access uses loaded subject
    client_code(virtual_proxy, "more lazy data")
    
    # Pre-initialized proxy
    print("\n6. Pre-initialized Proxy:")
    pre_real = RealSubject("PreInitialized")
    pre_proxy = Proxy(pre_real)
    client_code(pre_proxy, "pre-init data")


if __name__ == "__main__":
    main()