"""
Factory Method Design Pattern - Gang of Four Implementation

Intent: Define an interface for creating an object, but let subclasses decide 
which class to instantiate. Factory Method lets a class defer instantiation 
to subclasses.

Structure:
- Product: defines the interface of objects the factory method creates
- ConcreteProduct: implements the Product interface
- Creator: declares the factory method, which returns an object of type Product
- ConcreteCreator: overrides the factory method to return an instance of a ConcreteProduct
"""

from abc import ABC, abstractmethod
from typing import List


class Product(ABC):
    """
    The Product interface declares the operations that all concrete products
    must implement.
    """
    
    @abstractmethod
    def operation(self) -> str:
        """
        All products must implement this operation.
        """
        pass


class ConcreteProductA(Product):
    """
    Concrete Products provide various implementations of the Product interface.
    """
    
    def operation(self) -> str:
        return "Result of ConcreteProductA"


class ConcreteProductB(Product):
    """
    Concrete Products provide various implementations of the Product interface.
    """
    
    def operation(self) -> str:
        return "Result of ConcreteProductB"


class Creator(ABC):
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """
    
    @abstractmethod
    def factory_method(self) -> Product:
        """
        Note that the Creator may also provide some default implementation of
        the factory method.
        """
        pass
    
    def some_operation(self) -> str:
        """
        Also note that, despite its name, the Creator's primary responsibility
        is not creating products. Usually, it contains some core business logic
        that relies on Product objects, returned by the factory method.
        Subclasses can indirectly change that business logic by overriding the
        factory method and returning a different type of product from it.
        """
        # Call the factory method to create a Product object.
        product = self.factory_method()
        
        # Now, use the product.
        result = f"Creator: The same creator's code has just worked with {product.operation()}"
        return result


class ConcreteCreatorA(Creator):
    """
    Concrete Creators override the factory method in order to change the
    resulting product's type.
    """
    
    def factory_method(self) -> Product:
        return ConcreteProductA()


class ConcreteCreatorB(Creator):
    """
    Concrete Creators override the factory method in order to change the
    resulting product's type.
    """
    
    def factory_method(self) -> Product:
        return ConcreteProductB()


def client_code(creator: Creator) -> None:
    """
    The client code works with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    print(f"Client: I'm not aware of the creator's class, but it still works.")
    print(f"{creator.some_operation()}")


def main():
    """
    The Application picks a creator's type depending on the configuration or
    environment.
    """
    print("=== Factory Method Pattern Demo ===")
    
    # Create an array of creators
    creators: List[Creator] = [ConcreteCreatorA(), ConcreteCreatorB()]
    
    # Iterate over creators and create products
    for creator in creators:
        print(f"\nTesting {creator.__class__.__name__}:")
        client_code(creator)
        
        # Direct product creation
        product = creator.factory_method()
        print(f"Created product: {product.__class__.__name__}")
        print(f"Product operation: {product.operation()}")


if __name__ == "__main__":
    main()