"""
Adapter Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Protocol classes for structural typing
- Decorators for automatic adaptation
- Context managers for resource management
- Metaclasses for adapter registration
- Type hints with generics
- Multiple inheritance for mixin adapters
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Dict, Any, Optional, Union, Type, runtime_checkable, Callable
from dataclasses import dataclass, field
from functools import wraps, partial
import inspect
from enum import Enum, auto


# Type variables
T = TypeVar('T')
U = TypeVar('U')


class AdaptationStrategy(Enum):
    """Different adaptation strategies."""
    OBJECT_ADAPTER = auto()
    CLASS_ADAPTER = auto()
    PROTOCOL_ADAPTER = auto()
    DECORATOR_ADAPTER = auto()


@runtime_checkable
class Adaptable(Protocol):
    """Protocol for objects that can be adapted."""
    
    def adapt_to(self, target_type: Type[T]) -> T:
        """Adapt this object to target type."""
        ...


@runtime_checkable
class DataProcessor(Protocol):
    """Protocol for data processing services."""
    
    def process(self, data: Any) -> Any:
        """Process data."""
        ...
    
    def validate(self, data: Any) -> bool:
        """Validate data."""
        ...


@runtime_checkable
class ConfigurableService(Protocol):
    """Protocol for configurable services."""
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the service."""
        ...
    
    def get_status(self) -> str:
        """Get service status."""
        ...


class AdapterMeta(type):
    """
    Metaclass for automatic adapter registration and creation.
    """
    
    _adapters: Dict[str, Type] = {}
    _mappings: Dict[tuple, Type] = {}
    
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Auto-register adapters
        if hasattr(cls, '_adapts_from') and hasattr(cls, '_adapts_to'):
            key = (cls._adapts_from, cls._adapts_to)
            mcs._mappings[key] = cls
            mcs._adapters[name.lower()] = cls
        
        return cls
    
    @classmethod
    def get_adapter(mcs, from_type: Type, to_type: Type) -> Optional[Type]:
        """Get adapter for type conversion."""
        return mcs._mappings.get((from_type, to_type))
    
    @classmethod
    def list_adapters(mcs) -> list[str]:
        """List all registered adapters."""
        return list(mcs._adapters.keys())


def adapter_for(from_type: Type, to_type: Type):
    """Decorator to mark a class as an adapter."""
    def decorator(cls):
        cls._adapts_from = from_type
        cls._adapts_to = to_type
        return cls
    return decorator


def adapt_method(method_mapping: Dict[str, str]):
    """Decorator to adapt method calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get the original method name
            original_method = method_mapping.get(func.__name__)
            
            if original_method and hasattr(self._adaptee, original_method):
                # Call the mapped method on adaptee
                adaptee_method = getattr(self._adaptee, original_method)
                return adaptee_method(*args, **kwargs)
            else:
                # Call the original method
                return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


@dataclass
class AdaptationConfig:
    """Configuration for adaptation behavior."""
    strategy: AdaptationStrategy = AdaptationStrategy.OBJECT_ADAPTER
    method_mappings: Dict[str, str] = field(default_factory=dict)
    attribute_mappings: Dict[str, str] = field(default_factory=dict)
    validation_enabled: bool = True
    auto_configure: bool = True


class GenericAdapter(Generic[T, U]):
    """
    Generic adapter that can adapt between any two types.
    """
    
    def __init__(self, adaptee: T, config: Optional[AdaptationConfig] = None):
        self._adaptee = adaptee
        self._config = config or AdaptationConfig()
        
        if self._config.auto_configure:
            self._auto_configure()
    
    def _auto_configure(self) -> None:
        """Automatically configure method mappings."""
        if not self._config.method_mappings:
            # Try to map methods with similar names
            adaptee_methods = [method for method in dir(self._adaptee) 
                              if not method.startswith('_') and callable(getattr(self._adaptee, method))]
            
            target_methods = [method for method in dir(self) 
                             if not method.startswith('_') and callable(getattr(self, method))]
            
            # Simple name-based mapping
            for target_method in target_methods:
                for adaptee_method in adaptee_methods:
                    if target_method.lower() in adaptee_method.lower() or adaptee_method.lower() in target_method.lower():
                        self._config.method_mappings[target_method] = adaptee_method
                        break
    
    def adapt(self, method_name: str, *args, **kwargs) -> Any:
        """Adapt method call to adaptee."""
        mapped_method = self._config.method_mappings.get(method_name, method_name)
        
        if hasattr(self._adaptee, mapped_method):
            method = getattr(self._adaptee, mapped_method)
            return method(*args, **kwargs)
        else:
            raise AttributeError(f"Adaptee has no method '{mapped_method}'")
    
    def get_adaptee(self) -> T:
        """Get the wrapped adaptee."""
        return self._adaptee
    
    def __getattr__(self, name: str) -> Any:
        """Dynamic attribute access delegation."""
        mapped_attr = self._config.attribute_mappings.get(name, name)
        
        if hasattr(self._adaptee, mapped_attr):
            attr = getattr(self._adaptee, mapped_attr)
            if callable(attr):
                return partial(self.adapt, name)
            return attr
        
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


# Legacy system classes
class LegacyDataService:
    """Legacy data service with old interface."""
    
    def __init__(self):
        self.data_store = {}
        self.is_initialized = False
    
    def initialize_service(self, settings: str) -> None:
        """Initialize with legacy string settings."""
        # Parse legacy settings format: "key1=value1;key2=value2"
        for setting in settings.split(';'):
            if '=' in setting:
                key, value = setting.split('=', 1)
                self.data_store[key.strip()] = value.strip()
        self.is_initialized = True
    
    def process_data_string(self, data_str: str) -> str:
        """Process data in legacy string format."""
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        # Legacy processing: uppercase and add prefix
        return f"LEGACY:{data_str.upper()}"
    
    def validate_string_data(self, data_str: str) -> bool:
        """Validate string data."""
        return isinstance(data_str, str) and len(data_str) > 0
    
    def get_service_info(self) -> str:
        """Get service information."""
        return f"LegacyDataService(initialized={self.is_initialized}, settings={len(self.data_store)})"


class LegacyFileProcessor:
    """Legacy file processor with different interface."""
    
    def __init__(self):
        self.file_cache = {}
        self.settings = {}
    
    def setup(self, config_dict: Dict[str, Any]) -> None:
        """Setup with configuration."""
        self.settings = config_dict.copy()
    
    def process_file_content(self, content: str) -> str:
        """Process file content."""
        # Legacy file processing
        lines = content.split('\n')
        processed_lines = [f"PROCESSED: {line}" for line in lines]
        return '\n'.join(processed_lines)
    
    def is_valid_content(self, content: str) -> bool:
        """Check if content is valid."""
        return content is not None and len(content.strip()) > 0
    
    def status(self) -> str:
        """Get processor status."""
        return f"FileProcessor(settings={len(self.settings)}, cache={len(self.file_cache)})"


# Modern adapters using protocols
@adapter_for(LegacyDataService, DataProcessor)
class LegacyDataAdapter(DataProcessor, metaclass=AdapterMeta):
    """
    Adapter that makes LegacyDataService compatible with DataProcessor protocol.
    """
    
    def __init__(self, legacy_service: LegacyDataService):
        self._legacy_service = legacy_service
        
        # Auto-initialize if not already done
        if not legacy_service.is_initialized:
            legacy_service.initialize_service("mode=adapter;version=1.0")
    
    def process(self, data: Any) -> Any:
        """Process data using legacy service."""
        # Convert data to string format expected by legacy service
        if isinstance(data, dict):
            data_str = str(data)
        elif isinstance(data, (list, tuple)):
            data_str = ','.join(str(item) for item in data)
        else:
            data_str = str(data)
        
        # Process using legacy service
        result = self._legacy_service.process_data_string(data_str)
        
        # Convert result back to appropriate format
        return {"processed_data": result, "source": "legacy_adapter"}
    
    def validate(self, data: Any) -> bool:
        """Validate data using legacy service."""
        data_str = str(data) if data is not None else ""
        return self._legacy_service.validate_string_data(data_str)


@adapter_for(LegacyFileProcessor, DataProcessor)
class LegacyFileAdapter(DataProcessor, ConfigurableService, metaclass=AdapterMeta):
    """
    Adapter that makes LegacyFileProcessor compatible with multiple protocols.
    """
    
    def __init__(self, file_processor: LegacyFileProcessor):
        self._file_processor = file_processor
    
    def process(self, data: Any) -> Any:
        """Process data using file processor."""
        content = str(data) if data is not None else ""
        result = self._file_processor.process_file_content(content)
        return {"processed_content": result, "source": "file_adapter"}
    
    def validate(self, data: Any) -> bool:
        """Validate data using file processor."""
        content = str(data) if data is not None else ""
        return self._file_processor.is_valid_content(content)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure file processor."""
        self._file_processor.setup(config)
    
    def get_status(self) -> str:
        """Get processor status."""
        return self._file_processor.status()


class ProtocolAdapterFactory:
    """
    Factory for creating protocol adapters dynamically.
    """
    
    @staticmethod
    def create_adapter(adaptee: Any, target_protocol: Type[T]) -> T:
        """Create adapter for target protocol."""
        adaptee_type = type(adaptee)
        
        # Check if we have a registered adapter
        adapter_class = AdapterMeta.get_adapter(adaptee_type, target_protocol)
        
        if adapter_class:
            return adapter_class(adaptee)
        
        # Create dynamic adapter
        return ProtocolAdapterFactory._create_dynamic_adapter(adaptee, target_protocol)
    
    @staticmethod
    def _create_dynamic_adapter(adaptee: Any, target_protocol: Type[T]) -> T:
        """Create dynamic adapter using protocol inspection."""
        class DynamicAdapter:
            def __init__(self, adaptee):
                self._adaptee = adaptee
            
            def __getattr__(self, name):
                # Try to find matching method in adaptee
                if hasattr(self._adaptee, name):
                    return getattr(self._adaptee, name)
                
                # Try common variations
                variations = [
                    name.replace('_', ''),
                    name.lower(),
                    name.upper(),
                    f"get_{name}",
                    f"set_{name}",
                    f"{name}_data",
                    f"process_{name}"
                ]
                
                for variation in variations:
                    if hasattr(self._adaptee, variation):
                        attr = getattr(self._adaptee, variation)
                        if callable(attr):
                            return attr
                        return lambda: attr
                
                raise AttributeError(f"No suitable method found for '{name}'")
        
        return DynamicAdapter(adaptee)


class AdapterContext:
    """
    Context manager for adapter lifecycle management.
    """
    
    def __init__(self, adaptee: Any, target_protocol: Type[T], config: Optional[AdaptationConfig] = None):
        self.adaptee = adaptee
        self.target_protocol = target_protocol
        self.config = config or AdaptationConfig()
        self.adapter: Optional[T] = None
    
    def __enter__(self) -> T:
        """Create and configure adapter."""
        self.adapter = ProtocolAdapterFactory.create_adapter(self.adaptee, self.target_protocol)
        
        # Configure if adapter supports it
        if hasattr(self.adapter, 'configure') and self.config.auto_configure:
            default_config = {"context_managed": True, "auto_cleanup": True}
            self.adapter.configure(default_config)
        
        return self.adapter
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup adapter."""
        if self.adapter and hasattr(self.adapter, 'cleanup'):
            self.adapter.cleanup()
        
        self.adapter = None


def adapt_to_protocol(target_protocol: Type[T]):
    """Decorator to automatically adapt return values to protocol."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # If result doesn't implement protocol, try to adapt it
            if not isinstance(result, target_protocol):
                try:
                    result = ProtocolAdapterFactory.create_adapter(result, target_protocol)
                except Exception:
                    pass  # Return original result if adaptation fails
            
            return result
        
        return wrapper
    return decorator


class SmartAdapter(Generic[T]):
    """
    Smart adapter that learns method mappings.
    """
    
    def __init__(self, adaptee: T):
        self._adaptee = adaptee
        self._method_cache: Dict[str, str] = {}
        self._call_history: Dict[str, int] = {}
    
    def __getattr__(self, name: str) -> Any:
        """Smart attribute resolution with learning."""
        # Check cache first
        if name in self._method_cache:
            cached_method = self._method_cache[name]
            if hasattr(self._adaptee, cached_method):
                return getattr(self._adaptee, cached_method)
        
        # Try to find matching method
        found_method = self._find_method(name)
        
        if found_method:
            # Cache the mapping
            self._method_cache[name] = found_method
            self._call_history[name] = self._call_history.get(name, 0) + 1
            return getattr(self._adaptee, found_method)
        
        raise AttributeError(f"Could not adapt method '{name}' for {type(self._adaptee).__name__}")
    
    def _find_method(self, target_method: str) -> Optional[str]:
        """Find best matching method in adaptee."""
        adaptee_methods = [method for method in dir(self._adaptee) 
                          if not method.startswith('_') and callable(getattr(self._adaptee, method))]
        
        # Exact match
        if target_method in adaptee_methods:
            return target_method
        
        # Fuzzy matching
        for method in adaptee_methods:
            if target_method.lower() in method.lower() or method.lower() in target_method.lower():
                return method
        
        # Pattern-based matching
        patterns = [
            f"get_{target_method}",
            f"set_{target_method}",
            f"{target_method}_data",
            f"process_{target_method}",
            target_method.replace('_', ''),
            target_method.upper(),
            target_method.lower()
        ]
        
        for pattern in patterns:
            if pattern in adaptee_methods:
                return pattern
        
        return None
    
    def get_learned_mappings(self) -> Dict[str, str]:
        """Get learned method mappings."""
        return self._method_cache.copy()
    
    def get_usage_statistics(self) -> Dict[str, int]:
        """Get method usage statistics."""
        return self._call_history.copy()


def main():
    """
    Demonstrate optimized adapter implementations.
    """
    print("=== Optimized Adapter Pattern Demo ===")
    
    # Test protocol-based adapters
    print("\n1. Protocol-Based Adapters:")
    
    legacy_service = LegacyDataService()
    data_adapter = LegacyDataAdapter(legacy_service)
    
    # Test DataProcessor protocol
    test_data = {"user": "john", "action": "login", "timestamp": "2021-01-01"}
    
    print(f"Original data: {test_data}")
    print(f"Validation: {data_adapter.validate(test_data)}")
    
    result = data_adapter.process(test_data)
    print(f"Processed result: {result}")
    
    # Test file processor adapter
    print("\n2. Multi-Protocol Adapter:")
    
    file_processor = LegacyFileProcessor()
    file_adapter = LegacyFileAdapter(file_processor)
    
    # Configure through ConfigurableService protocol
    file_adapter.configure({"mode": "production", "cache_size": 1000})
    print(f"Status: {file_adapter.get_status()}")
    
    # Process through DataProcessor protocol
    file_content = "Line 1\nLine 2\nLine 3"
    file_result = file_adapter.process(file_content)
    print(f"File processing result: {file_result}")
    
    # Test adapter factory
    print("\n3. Adapter Factory:")
    
    # Create adapter dynamically
    dynamic_adapter = ProtocolAdapterFactory.create_adapter(legacy_service, DataProcessor)
    
    print(f"Dynamic adapter type: {type(dynamic_adapter).__name__}")
    
    dynamic_result = dynamic_adapter.process(["item1", "item2", "item3"])
    print(f"Dynamic processing result: {dynamic_result}")
    
    # Test context manager
    print("\n4. Adapter Context Manager:")
    
    with AdapterContext(file_processor, ConfigurableService) as adapter:
        adapter.configure({"context": "test", "managed": True})
        status = adapter.get_status()
        print(f"Context-managed adapter status: {status}")
    
    # Test smart adapter
    print("\n5. Smart Adapter with Learning:")
    
    smart_adapter = SmartAdapter(legacy_service)
    
    # These calls will trigger method learning
    try:
        # This should map to process_data_string
        result1 = smart_adapter.process("test data")
        print(f"Smart adapter result 1: {result1}")
    except Exception as e:
        print(f"Smart adapter error: {e}")
    
    try:
        # This should map to validate_string_data
        result2 = smart_adapter.validate("test data")
        print(f"Smart adapter result 2: {result2}")
    except Exception as e:
        print(f"Smart adapter error: {e}")
    
    print(f"Learned mappings: {smart_adapter.get_learned_mappings()}")
    print(f"Usage statistics: {smart_adapter.get_usage_statistics()}")
    
    # Test generic adapter
    print("\n6. Generic Adapter:")
    
    config = AdaptationConfig(
        method_mappings={
            "process": "process_data_string",
            "validate": "validate_string_data",
            "status": "get_service_info"
        }
    )
    
    generic_adapter = GenericAdapter(legacy_service, config)
    
    try:
        generic_result = generic_adapter.process("generic test")
        print(f"Generic adapter result: {generic_result}")
    except Exception as e:
        print(f"Generic adapter error: {e}")
    
    # Test adapter decorator
    print("\n7. Adapter Decorator:")
    
    @adapt_to_protocol(DataProcessor)
    def get_legacy_processor():
        return LegacyDataService()
    
    decorated_result = get_legacy_processor()
    print(f"Decorated result type: {type(decorated_result).__name__}")
    
    if hasattr(decorated_result, 'process'):
        decorated_process_result = decorated_result.process("decorated test")
        print(f"Decorated processing result: {decorated_process_result}")
    
    # Test adapter registry
    print("\n8. Adapter Registry:")
    
    print(f"Registered adapters: {AdapterMeta.list_adapters()}")
    
    # Get adapter from registry
    registry_adapter_class = AdapterMeta.get_adapter(LegacyDataService, DataProcessor)
    if registry_adapter_class:
        registry_adapter = registry_adapter_class(LegacyDataService())
        registry_result = registry_adapter.process("registry test")
        print(f"Registry adapter result: {registry_result}")
    
    # Demonstrate protocol checking
    print("\n9. Protocol Checking:")
    
    def process_with_any_processor(processor: DataProcessor, data: Any) -> Any:
        """Function that works with any DataProcessor."""
        if processor.validate(data):
            return processor.process(data)
        else:
            return {"error": "Invalid data"}
    
    # All adapters can be used interchangeably
    processors = [data_adapter, file_adapter, dynamic_adapter]
    test_data_list = ["test1", {"key": "value"}, ["item1", "item2"]]
    
    for i, processor in enumerate(processors):
        data = test_data_list[i % len(test_data_list)]
        result = process_with_any_processor(processor, data)
        print(f"Processor {i+1} result: {result}")
    
    # Show performance benefits
    print("\n10. Performance Benefits:")
    
    print("Benefits of optimized adapters:")
    print("- Protocol-based typing for better IDE support")
    print("- Automatic method mapping reduces boilerplate")
    print("- Context managers for proper resource handling")
    print("- Smart adapters that learn from usage patterns")
    print("- Generic adapters for quick prototyping")
    print("- Decorator-based adaptation for return values")
    print("- Registry system for reusable adapters")


if __name__ == "__main__":
    main()