"""
Abstract Factory Design Pattern - Gang of Four Implementation

Intent: Provide an interface for creating families of related or dependent objects
without specifying their concrete classes.

Structure:
- AbstractFactory: declares an interface for operations that create abstract products
- ConcreteFactory: implements the operations to create concrete product objects
- AbstractProduct: declares an interface for a type of product object
- ConcreteProduct: defines a product object to be created by the corresponding concrete factory
- Client: uses only interfaces declared by AbstractFactory and AbstractProduct classes
"""

from abc import ABC, abstractmethod
from typing import Protocol


class AbstractProductA(ABC):
    """
    Each distinct product of a product family should have a base interface.
    All variants of the product must implement this interface.
    """
    
    @abstractmethod
    def useful_function_a(self) -> str:
        """Return the result of the product A."""
        pass


class ConcreteProductA1(AbstractProductA):
    """
    Concrete Products are created by corresponding Concrete Factories.
    """
    
    def useful_function_a(self) -> str:
        return "The result of the product A1."


class ConcreteProductA2(AbstractProductA):
    """
    Concrete Products are created by corresponding Concrete Factories.
    """
    
    def useful_function_a(self) -> str:
        return "The result of the product A2."


class AbstractProductB(ABC):
    """
    Here's the base interface of another product. All products can interact
    with each other, but proper interaction is possible only between products
    of the same concrete variant.
    """
    
    @abstractmethod
    def useful_function_b(self) -> str:
        """Return the result of the product B."""
        pass
    
    @abstractmethod
    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        """
        Product B is able to do its own thing and collaborate with the ProductA.
        
        The Abstract Factory makes sure that all products it creates are of the
        same variant and thus, compatible.
        """
        pass


class ConcreteProductB1(AbstractProductB):
    """
    Concrete Products are created by corresponding Concrete Factories.
    """
    
    def useful_function_b(self) -> str:
        return "The result of the product B1."
    
    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        """
        The variant, Product B1, is only able to work correctly with the
        variant, Product A1. Nevertheless, it accepts any instance of
        AbstractProductA as an argument.
        """
        result = collaborator.useful_function_a()
        return f"The result of the B1 collaborating with ({result})"


class ConcreteProductB2(AbstractProductB):
    """
    Concrete Products are created by corresponding Concrete Factories.
    """
    
    def useful_function_b(self) -> str:
        return "The result of the product B2."
    
    def another_useful_function_b(self, collaborator: AbstractProductA) -> str:
        """
        The variant, Product B2, is only able to work correctly with the
        variant, Product A2. Nevertheless, it accepts any instance of
        AbstractProductA as an argument.
        """
        result = collaborator.useful_function_a()
        return f"The result of the B2 collaborating with ({result})"


class AbstractFactory(ABC):
    """
    The Abstract Factory interface declares a set of methods that return
    different abstract products. These products are called a family and are
    related by a high-level theme or concept. Products of one family are
    usually able to collaborate among themselves. A family of products may
    have several variants, but the products of one variant are incompatible
    with products of another.
    """
    
    @abstractmethod
    def create_product_a(self) -> AbstractProductA:
        """Create an abstract product A."""
        pass
    
    @abstractmethod
    def create_product_b(self) -> AbstractProductB:
        """Create an abstract product B."""
        pass


class ConcreteFactory1(AbstractFactory):
    """
    Concrete Factories produce a family of products that belong to a single
    variant. The factory guarantees that resulting products are compatible.
    Note that signatures of the Concrete Factory's methods return an abstract
    product, while inside the method a concrete product is instantiated.
    """
    
    def create_product_a(self) -> AbstractProductA:
        return ConcreteProductA1()
    
    def create_product_b(self) -> AbstractProductB:
        return ConcreteProductB1()


class ConcreteFactory2(AbstractFactory):
    """
    Each Concrete Factory has a corresponding product variant.
    """
    
    def create_product_a(self) -> AbstractProductA:
        return ConcreteProductA2()
    
    def create_product_b(self) -> AbstractProductB:
        return ConcreteProductB2()


def client_code(factory: AbstractFactory) -> None:
    """
    The client code works with factories and products only through abstract
    types: AbstractFactory and AbstractProduct. This lets you pass any factory
    or product subclass to the client code without breaking it.
    """
    product_a = factory.create_product_a()
    product_b = factory.create_product_b()
    
    print(product_b.useful_function_b())
    print(product_b.another_useful_function_b(product_a))


def main():
    """
    The client code.
    """
    print("=== Abstract Factory Pattern Demo ===")
    
    print("\nClient: Testing client code with the first factory type:")
    client_code(ConcreteFactory1())
    
    print("\nClient: Testing the same client code with the second factory type:")
    client_code(ConcreteFactory2())
    
    # Direct usage example
    print("\n=== Direct Usage Example ===")
    
    # Create factory 1 products
    factory1 = ConcreteFactory1()
    product_a1 = factory1.create_product_a()
    product_b1 = factory1.create_product_b()
    
    print(f"Factory 1 - Product A: {product_a1.useful_function_a()}")
    print(f"Factory 1 - Product B: {product_b1.useful_function_b()}")
    print(f"Factory 1 - Collaboration: {product_b1.another_useful_function_b(product_a1)}")
    
    # Create factory 2 products
    factory2 = ConcreteFactory2()
    product_a2 = factory2.create_product_a()
    product_b2 = factory2.create_product_b()
    
    print(f"\nFactory 2 - Product A: {product_a2.useful_function_a()}")
    print(f"Factory 2 - Product B: {product_b2.useful_function_b()}")
    print(f"Factory 2 - Collaboration: {product_b2.another_useful_function_b(product_a2)}")
    
    # Cross-variant collaboration (works but may not be intended)
    print(f"\nCross-variant collaboration:")
    print(f"B1 with A2: {product_b1.another_useful_function_b(product_a2)}")
    print(f"B2 with A1: {product_b2.another_useful_function_b(product_a1)}")


if __name__ == "__main__":
    main()