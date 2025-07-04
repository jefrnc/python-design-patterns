"""
Decorator Design Pattern - Gang of Four Implementation

Intent: Attach additional responsibilities to an object dynamically. 
Decorators provide a flexible alternative to subclassing for extending functionality.

Structure:
- Component: defines the interface for objects that can have responsibilities added to them dynamically
- ConcreteComponent: defines an object to which additional responsibilities can be attached
- Decorator: maintains a reference to a Component object and defines an interface that conforms to Component's interface
- ConcreteDecorator: adds responsibilities to the component
"""

from abc import ABC, abstractmethod


class Component(ABC):
    """
    The base Component interface defines operations that can be altered by
    decorators.
    """
    
    @abstractmethod
    def operation(self) -> str:
        pass


class ConcreteComponent(Component):
    """
    Concrete Components provide default implementations for the operations.
    There might be several variations of these classes.
    """
    
    def operation(self) -> str:
        return "ConcreteComponent"


class Decorator(Component):
    """
    The base Decorator class follows the same interface as the other components.
    The primary purpose of this class is to define the wrapping interface for
    all concrete decorators. The default implementation of the wrapping code
    might include a field for storing a wrapped component and the means to
    initialize it.
    """
    
    def __init__(self, component: Component) -> None:
        self._component = component
    
    @property
    def component(self) -> Component:
        """
        The Decorator delegates all work to the wrapped component.
        """
        return self._component
    
    def operation(self) -> str:
        return self._component.operation()


class ConcreteDecoratorA(Decorator):
    """
    Concrete Decorators call the wrapped object and alter its result in some way.
    """
    
    def operation(self) -> str:
        return f"ConcreteDecoratorA({self.component.operation()})"


class ConcreteDecoratorB(Decorator):
    """
    Decorators can execute their behavior either before or after the call to a
    wrapped object.
    """
    
    def operation(self) -> str:
        return f"ConcreteDecoratorB({self.component.operation()})"


def client_code(component: Component) -> None:
    """
    The client code works with all objects using the Component interface. This
    way it can stay independent of the concrete classes of components it works
    with.
    """
    print(f"RESULT: {component.operation()}")


def main():
    """
    This way the client code can support both simple components...
    """
    print("=== Decorator Pattern Demo ===")
    
    # Simple component
    simple = ConcreteComponent()
    print("Client: I've got a simple component:")
    client_code(simple)
    print()
    
    # Decorated component
    print("Client: Now I've got a decorated component:")
    
    # Decorator A
    decorator1 = ConcreteDecoratorA(simple)
    client_code(decorator1)
    print()
    
    # Decorator B
    decorator2 = ConcreteDecoratorB(simple)
    client_code(decorator2)
    print()
    
    # Multiple decorators
    print("Client: Now I've got a component with multiple decorators:")
    decorator3 = ConcreteDecoratorB(ConcreteDecoratorA(simple))
    client_code(decorator3)


if __name__ == "__main__":
    main()