"""
Prototype Design Pattern - Gang of Four Implementation

Intent: Specify the kinds of objects to create using a prototypical instance,
and create new objects by copying this prototype.

Structure:
- Prototype: declares an interface for cloning itself
- ConcretePrototype: implements an operation for cloning itself
- Client: creates a new object by asking a prototype to clone itself
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import copy


class Prototype(ABC):
    """
    The Prototype interface declares the cloning methods. In most
    cases, it's a single "clone" method.
    """
    
    @abstractmethod
    def clone(self) -> 'Prototype':
        """Create a copy of the current object."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the object."""
        pass


class ConcretePrototype1(Prototype):
    """
    ConcretePrototype1 implements the Prototype interface.
    """
    
    def __init__(self, value: str):
        self.value = value
        self.list_value: List[str] = []
        self.dict_value: Dict[str, Any] = {}
    
    def clone(self) -> 'ConcretePrototype1':
        """
        Create a deep copy of the current object.
        Python's copy module provides convenient methods for this.
        """
        # Create a new instance
        cloned = ConcretePrototype1(self.value)
        
        # Deep copy mutable attributes
        cloned.list_value = copy.deepcopy(self.list_value)
        cloned.dict_value = copy.deepcopy(self.dict_value)
        
        return cloned
    
    def add_to_list(self, item: str) -> None:
        """Add an item to the list."""
        self.list_value.append(item)
    
    def set_dict_value(self, key: str, value: Any) -> None:
        """Set a dictionary value."""
        self.dict_value[key] = value
    
    def __str__(self) -> str:
        return f"ConcretePrototype1(value={self.value}, list={self.list_value}, dict={self.dict_value})"


class ConcretePrototype2(Prototype):
    """
    ConcretePrototype2 implements the Prototype interface differently.
    """
    
    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.nested_object: Dict[str, Any] = {"level": 1, "data": []}
    
    def clone(self) -> 'ConcretePrototype2':
        """
        Alternative implementation using copy.deepcopy directly.
        """
        return copy.deepcopy(self)
    
    def add_nested_data(self, data: Any) -> None:
        """Add data to nested object."""
        self.nested_object["data"].append(data)
    
    def increase_level(self) -> None:
        """Increase the nested level."""
        self.nested_object["level"] += 1
    
    def __str__(self) -> str:
        return f"ConcretePrototype2(number={self.number}, name={self.name}, nested={self.nested_object})"


class ComplexPrototype(Prototype):
    """
    A more complex prototype that demonstrates handling of various data types.
    """
    
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.attributes: Dict[str, Any] = {}
        self.components: List[Prototype] = []
        self.references: Dict[str, Prototype] = {}
    
    def clone(self) -> 'ComplexPrototype':
        """
        Complex cloning that handles nested prototypes.
        """
        # Create new instance
        cloned = ComplexPrototype(self.id, self.name)
        
        # Deep copy attributes
        cloned.attributes = copy.deepcopy(self.attributes)
        
        # Clone nested prototypes
        cloned.components = [component.clone() for component in self.components]
        cloned.references = {key: prototype.clone() for key, prototype in self.references.items()}
        
        return cloned
    
    def add_attribute(self, key: str, value: Any) -> None:
        """Add an attribute."""
        self.attributes[key] = value
    
    def add_component(self, component: Prototype) -> None:
        """Add a component prototype."""
        self.components.append(component)
    
    def add_reference(self, key: str, prototype: Prototype) -> None:
        """Add a reference to another prototype."""
        self.references[key] = prototype
    
    def __str__(self) -> str:
        return (f"ComplexPrototype(id={self.id}, name={self.name}, "
                f"attributes={len(self.attributes)}, components={len(self.components)}, "
                f"references={len(self.references)})")


class PrototypeManager:
    """
    A registry that manages prototypes and provides convenient access to them.
    """
    
    def __init__(self):
        self._prototypes: Dict[str, Prototype] = {}
    
    def register_prototype(self, name: str, prototype: Prototype) -> None:
        """Register a prototype with a name."""
        self._prototypes[name] = prototype
    
    def unregister_prototype(self, name: str) -> None:
        """Unregister a prototype."""
        if name in self._prototypes:
            del self._prototypes[name]
    
    def get_prototype(self, name: str) -> Prototype:
        """Get a clone of the registered prototype."""
        if name not in self._prototypes:
            raise ValueError(f"Prototype '{name}' not found")
        
        return self._prototypes[name].clone()
    
    def list_prototypes(self) -> List[str]:
        """List all registered prototype names."""
        return list(self._prototypes.keys())
    
    def has_prototype(self, name: str) -> bool:
        """Check if a prototype is registered."""
        return name in self._prototypes


def main():
    """
    Client code that demonstrates the Prototype pattern.
    """
    print("=== Prototype Pattern Demo ===")
    
    # Test ConcretePrototype1
    print("\n--- ConcretePrototype1 ---")
    prototype1 = ConcretePrototype1("Original")
    prototype1.add_to_list("item1")
    prototype1.add_to_list("item2")
    prototype1.set_dict_value("key1", "value1")
    
    print(f"Original: {prototype1}")
    
    # Clone the prototype
    cloned1 = prototype1.clone()
    print(f"Cloned: {cloned1}")
    
    # Modify the original
    prototype1.add_to_list("item3")
    prototype1.set_dict_value("key2", "value2")
    
    # Modify the clone
    cloned1.add_to_list("cloned_item")
    cloned1.set_dict_value("cloned_key", "cloned_value")
    
    print(f"After modifications:")
    print(f"Original: {prototype1}")
    print(f"Cloned: {cloned1}")
    
    # Test ConcretePrototype2
    print("\n--- ConcretePrototype2 ---")
    prototype2 = ConcretePrototype2(42, "Test")
    prototype2.add_nested_data("data1")
    prototype2.add_nested_data("data2")
    prototype2.increase_level()
    
    print(f"Original: {prototype2}")
    
    cloned2 = prototype2.clone()
    print(f"Cloned: {cloned2}")
    
    # Modify both
    prototype2.add_nested_data("original_data")
    prototype2.increase_level()
    
    cloned2.add_nested_data("cloned_data")
    cloned2.number = 100
    
    print(f"After modifications:")
    print(f"Original: {prototype2}")
    print(f"Cloned: {cloned2}")
    
    # Test ComplexPrototype
    print("\n--- ComplexPrototype ---")
    complex_prototype = ComplexPrototype(1, "Complex")
    complex_prototype.add_attribute("color", "blue")
    complex_prototype.add_attribute("size", "large")
    
    # Add components
    component1 = ConcretePrototype1("component1")
    component1.add_to_list("comp_item1")
    complex_prototype.add_component(component1)
    
    component2 = ConcretePrototype2(99, "component2")
    component2.add_nested_data("comp_data")
    complex_prototype.add_component(component2)
    
    # Add references
    ref_prototype = ConcretePrototype1("reference")
    ref_prototype.add_to_list("ref_item")
    complex_prototype.add_reference("main_ref", ref_prototype)
    
    print(f"Original complex: {complex_prototype}")
    
    # Clone complex prototype
    cloned_complex = complex_prototype.clone()
    print(f"Cloned complex: {cloned_complex}")
    
    # Modify original components
    complex_prototype.components[0].add_to_list("modified_item")
    complex_prototype.references["main_ref"].add_to_list("modified_ref")
    
    # Modify cloned components
    cloned_complex.components[0].add_to_list("cloned_modified_item")
    cloned_complex.references["main_ref"].add_to_list("cloned_modified_ref")
    
    print(f"After component modifications:")
    print(f"Original first component: {complex_prototype.components[0]}")
    print(f"Cloned first component: {cloned_complex.components[0]}")
    print(f"Original reference: {complex_prototype.references['main_ref']}")
    print(f"Cloned reference: {cloned_complex.references['main_ref']}")
    
    # Test PrototypeManager
    print("\n--- PrototypeManager ---")
    manager = PrototypeManager()
    
    # Register prototypes
    manager.register_prototype("simple", ConcretePrototype1("template"))
    manager.register_prototype("numbered", ConcretePrototype2(0, "template"))
    manager.register_prototype("complex", ComplexPrototype(0, "template"))
    
    print(f"Registered prototypes: {manager.list_prototypes()}")
    
    # Create objects from prototypes
    simple_obj = manager.get_prototype("simple")
    simple_obj.value = "from_manager"
    simple_obj.add_to_list("manager_item")
    
    numbered_obj = manager.get_prototype("numbered")
    numbered_obj.number = 555
    numbered_obj.name = "from_manager"
    
    complex_obj = manager.get_prototype("complex")
    complex_obj.id = 999
    complex_obj.name = "from_manager"
    complex_obj.add_attribute("source", "manager")
    
    print(f"Created from manager:")
    print(f"  Simple: {simple_obj}")
    print(f"  Numbered: {numbered_obj}")
    print(f"  Complex: {complex_obj}")
    
    # Create multiple instances
    print("\n--- Multiple Instances ---")
    instances = []
    for i in range(3):
        instance = manager.get_prototype("simple")
        instance.value = f"instance_{i}"
        instance.add_to_list(f"item_{i}")
        instances.append(instance)
    
    for i, instance in enumerate(instances):
        print(f"Instance {i}: {instance}")
    
    # Demonstrate the benefit of the pattern
    print("\n--- Pattern Benefits ---")
    print("Benefits of Prototype Pattern:")
    print("1. Avoid expensive object creation")
    print("2. Create objects without knowing their exact class")
    print("3. Add/remove objects at runtime")
    print("4. Configure objects with varying compositions")
    
    # Performance comparison (conceptual)
    print("\nPerformance benefit example:")
    print("- Creating complex objects from scratch: expensive")
    print("- Cloning pre-configured prototypes: fast")
    
    # Show different configurations
    base_prototype = ConcretePrototype1("base")
    base_prototype.add_to_list("base_item")
    base_prototype.set_dict_value("base_key", "base_value")
    
    # Create variations
    variations = []
    for i in range(3):
        variation = base_prototype.clone()
        variation.value = f"variation_{i}"
        variation.add_to_list(f"variation_item_{i}")
        variations.append(variation)
    
    print(f"\nBase prototype: {base_prototype}")
    for i, variation in enumerate(variations):
        print(f"Variation {i}: {variation}")


if __name__ == "__main__":
    main()