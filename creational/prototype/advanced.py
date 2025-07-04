"""
Prototype Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Dataclasses with copy methods
- __copy__ and __deepcopy__ magic methods
- Metaclasses for automatic prototype registration
- Protocols for structural typing
- Context managers for prototype factories
- Decorators for cloning validation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, Generic, Dict, Any, Optional, Union, Type, runtime_checkable
from functools import wraps
import copy
import json
import pickle
from enum import Enum, auto


# Type variables
T = TypeVar('T')
P = TypeVar('P', bound='Prototype')


def validate_clone(func):
    """Decorator to validate cloning operations."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        original_id = id(self)
        cloned = func(self, *args, **kwargs)
        cloned_id = id(cloned)
        
        if original_id == cloned_id:
            raise ValueError("Clone operation failed: same object reference")
        
        return cloned
    return wrapper


@runtime_checkable
class Prototype(Protocol):
    """Protocol for objects that can be cloned."""
    
    def clone(self) -> 'Prototype':
        """Create a copy of this object."""
        ...


class CloningStrategy(Enum):
    """Different cloning strategies."""
    SHALLOW = auto()
    DEEP = auto()
    CUSTOM = auto()
    PICKLE = auto()


class PrototypeMeta(type):
    """
    Metaclass that automatically registers prototypes.
    """
    
    _registry: Dict[str, Any] = {}
    
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Auto-register prototypes
        if hasattr(cls, '_auto_register') and cls._auto_register:
            registry_name = kwargs.get('registry_name', name.lower())
            mcs._registry[registry_name] = cls
        
        return cls
    
    @classmethod
    def get_registered(mcs, name: str) -> Optional[Type]:
        """Get a registered prototype class."""
        return mcs._registry.get(name)
    
    @classmethod
    def list_registered(mcs) -> list[str]:
        """List all registered prototype names."""
        return list(mcs._registry.keys())


@dataclass
class ConfigurablePrototype:
    """
    Base class for configurable prototypes using dataclasses.
    """
    
    name: str
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    _cloning_strategy: CloningStrategy = CloningStrategy.DEEP
    
    def __post_init__(self):
        """Post-initialization hook."""
        if 'created_at' not in self.metadata:
            import datetime
            self.metadata['created_at'] = datetime.datetime.now().isoformat()
    
    @validate_clone
    def clone(self) -> 'ConfigurablePrototype':
        """Clone using the configured strategy."""
        if self._cloning_strategy == CloningStrategy.SHALLOW:
            return copy.copy(self)
        elif self._cloning_strategy == CloningStrategy.DEEP:
            return copy.deepcopy(self)
        elif self._cloning_strategy == CloningStrategy.PICKLE:
            return pickle.loads(pickle.dumps(self))
        else:
            return self._custom_clone()
    
    def _custom_clone(self) -> 'ConfigurablePrototype':
        """Custom cloning implementation."""
        return copy.deepcopy(self)
    
    def set_cloning_strategy(self, strategy: CloningStrategy) -> None:
        """Set the cloning strategy."""
        self._cloning_strategy = strategy
    
    def __copy__(self):
        """Shallow copy implementation."""
        return type(self)(
            name=self.name,
            version=self.version,
            metadata=self.metadata,
            _cloning_strategy=self._cloning_strategy
        )
    
    def __deepcopy__(self, memo):
        """Deep copy implementation."""
        return type(self)(
            name=self.name,
            version=self.version,
            metadata=copy.deepcopy(self.metadata, memo),
            _cloning_strategy=self._cloning_strategy
        )


@dataclass
class DatabaseConnection(ConfigurablePrototype):
    """Database connection prototype with connection pooling."""
    
    host: str = "localhost"
    port: int = 5432
    database: str = "default"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    connection_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.metadata['connection_string'] = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build connection string."""
        return f"postgresql://{self.username}@{self.host}:{self.port}/{self.database}"
    
    def _custom_clone(self) -> 'DatabaseConnection':
        """Custom cloning that resets sensitive data."""
        cloned = copy.deepcopy(self)
        cloned.password = ""  # Don't clone passwords
        cloned.metadata['cloned_at'] = self.metadata.get('created_at', '')
        return cloned


@dataclass
class WebServiceConfig(ConfigurablePrototype):
    """Web service configuration prototype."""
    
    base_url: str = "https://api.example.com"
    api_key: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    headers: Dict[str, str] = field(default_factory=dict)
    endpoints: Dict[str, str] = field(default_factory=dict)
    
    def add_endpoint(self, name: str, path: str) -> None:
        """Add an API endpoint."""
        self.endpoints[name] = path
    
    def add_header(self, key: str, value: str) -> None:
        """Add a header."""
        self.headers[key] = value
    
    def _custom_clone(self) -> 'WebServiceConfig':
        """Custom cloning that handles API keys."""
        cloned = copy.deepcopy(self)
        if self.api_key:
            cloned.api_key = "***REDACTED***"
        return cloned


class PrototypeFactory(Generic[T]):
    """
    Generic prototype factory with context manager support.
    """
    
    def __init__(self, prototype_class: Type[T]):
        self.prototype_class = prototype_class
        self.prototypes: Dict[str, T] = {}
        self.creation_count = 0
    
    def register(self, name: str, prototype: T) -> None:
        """Register a prototype."""
        self.prototypes[name] = prototype
    
    def create(self, name: str, **kwargs) -> T:
        """Create instance from prototype."""
        if name not in self.prototypes:
            raise ValueError(f"Prototype '{name}' not found")
        
        prototype = self.prototypes[name]
        instance = prototype.clone()
        
        # Apply any overrides
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.creation_count += 1
        return instance
    
    def list_prototypes(self) -> list[str]:
        """List available prototypes."""
        return list(self.prototypes.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get factory statistics."""
        return {
            'total_prototypes': len(self.prototypes),
            'total_created': self.creation_count,
            'prototype_names': list(self.prototypes.keys())
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass


class SmartPrototypeManager:
    """
    Advanced prototype manager with serialization support.
    """
    
    def __init__(self):
        self._prototypes: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, prototype: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a prototype with metadata."""
        self._prototypes[name] = prototype
        self._metadata[name] = metadata or {}
        self._metadata[name]['registered_at'] = self._get_timestamp()
    
    def create(self, name: str, **kwargs) -> Any:
        """Create instance from prototype."""
        if name not in self._prototypes:
            raise ValueError(f"Prototype '{name}' not found")
        
        prototype = self._prototypes[name]
        
        # Use different cloning methods based on object type
        if hasattr(prototype, 'clone'):
            instance = prototype.clone()
        elif hasattr(prototype, '__deepcopy__'):
            instance = copy.deepcopy(prototype)
        else:
            instance = copy.copy(prototype)
        
        # Apply kwargs
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        return instance
    
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get prototype metadata."""
        return self._metadata.get(name, {})
    
    def save_to_file(self, filename: str) -> None:
        """Save prototypes to file."""
        data = {
            'prototypes': {},
            'metadata': self._metadata
        }
        
        for name, prototype in self._prototypes.items():
            try:
                # Try to serialize with pickle
                data['prototypes'][name] = pickle.dumps(prototype).hex()
            except Exception:
                # Fall back to JSON if possible
                if hasattr(prototype, '__dict__'):
                    data['prototypes'][name] = prototype.__dict__
                else:
                    data['prototypes'][name] = str(prototype)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """Load prototypes from file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self._metadata = data.get('metadata', {})
        
        for name, prototype_data in data.get('prototypes', {}).items():
            try:
                # Try to deserialize with pickle
                if isinstance(prototype_data, str) and len(prototype_data) % 2 == 0:
                    prototype = pickle.loads(bytes.fromhex(prototype_data))
                    self._prototypes[name] = prototype
            except Exception:
                # Handle other formats as needed
                pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def clone_with_modifications(self, name: str, modifications: Dict[str, Any]) -> Any:
        """Clone prototype with specific modifications."""
        instance = self.create(name)
        
        for key, value in modifications.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        return instance
    
    def bulk_create(self, name: str, count: int, **kwargs) -> list[Any]:
        """Create multiple instances from prototype."""
        instances = []
        for i in range(count):
            instance = self.create(name, **kwargs)
            instances.append(instance)
        return instances


class PrototypeRegistry(metaclass=PrototypeMeta):
    """
    Registry for automatically managed prototypes.
    """
    
    _auto_register = True
    
    def __init__(self):
        self.instances: Dict[str, Any] = {}
    
    @classmethod
    def get_instance(cls, name: str) -> Any:
        """Get or create instance."""
        if name not in cls._registry:
            raise ValueError(f"Prototype '{name}' not registered")
        
        prototype_class = cls._registry[name]
        return prototype_class()
    
    @classmethod
    def create_from_registry(cls, name: str) -> Any:
        """Create instance from registry."""
        prototype = cls.get_instance(name)
        return prototype.clone()


def create_prototype_factory(prototype_class: Type[T]) -> PrototypeFactory[T]:
    """Factory function to create prototype factories."""
    return PrototypeFactory(prototype_class)


def main():
    """
    Demonstrate optimized prototype implementations.
    """
    print("=== Optimized Prototype Pattern Demo ===")
    
    # Test configurable prototypes
    print("\n1. Configurable Prototypes:")
    
    # Create database connection prototype
    db_prototype = DatabaseConnection(
        name="Production DB",
        host="prod-db.example.com",
        port=5432,
        database="myapp",
        username="app_user",
        password="secret123",
        pool_size=20
    )
    
    print(f"Original DB: {db_prototype.name} at {db_prototype.host}")
    
    # Clone with different strategies
    db_prototype.set_cloning_strategy(CloningStrategy.CUSTOM)
    db_clone = db_prototype.clone()
    db_clone.name = "Development DB"
    db_clone.host = "dev-db.example.com"
    
    print(f"Cloned DB: {db_clone.name} at {db_clone.host}")
    print(f"Password cloned: {db_clone.password}")  # Should be empty due to custom cloning
    
    # Test web service config
    print("\n2. Web Service Configuration:")
    
    api_config = WebServiceConfig(
        name="Payment API",
        base_url="https://api.payment.com",
        api_key="secret_key_123",
        timeout=60
    )
    
    api_config.add_endpoint("charge", "/v1/charges")
    api_config.add_endpoint("refund", "/v1/refunds")
    api_config.add_header("Accept", "application/json")
    
    # Clone API config
    api_clone = api_config.clone()
    api_clone.name = "Test Payment API"
    api_clone.base_url = "https://test-api.payment.com"
    
    print(f"Original API: {api_config.name} - {api_config.base_url}")
    print(f"Original API Key: {api_config.api_key}")
    print(f"Cloned API: {api_clone.name} - {api_clone.base_url}")
    print(f"Cloned API Key: {api_clone.api_key}")
    
    # Test prototype factory
    print("\n3. Prototype Factory:")
    
    with create_prototype_factory(DatabaseConnection) as factory:
        # Register prototypes
        factory.register("postgres", DatabaseConnection(
            name="PostgreSQL Template",
            host="localhost",
            port=5432,
            database="template"
        ))
        
        factory.register("mysql", DatabaseConnection(
            name="MySQL Template",
            host="localhost",
            port=3306,
            database="template"
        ))
        
        # Create instances
        pg_instance = factory.create("postgres", database="myapp", username="user1")
        mysql_instance = factory.create("mysql", database="webapp", username="user2")
        
        print(f"PostgreSQL instance: {pg_instance.name} - {pg_instance.database}")
        print(f"MySQL instance: {mysql_instance.name} - {mysql_instance.database}")
        
        # Show statistics
        stats = factory.get_statistics()
        print(f"Factory stats: {stats}")
    
    # Test smart prototype manager
    print("\n4. Smart Prototype Manager:")
    
    manager = SmartPrototypeManager()
    
    # Register various prototypes
    manager.register("db_config", db_prototype, {"type": "database", "environment": "production"})
    manager.register("api_config", api_config, {"type": "api", "service": "payment"})
    
    # Create instances
    new_db = manager.create("db_config", name="Staging DB", host="staging-db.example.com")
    new_api = manager.create("api_config", name="Staging API", base_url="https://staging-api.payment.com")
    
    print(f"New DB: {new_db.name} at {new_db.host}")
    print(f"New API: {new_api.name} at {new_api.base_url}")
    
    # Show metadata
    db_metadata = manager.get_metadata("db_config")
    print(f"DB metadata: {db_metadata}")
    
    # Test bulk creation
    print("\n5. Bulk Creation:")
    
    bulk_dbs = manager.bulk_create("db_config", 3, name="Bulk DB")
    for i, db in enumerate(bulk_dbs):
        print(f"Bulk DB {i+1}: {db.name} at {db.host}")
    
    # Test clone with modifications
    print("\n6. Clone with Modifications:")
    
    modified_api = manager.clone_with_modifications("api_config", {
        "name": "Modified API",
        "timeout": 120,
        "base_url": "https://modified-api.example.com"
    })
    
    print(f"Modified API: {modified_api.name} - timeout: {modified_api.timeout}")
    
    # Test protocol usage
    print("\n7. Protocol Usage:")
    
    def process_prototype(proto: Prototype) -> Prototype:
        """Function that works with any prototype."""
        return proto.clone()
    
    # Different types can be processed
    cloned_db = process_prototype(db_prototype)
    cloned_api = process_prototype(api_config)
    
    print(f"Protocol cloned DB: {cloned_db.name}")
    print(f"Protocol cloned API: {cloned_api.name}")
    
    # Test serialization
    print("\n8. Serialization:")
    
    try:
        # Save prototypes to file
        manager.save_to_file("prototypes.json")
        print("Prototypes saved to file")
        
        # Load into new manager
        new_manager = SmartPrototypeManager()
        new_manager.load_from_file("prototypes.json")
        print("Prototypes loaded from file")
        
    except Exception as e:
        print(f"Serialization test failed: {e}")
    
    # Demonstrate cloning validation
    print("\n9. Cloning Validation:")
    
    @dataclass
    class ValidatedPrototype(ConfigurablePrototype):
        value: int = 0
        
        @validate_clone
        def clone(self) -> 'ValidatedPrototype':
            return copy.deepcopy(self)
    
    validated = ValidatedPrototype(name="Validated", value=42)
    validated_clone = validated.clone()
    
    print(f"Validated original: {validated.name} = {validated.value}")
    print(f"Validated clone: {validated_clone.name} = {validated_clone.value}")
    print(f"Different objects: {validated is not validated_clone}")
    
    # Show performance benefits
    print("\n10. Performance Benefits:")
    import time
    
    # Measure creation time
    start_time = time.time()
    for _ in range(100):
        clone = db_prototype.clone()
    clone_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(100):
        new_db = DatabaseConnection(
            name="New DB",
            host="localhost",
            port=5432,
            database="test"
        )
    creation_time = time.time() - start_time
    
    print(f"100 clones took: {clone_time:.4f} seconds")
    print(f"100 new objects took: {creation_time:.4f} seconds")
    print(f"Cloning is {creation_time/clone_time:.2f}x faster")


if __name__ == "__main__":
    main()