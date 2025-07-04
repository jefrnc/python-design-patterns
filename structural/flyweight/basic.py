"""
Flyweight Design Pattern - Gang of Four Implementation

Intent: Use sharing to support large numbers of fine-grained objects efficiently.

Structure:
- Flyweight: declares an interface through which flyweights can receive and act on extrinsic state
- ConcreteFlyweight: implements the Flyweight interface and adds storage for intrinsic state
- FlyweightFactory: creates and manages flyweight objects and ensures flyweights are shared properly
- Context: maintains a reference to flyweight(s) and stores extrinsic state
"""

from typing import Dict, List, Tuple
import json


class Flyweight:
    """
    The Flyweight stores a common portion of the state (also called intrinsic
    state) that belongs to multiple real business entities. The Flyweight
    accepts the rest of the state (extrinsic state, unique for each entity) via
    its method parameters.
    """
    
    def __init__(self, shared_state: str):
        self._shared_state = shared_state
    
    def operation(self, unique_state: str) -> str:
        """
        The Flyweight's method accepts the extrinsic state as a parameter and
        uses it along with the intrinsic state to perform some operation.
        """
        s = json.dumps(self._shared_state)
        u = json.dumps(unique_state)
        return f"Flyweight: Displaying shared ({s}) and unique ({u}) state."
    
    @property
    def shared_state(self) -> str:
        return self._shared_state


class FlyweightFactory:
    """
    The Flyweight Factory creates and manages the Flyweight objects. It ensures
    that flyweights are shared correctly. When the client requests a flyweight,
    the factory either returns an existing instance or creates a new one, if it
    doesn't exist yet.
    """
    
    _flyweights: Dict[str, Flyweight] = {}
    
    def __init__(self, initial_flyweights: List[str]):
        for state in initial_flyweights:
            self._flyweights[self._get_key(state)] = Flyweight(state)
    
    def _get_key(self, state: str) -> str:
        """
        Returns a Flyweight's string hash for a given state.
        """
        return state
    
    def get_flyweight(self, shared_state: str) -> Flyweight:
        """
        Returns an existing Flyweight with a given state or creates a new one.
        """
        key = self._get_key(shared_state)
        
        if key not in self._flyweights:
            print(f"FlyweightFactory: Can't find a flyweight, creating new one.")
            self._flyweights[key] = Flyweight(shared_state)
        else:
            print(f"FlyweightFactory: Reusing existing flyweight.")
        
        return self._flyweights[key]
    
    def list_flyweights(self) -> None:
        """
        List all flyweights in the factory.
        """
        count = len(self._flyweights)
        print(f"FlyweightFactory: I have {count} flyweights:")
        for key in self._flyweights.keys():
            print(f"  - {key}")


class Context:
    """
    The Context stores the extrinsic state and maintains a reference to the
    flyweight object. The Context's state can change, but the flyweight's
    intrinsic state must remain constant.
    """
    
    def __init__(self, flyweight: Flyweight, extrinsic_state: str):
        self._flyweight = flyweight
        self._extrinsic_state = extrinsic_state
    
    def operation(self) -> str:
        """
        The Context delegates work to the flyweight object, passing the
        extrinsic state as parameters.
        """
        return self._flyweight.operation(self._extrinsic_state)
    
    @property
    def extrinsic_state(self) -> str:
        return self._extrinsic_state
    
    @extrinsic_state.setter
    def extrinsic_state(self, value: str) -> None:
        self._extrinsic_state = value


def add_car_to_police_database(
    factory: FlyweightFactory, plates: str, owner: str,
    brand: str, model: str, color: str
) -> Context:
    """
    The client code usually creates a bunch of pre-populated flyweights in the
    initialization stage of the application.
    """
    print("\nClient: Adding a car to database.")
    
    # The intrinsic state (shared among cars of the same type)
    shared_state = f"{brand}-{model}-{color}"
    flyweight = factory.get_flyweight(shared_state)
    
    # The extrinsic state (unique for each car)
    extrinsic_state = f"{plates}-{owner}"
    context = Context(flyweight, extrinsic_state)
    
    print(context.operation())
    return context


def main():
    """
    The client code demonstrates the Flyweight pattern usage.
    """
    print("=== Flyweight Pattern Demo ===")
    
    # Initialize factory with some common car types
    print("\n1. Initializing flyweight factory:")
    initial_types = [
        "Chevrolet-Camaro-pink",
        "Mercedes-Benz-C300-black",
        "Mercedes-Benz-C500-red",
        "BMW-M5-red",
        "BMW-X6-white"
    ]
    
    factory = FlyweightFactory(initial_types)
    factory.list_flyweights()
    
    # Add cars to police database
    print("\n2. Adding cars to police database:")
    
    cars = []
    
    # Add existing car types (will reuse flyweights)
    cars.append(add_car_to_police_database(
        factory, "CL234IR", "James Doe", "BMW", "M5", "red"))
    
    cars.append(add_car_to_police_database(
        factory, "CL234IR", "James Doe", "BMW", "X6", "white"))
    
    # Add new car type (will create new flyweight)
    cars.append(add_car_to_police_database(
        factory, "CL234IR", "James Doe", "BMW", "X3", "blue"))
    
    # Add more cars with existing types
    cars.append(add_car_to_police_database(
        factory, "AB123CD", "Jane Smith", "Mercedes-Benz", "C300", "black"))
    
    cars.append(add_car_to_police_database(
        factory, "EF456GH", "Bob Johnson", "Chevrolet", "Camaro", "pink"))
    
    # Show final flyweight count
    print("\n3. Final flyweight factory state:")
    factory.list_flyweights()
    
    # Demonstrate state changes in context
    print("\n4. Changing extrinsic state:")
    print(f"Before: {cars[0].operation()}")
    cars[0].extrinsic_state = "NEW123-John Smith"
    print(f"After:  {cars[0].operation()}")
    
    # Show memory efficiency
    print("\n5. Memory efficiency demonstration:")
    print(f"Total cars: {len(cars)}")
    print(f"Total flyweights: {len(factory._flyweights)}")
    print(f"Memory savings: {len(cars) - len(factory._flyweights)} objects")
    
    # Test flyweight sharing
    print("\n6. Flyweight sharing test:")
    flyweight1 = factory.get_flyweight("BMW-M5-red")
    flyweight2 = factory.get_flyweight("BMW-M5-red")
    
    print(f"Same flyweight object: {flyweight1 is flyweight2}")
    print(f"Flyweight1 ID: {id(flyweight1)}")
    print(f"Flyweight2 ID: {id(flyweight2)}")
    
    # Show operations with different extrinsic states
    print("\n7. Same flyweight, different contexts:")
    context1 = Context(flyweight1, "ABC123-Owner1")
    context2 = Context(flyweight1, "XYZ789-Owner2")
    
    print(context1.operation())
    print(context2.operation())


if __name__ == "__main__":
    main()