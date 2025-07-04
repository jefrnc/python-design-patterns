"""
Builder Design Pattern - Gang of Four Implementation

Intent: Separate the construction of a complex object from its representation
so that the same construction process can create different representations.

Structure:
- Builder: specifies an abstract interface for creating parts of a Product object
- ConcreteBuilder: constructs and assembles parts of the product by implementing the Builder interface
- Director: constructs an object using the Builder interface
- Product: represents the complex object under construction
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class Product:
    """
    The Product class represents the complex object under construction.
    Products from different builders don't have to belong to the same class hierarchy.
    """
    
    def __init__(self):
        self.parts: List[str] = []
    
    def add_part(self, part: str) -> None:
        """Add a part to the product."""
        self.parts.append(part)
    
    def list_parts(self) -> str:
        """List all parts of the product."""
        return f"Product parts: {', '.join(self.parts)}"


class Builder(ABC):
    """
    The Builder interface specifies methods for creating the different parts
    of the Product objects.
    """
    
    @property
    @abstractmethod
    def product(self) -> Product:
        """Return the product being built."""
        pass
    
    @abstractmethod
    def produce_part_a(self) -> None:
        """Build part A."""
        pass
    
    @abstractmethod
    def produce_part_b(self) -> None:
        """Build part B."""
        pass
    
    @abstractmethod
    def produce_part_c(self) -> None:
        """Build part C."""
        pass


class ConcreteBuilder1(Builder):
    """
    The Concrete Builder classes follow the Builder interface and provide
    specific implementations of the building steps. Your program may have
    several variations of Builders, implemented differently.
    """
    
    def __init__(self) -> None:
        """
        A fresh builder instance should contain a blank product object, which
        is used in further assembly.
        """
        self.reset()
    
    def reset(self) -> None:
        """Reset the builder to start building a new product."""
        self._product = Product()
    
    @property
    def product(self) -> Product:
        """
        Concrete Builders are supposed to provide their own methods for
        retrieving results. That's because various types of builders may
        create entirely different products that don't follow the same
        interface. Therefore, such methods cannot be declared in the base
        Builder interface (at least in a statically typed programming
        language).
        
        Usually, after returning the end result to the client, a builder
        instance is expected to be ready to start producing another product.
        That's why it's a usual practice to call the reset method at the end
        of the `get_product` method body. However, this behavior is not
        mandatory, and you can make your builders wait for an explicit reset
        call from the client code before disposing of the previous result.
        """
        product = self._product
        self.reset()
        return product
    
    def produce_part_a(self) -> None:
        """Build part A with specific implementation."""
        self._product.add_part("PartA1")
    
    def produce_part_b(self) -> None:
        """Build part B with specific implementation."""
        self._product.add_part("PartB1")
    
    def produce_part_c(self) -> None:
        """Build part C with specific implementation."""
        self._product.add_part("PartC1")


class ConcreteBuilder2(Builder):
    """
    Another concrete builder that creates a different representation
    of the same product.
    """
    
    def __init__(self) -> None:
        self.reset()
    
    def reset(self) -> None:
        """Reset the builder to start building a new product."""
        self._product = Product()
    
    @property
    def product(self) -> Product:
        """Return the product and reset the builder."""
        product = self._product
        self.reset()
        return product
    
    def produce_part_a(self) -> None:
        """Build part A with alternative implementation."""
        self._product.add_part("PartA2")
    
    def produce_part_b(self) -> None:
        """Build part B with alternative implementation."""
        self._product.add_part("PartB2")
    
    def produce_part_c(self) -> None:
        """Build part C with alternative implementation."""
        self._product.add_part("PartC2")


class Director:
    """
    The Director is only responsible for executing the building steps in a
    particular sequence. It is helpful when producing products according to a
    specific order or configuration. Strictly speaking, the Director class is
    optional, since the client can control builders directly.
    """
    
    def __init__(self) -> None:
        self._builder: Optional[Builder] = None
    
    @property
    def builder(self) -> Builder:
        """Get the current builder."""
        if self._builder is None:
            raise ValueError("Builder not set")
        return self._builder
    
    @builder.setter
    def builder(self, builder: Builder) -> None:
        """Set the builder to use."""
        self._builder = builder
    
    def build_minimal_viable_product(self) -> None:
        """Build a minimal product with just part A."""
        self.builder.produce_part_a()
    
    def build_full_featured_product(self) -> None:
        """Build a full product with all parts."""
        self.builder.produce_part_a()
        self.builder.produce_part_b()
        self.builder.produce_part_c()
    
    def build_custom_product(self, parts: List[str]) -> None:
        """Build a custom product with specified parts."""
        part_methods = {
            'A': self.builder.produce_part_a,
            'B': self.builder.produce_part_b,
            'C': self.builder.produce_part_c
        }
        
        for part in parts:
            if part in part_methods:
                part_methods[part]()
            else:
                print(f"Warning: Unknown part '{part}' requested")


def main():
    """
    The client code creates a builder object, passes it to the director and
    then initiates the construction process. The end result is retrieved from
    the builder object.
    """
    print("=== Builder Pattern Demo ===")
    
    # Create director
    director = Director()
    
    # Test with first builder
    print("\n--- ConcreteBuilder1 ---")
    builder1 = ConcreteBuilder1()
    director.builder = builder1
    
    print("Standard basic product:")
    director.build_minimal_viable_product()
    print(builder1.product.list_parts())
    
    print("Standard full featured product:")
    director.build_full_featured_product()
    print(builder1.product.list_parts())
    
    # Test with second builder
    print("\n--- ConcreteBuilder2 ---")
    builder2 = ConcreteBuilder2()
    director.builder = builder2
    
    print("Standard basic product:")
    director.build_minimal_viable_product()
    print(builder2.product.list_parts())
    
    print("Standard full featured product:")
    director.build_full_featured_product()
    print(builder2.product.list_parts())
    
    # Test custom products
    print("\n--- Custom Products ---")
    director.builder = builder1
    
    print("Custom product with parts A and C:")
    director.build_custom_product(['A', 'C'])
    print(builder1.product.list_parts())
    
    print("Custom product with parts B and A:")
    director.build_custom_product(['B', 'A'])
    print(builder1.product.list_parts())
    
    # Builder can be used without director
    print("\n--- Direct Builder Usage ---")
    builder3 = ConcreteBuilder1()
    
    print("Building manually without director:")
    builder3.produce_part_b()
    builder3.produce_part_a()
    builder3.produce_part_c()
    builder3.produce_part_b()  # Add part B again
    
    manual_product = builder3.product
    print(manual_product.list_parts())
    
    # Demonstrate different representations
    print("\n--- Different Representations ---")
    
    def create_product_with_builder(builder: Builder, product_type: str) -> Product:
        """Helper function to create products with different builders."""
        if product_type == "minimal":
            builder.produce_part_a()
        elif product_type == "standard":
            builder.produce_part_a()
            builder.produce_part_b()
        elif product_type == "deluxe":
            builder.produce_part_a()
            builder.produce_part_b()
            builder.produce_part_c()
        
        return builder.product
    
    # Create same product types with different builders
    for product_type in ["minimal", "standard", "deluxe"]:
        print(f"\n{product_type.capitalize()} products:")
        
        # Builder 1 version
        b1 = ConcreteBuilder1()
        product1 = create_product_with_builder(b1, product_type)
        print(f"  Builder1: {product1.list_parts()}")
        
        # Builder 2 version
        b2 = ConcreteBuilder2()
        product2 = create_product_with_builder(b2, product_type)
        print(f"  Builder2: {product2.list_parts()}")


if __name__ == "__main__":
    main()