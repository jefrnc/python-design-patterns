"""
Facade Design Pattern - Gang of Four Implementation

Intent: Provide a unified interface to a set of interfaces in a subsystem.
Facade defines a higher-level interface that makes the subsystem easier to use.

Structure:
- Facade: knows which subsystem classes are responsible for a request
- Subsystem classes: implement subsystem functionality and handle work assigned by the Facade
"""

from typing import List, Optional


class SubsystemA:
    """
    The Subsystem can accept requests either from the facade or client directly.
    In any case, to the Subsystem, the Facade is yet another client, and it's
    not a part of the Subsystem.
    """
    
    def operation1(self) -> str:
        return "SubsystemA: Ready!"
    
    def operation_n(self) -> str:
        return "SubsystemA: Go!"


class SubsystemB:
    """
    Some facades can work with multiple subsystems at the same time.
    """
    
    def operation1(self) -> str:
        return "SubsystemB: Get ready!"
    
    def operation_z(self) -> str:
        return "SubsystemB: Fire!"


class SubsystemC:
    """
    Additional subsystem for more complex operations.
    """
    
    def operation1(self) -> str:
        return "SubsystemC: Initializing..."
    
    def operation2(self) -> str:
        return "SubsystemC: Processing..."
    
    def operation3(self) -> str:
        return "SubsystemC: Finalizing..."


class Facade:
    """
    The Facade class provides a simple interface to the complex logic of one or
    several subsystems. The Facade delegates the client requests to the
    appropriate objects within the subsystem. The Facade is also responsible for
    managing their lifecycle. All of this shields the client from the undesired
    complexity of the subsystem.
    """
    
    def __init__(self, subsystem1: Optional[SubsystemA] = None,
                 subsystem2: Optional[SubsystemB] = None,
                 subsystem3: Optional[SubsystemC] = None):
        """
        Depending on your application's needs, you can provide the Facade with
        existing subsystem objects or force the Facade to create them on its own.
        """
        self._subsystem1 = subsystem1 or SubsystemA()
        self._subsystem2 = subsystem2 or SubsystemB()
        self._subsystem3 = subsystem3 or SubsystemC()
    
    def operation(self) -> str:
        """
        The Facade's methods are convenient shortcuts to the sophisticated
        functionality of the subsystems. However, clients get only to a fraction
        of a subsystem's capabilities.
        """
        results = []
        results.append("Facade initializes subsystems:")
        results.append(self._subsystem1.operation1())
        results.append(self._subsystem2.operation1())
        results.append(self._subsystem3.operation1())
        
        results.append("Facade orders subsystems to perform the action:")
        results.append(self._subsystem1.operation_n())
        results.append(self._subsystem2.operation_z())
        results.append(self._subsystem3.operation2())
        
        results.append("Facade finalizes operations:")
        results.append(self._subsystem3.operation3())
        
        return "\n".join(results)
    
    def simple_operation(self) -> str:
        """
        Simple operation that uses only one subsystem.
        """
        return f"Facade simple operation:\n{self._subsystem1.operation1()}"
    
    def complex_operation(self) -> str:
        """
        Complex operation that coordinates multiple subsystems.
        """
        results = []
        results.append("Facade complex operation:")
        results.append(self._subsystem1.operation1())
        results.append(self._subsystem2.operation1())
        results.append(self._subsystem3.operation1())
        results.append(self._subsystem3.operation2())
        results.append(self._subsystem1.operation_n())
        results.append(self._subsystem2.operation_z())
        results.append(self._subsystem3.operation3())
        
        return "\n".join(results)


def client_code(facade: Facade) -> None:
    """
    The client code works with complex subsystems through a simple interface
    provided by the Facade. When a facade manages the lifecycle of the
    subsystem, the client might not even know about the existence of the
    subsystem. This approach lets you keep the complexity under control.
    """
    print(facade.operation())


def main():
    """
    The client code may have some of the subsystem's objects already created.
    In this case, it might be worthwhile to initialize the Facade with these
    objects instead of letting the Facade create new instances.
    """
    print("=== Facade Pattern Demo ===")
    
    # Basic facade usage
    print("\n1. Basic facade operation:")
    facade = Facade()
    client_code(facade)
    
    # Simple operation
    print("\n2. Simple facade operation:")
    print(facade.simple_operation())
    
    # Complex operation
    print("\n3. Complex facade operation:")
    print(facade.complex_operation())
    
    # Client with existing subsystems
    print("\n4. Facade with pre-existing subsystems:")
    subsystem1 = SubsystemA()
    subsystem2 = SubsystemB()
    subsystem3 = SubsystemC()
    
    facade_with_existing = Facade(subsystem1, subsystem2, subsystem3)
    print("Using facade with existing subsystems:")
    client_code(facade_with_existing)
    
    # Demonstrate direct subsystem access vs facade
    print("\n5. Direct subsystem access vs Facade:")
    print("Direct subsystem access (complex):")
    print(f"  {subsystem1.operation1()}")
    print(f"  {subsystem2.operation1()}")
    print(f"  {subsystem3.operation1()}")
    print(f"  {subsystem3.operation2()}")
    print(f"  {subsystem1.operation_n()}")
    print(f"  {subsystem2.operation_z()}")
    print(f"  {subsystem3.operation3()}")
    
    print("\nUsing Facade (simple):")
    print(facade.complex_operation())
    
    # Multiple facades
    print("\n6. Multiple facades for different use cases:")
    facade1 = Facade()
    facade2 = Facade()
    
    print("Facade 1 - Simple operation:")
    print(facade1.simple_operation())
    
    print("\nFacade 2 - Complex operation:")
    print(facade2.complex_operation())


if __name__ == "__main__":
    main()