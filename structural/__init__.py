"""
Structural Design Patterns

Structural patterns are concerned with how classes and objects are composed 
to form larger structures. They help ensure that when one part of a system 
changes, the entire structure doesn't need to change.

This package contains all 7 structural patterns from the Gang of Four:
- Adapter: Allow incompatible interfaces to work together
- Bridge: Separate abstraction from implementation
- Composite: Compose objects into tree structures
- Decorator: Add behavior to objects dynamically
- Facade: Provide simplified interface to complex subsystem
- Flyweight: Minimize memory usage by sharing data
- Proxy: Provide placeholder for another object
"""

__version__ = "1.0.0"
__author__ = "Python Design Patterns Contributors"

# Available patterns in this package
PATTERNS = [
    "adapter",
    "bridge", 
    "composite",
    "decorator",
    "facade",
    "flyweight",
    "proxy"
]

# Implementation tiers available for each pattern
TIERS = ["basic", "practical", "advanced"]