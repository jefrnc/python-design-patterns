"""
Behavioral Design Patterns

Behavioral patterns are concerned with algorithms and the assignment of 
responsibilities between objects. They characterize complex control flow 
that's difficult to follow at run-time.

This package contains all 11 behavioral patterns from the Gang of Four:
- Chain of Responsibility: Pass requests along a chain of handlers
- Command: Encapsulate requests as objects
- Interpreter: Define grammar and interpret sentences  
- Iterator: Access elements sequentially
- Mediator: Define how objects interact
- Memento: Capture and restore object state
- Observer: Notify multiple objects about state changes
- State: Alter behavior when state changes
- Strategy: Make algorithms interchangeable
- Template Method: Define algorithm skeleton in base class
- Visitor: Define new operations without changing structure
"""

__version__ = "1.0.0"
__author__ = "Python Design Patterns Contributors"

# Available patterns in this package
PATTERNS = [
    "chain_of_responsibility",
    "command", 
    "interpreter",
    "iterator",
    "mediator",
    "memento",
    "observer",
    "state",
    "strategy", 
    "template_method",
    "visitor"
]

# Implementation tiers available for each pattern
TIERS = ["basic", "practical", "advanced"]