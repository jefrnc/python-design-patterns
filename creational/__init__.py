"""
Creational Design Patterns

Creational patterns deal with object creation mechanisms, trying to create 
objects in a manner suitable to the situation. The basic form of object 
creation could result in design problems or in added complexity to the design.

This package contains all 5 creational patterns from the Gang of Four:
- Abstract Factory: Create families of related objects
- Builder: Construct complex objects step-by-step
- Factory Method: Create objects without specifying exact classes
- Prototype: Create objects by cloning existing instances
- Singleton: Ensure only one instance exists
"""

__version__ = "1.0.0"
__author__ = "Python Design Patterns Contributors"

# Available patterns in this package
PATTERNS = [
    "abstract_factory",
    "builder",
    "factory_method",
    "prototype", 
    "singleton"
]

# Implementation tiers available for each pattern
TIERS = ["basic", "practical", "advanced"]