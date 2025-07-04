"""
Adapter Design Pattern - Gang of Four Implementation

Intent: Convert the interface of a class into another interface clients expect.
Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

Structure:
- Target: defines the domain-specific interface that Client uses
- Client: collaborates with objects conforming to the Target interface
- Adaptee: defines an existing interface that needs adapting
- Adapter: adapts the interface of Adaptee to the Target interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Target(ABC):
    """
    The Target defines the domain-specific interface used by the client code.
    """
    
    @abstractmethod
    def request(self) -> str:
        """The target interface method."""
        pass


class Adaptee:
    """
    The Adaptee contains some useful behavior, but its interface is incompatible
    with the existing client code. The Adaptee needs some adaptation before the
    client code can use it.
    """
    
    def specific_request(self) -> str:
        """
        The Adaptee has a specific interface that is incompatible with the Target.
        """
        return "Special behavior from Adaptee"


class Adapter(Target):
    """
    The Adapter makes the Adaptee's interface compatible with the Target's
    interface via composition.
    """
    
    def __init__(self, adaptee: Adaptee):
        self._adaptee = adaptee
    
    def request(self) -> str:
        """
        The Adapter translates the Target's interface to the Adaptee's interface.
        """
        result = self._adaptee.specific_request()
        return f"Adapter: (TRANSLATED) {result}"


class ClassAdapter(Target, Adaptee):
    """
    The Class Adapter uses inheritance to adapt the Adaptee's interface
    to the Target's interface. This is an alternative to composition.
    """
    
    def request(self) -> str:
        """
        The Class Adapter calls the Adaptee's method directly through inheritance.
        """
        result = self.specific_request()
        return f"ClassAdapter: (INHERITED) {result}"


# More complex example with multiple methods
class ModernInterface(ABC):
    """
    Modern interface that clients expect to use.
    """
    
    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data in modern format."""
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """Get processing status."""
        pass
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the processor."""
        pass


class LegacyDataProcessor:
    """
    Legacy data processor with incompatible interface.
    """
    
    def __init__(self):
        self.is_configured = False
        self.last_operation = "none"
    
    def process_legacy_data(self, data_string: str) -> str:
        """Process data in legacy string format."""
        if not self.is_configured:
            raise RuntimeError("Legacy processor not configured")
        
        self.last_operation = "process"
        # Simulate legacy processing
        processed = f"LEGACY_PROCESSED: {data_string.upper()}"
        return processed
    
    def get_operation_status(self) -> str:
        """Get status of last operation."""
        return f"Legacy status: {self.last_operation}"
    
    def setup_processor(self, config_string: str) -> None:
        """Setup processor with configuration string."""
        # Parse legacy configuration format
        self.is_configured = True
        self.last_operation = "configured"


class LegacyAdapter(ModernInterface):
    """
    Adapter that makes legacy processor compatible with modern interface.
    """
    
    def __init__(self, legacy_processor: LegacyDataProcessor):
        self._legacy_processor = legacy_processor
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert modern data format to legacy format, process it,
        and convert the result back to modern format.
        """
        # Convert modern dict to legacy string format
        data_string = self._dict_to_legacy_string(data)
        
        # Process using legacy processor
        result_string = self._legacy_processor.process_legacy_data(data_string)
        
        # Convert legacy result back to modern format
        result_dict = self._legacy_string_to_dict(result_string)
        
        return result_dict
    
    def get_status(self) -> str:
        """Get status from legacy processor and format for modern interface."""
        legacy_status = self._legacy_processor.get_operation_status()
        return f"Adapted: {legacy_status}"
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Convert modern configuration to legacy format."""
        config_string = self._dict_to_legacy_config(config)
        self._legacy_processor.setup_processor(config_string)
    
    def _dict_to_legacy_string(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to legacy string format."""
        items = []
        for key, value in data.items():
            items.append(f"{key}={value}")
        return "|".join(items)
    
    def _legacy_string_to_dict(self, data_string: str) -> Dict[str, Any]:
        """Convert legacy string to dictionary format."""
        result = {"processed": True, "data": data_string}
        return result
    
    def _dict_to_legacy_config(self, config: Dict[str, Any]) -> str:
        """Convert configuration dictionary to legacy format."""
        config_items = []
        for key, value in config.items():
            config_items.append(f"{key}:{value}")
        return ";".join(config_items)


# Two-way adapter example
class TwoWayAdapter(ModernInterface):
    """
    Two-way adapter that can work with both modern and legacy interfaces.
    """
    
    def __init__(self, legacy_processor: LegacyDataProcessor):
        self._legacy_processor = legacy_processor
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data using modern interface."""
        data_string = self._dict_to_legacy_string(data)
        result_string = self._legacy_processor.process_legacy_data(data_string)
        return self._legacy_string_to_dict(result_string)
    
    def get_status(self) -> str:
        """Get status using modern interface."""
        legacy_status = self._legacy_processor.get_operation_status()
        return f"TwoWay: {legacy_status}"
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure using modern interface."""
        config_string = self._dict_to_legacy_config(config)
        self._legacy_processor.setup_processor(config_string)
    
    # Legacy interface methods for backward compatibility
    def process_legacy_data(self, data_string: str) -> str:
        """Process data using legacy interface."""
        return self._legacy_processor.process_legacy_data(data_string)
    
    def get_operation_status(self) -> str:
        """Get status using legacy interface."""
        return self._legacy_processor.get_operation_status()
    
    def setup_processor(self, config_string: str) -> None:
        """Setup using legacy interface."""
        self._legacy_processor.setup_processor(config_string)
    
    def _dict_to_legacy_string(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to legacy string format."""
        items = []
        for key, value in data.items():
            items.append(f"{key}={value}")
        return "|".join(items)
    
    def _legacy_string_to_dict(self, data_string: str) -> Dict[str, Any]:
        """Convert legacy string to dictionary format."""
        result = {"processed": True, "data": data_string}
        return result
    
    def _dict_to_legacy_config(self, config: Dict[str, Any]) -> str:
        """Convert configuration dictionary to legacy format."""
        config_items = []
        for key, value in config.items():
            config_items.append(f"{key}:{value}")
        return ";".join(config_items)


def client_code(target: Target) -> None:
    """
    The client code supports all classes that follow the Target interface.
    """
    result = target.request()
    print(f"Client: {result}")


def modern_client_code(processor: ModernInterface) -> None:
    """
    Client code that works with modern interface.
    """
    # Configure processor
    processor.configure({"mode": "fast", "level": "high"})
    print(f"Configuration status: {processor.get_status()}")
    
    # Process data
    data = {"name": "John", "age": 30, "city": "New York"}
    result = processor.process_data(data)
    print(f"Processing result: {result}")
    print(f"Final status: {processor.get_status()}")


def main():
    """
    The client code.
    """
    print("=== Adapter Pattern Demo ===")
    
    # Simple adapter example
    print("\n--- Simple Adapter ---")
    
    # Client can work with Target objects directly
    print("Client: I can work just fine with Target objects:")
    target = Target()
    # This would fail because Target is abstract
    # client_code(target)
    
    # But client can't work with Adaptee objects directly
    print("\nClient: The Adaptee class has a weird interface.")
    adaptee = Adaptee()
    print(f"Adaptee: {adaptee.specific_request()}")
    
    # However, client can work with Adaptee via Adapter
    print("\nClient: But I can work with it via the Adapter:")
    adapter = Adapter(adaptee)
    client_code(adapter)
    
    # Test class adapter
    print("\nClient: Class Adapter also works:")
    class_adapter = ClassAdapter()
    client_code(class_adapter)
    
    # Complex adapter example
    print("\n--- Complex Adapter Example ---")
    
    # Create legacy processor
    legacy_processor = LegacyDataProcessor()
    
    # Create adapter
    adapter = LegacyAdapter(legacy_processor)
    
    # Client can now use legacy processor via modern interface
    print("Client: Using legacy processor via modern interface:")
    modern_client_code(adapter)
    
    # Two-way adapter example
    print("\n--- Two-Way Adapter Example ---")
    
    # Create two-way adapter
    two_way_adapter = TwoWayAdapter(LegacyDataProcessor())
    
    # Use via modern interface
    print("Using two-way adapter via modern interface:")
    modern_client_code(two_way_adapter)
    
    # Use via legacy interface
    print("\nUsing two-way adapter via legacy interface:")
    two_way_adapter.setup_processor("mode:legacy;level:medium")
    print(f"Legacy status: {two_way_adapter.get_operation_status()}")
    
    legacy_result = two_way_adapter.process_legacy_data("test data")
    print(f"Legacy processing result: {legacy_result}")
    
    # Multiple adapters example
    print("\n--- Multiple Adapters ---")
    
    # Create multiple legacy processors
    processors = [LegacyDataProcessor() for _ in range(3)]
    adapters = [LegacyAdapter(processor) for processor in processors]
    
    # Use all adapters with same modern interface
    test_data = {"message": "Hello", "count": 42}
    
    for i, adapter in enumerate(adapters):
        print(f"\nAdapter {i+1}:")
        adapter.configure({"mode": f"test_{i+1}", "level": "normal"})
        result = adapter.process_data(test_data)
        print(f"  Result: {result}")
        print(f"  Status: {adapter.get_status()}")
    
    # Demonstrate adapter benefits
    print("\n--- Adapter Benefits ---")
    print("Benefits of Adapter Pattern:")
    print("1. Enables incompatible interfaces to work together")
    print("2. Promotes code reuse of existing classes")
    print("3. Separates interface conversion from business logic")
    print("4. Allows gradual migration from legacy systems")
    print("5. Supports both object and class adaptation")
    
    # Show interface compatibility
    print("\n--- Interface Compatibility ---")
    
    def process_with_modern_interface(processors: List[ModernInterface]):
        """Function that works with modern interface."""
        for i, processor in enumerate(processors):
            print(f"Processor {i+1}: {type(processor).__name__}")
            processor.configure({"test": True})
            result = processor.process_data({"test": "data"})
            print(f"  Result: {result}")
    
    # All adapters can be used interchangeably
    mixed_processors = [
        LegacyAdapter(LegacyDataProcessor()),
        TwoWayAdapter(LegacyDataProcessor()),
        LegacyAdapter(LegacyDataProcessor())
    ]
    
    process_with_modern_interface(mixed_processors)


if __name__ == "__main__":
    main()