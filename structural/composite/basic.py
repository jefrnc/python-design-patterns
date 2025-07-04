"""
Composite Design Pattern - Gang of Four Implementation

Intent: Compose objects into tree structures to represent part-whole hierarchies.
Composite lets clients treat individual objects and compositions of objects uniformly.

Structure:
- Component: declares the interface for objects in the composition
- Leaf: represents leaf objects in the composition
- Composite: defines behavior for components having children and stores child components
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Component(ABC):
    """
    The base Component class declares common operations for both simple and
    complex objects of a composition.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._parent: Optional['Component'] = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def parent(self) -> Optional['Component']:
        return self._parent
    
    @parent.setter
    def parent(self, parent: Optional['Component']):
        self._parent = parent
    
    def add(self, component: 'Component') -> None:
        """
        Add a component to this component.
        """
        pass
    
    def remove(self, component: 'Component') -> None:
        """
        Remove a component from this component.
        """
        pass
    
    def is_composite(self) -> bool:
        """
        Check if this component is a composite.
        """
        return False
    
    @abstractmethod
    def operation(self) -> str:
        """
        The Component declares an operation that should be implemented by both
        simple and complex components.
        """
        pass


class Leaf(Component):
    """
    The Leaf class represents the end objects of a composition. A leaf can't
    have any children.
    """
    
    def operation(self) -> str:
        return f"Leaf({self.name})"


class Composite(Component):
    """
    The Composite class represents the complex components that may have children.
    Usually, the Composite objects delegate the actual work to their children
    and then "sum-up" the result.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[Component] = []
    
    def add(self, component: Component) -> None:
        """
        Add a component to this composite.
        """
        self._children.append(component)
        component.parent = self
    
    def remove(self, component: Component) -> None:
        """
        Remove a component from this composite.
        """
        if component in self._children:
            self._children.remove(component)
            component.parent = None
    
    def is_composite(self) -> bool:
        return True
    
    def operation(self) -> str:
        """
        The Composite executes its primary logic in a particular way. It
        traverses recursively through all its children, collecting and
        summing their results.
        """
        results = []
        for child in self._children:
            results.append(child.operation())
        
        children_result = ", ".join(results)
        return f"Composite({self.name})[{children_result}]"
    
    def get_children(self) -> List[Component]:
        """
        Get all children of this composite.
        """
        return self._children.copy()


def client_code(component: Component) -> None:
    """
    The client code works with all of the components via the base interface.
    """
    print(f"RESULT: {component.operation()}")


def client_code2(component1: Component, component2: Component) -> None:
    """
    Thanks to the fact that the child-management operations are declared in the
    base Component class, the client code can work with any component, simple or
    complex, without depending on their concrete classes.
    """
    if component1.is_composite():
        component1.add(component2)
    
    print(f"RESULT: {component1.operation()}")


def main():
    """
    The client code demonstrates how to work with the Composite pattern.
    """
    print("=== Composite Pattern Demo ===")
    
    # Simple components
    print("\n1. Simple leaf components:")
    leaf1 = Leaf("Leaf1")
    leaf2 = Leaf("Leaf2")
    
    client_code(leaf1)
    client_code(leaf2)
    
    # Composite components
    print("\n2. Composite components:")
    tree = Composite("Root")
    branch1 = Composite("Branch1")
    branch2 = Composite("Branch2")
    
    # Build tree structure
    tree.add(branch1)
    tree.add(branch2)
    
    branch1.add(Leaf("Leaf1"))
    branch1.add(Leaf("Leaf2"))
    
    branch2.add(Leaf("Leaf3"))
    branch2.add(Leaf("Leaf4"))
    
    print("Tree structure:")
    client_code(tree)
    
    # Dynamic composition
    print("\n3. Dynamic composition:")
    new_leaf = Leaf("NewLeaf")
    client_code2(tree, new_leaf)
    
    # Nested composites
    print("\n4. Nested composites:")
    complex_tree = Composite("ComplexRoot")
    
    # First branch
    branch_a = Composite("BranchA")
    branch_a.add(Leaf("LeafA1"))
    branch_a.add(Leaf("LeafA2"))
    
    # Second branch with sub-branches
    branch_b = Composite("BranchB")
    sub_branch_b1 = Composite("SubBranchB1")
    sub_branch_b2 = Composite("SubBranchB2")
    
    sub_branch_b1.add(Leaf("LeafB1"))
    sub_branch_b1.add(Leaf("LeafB2"))
    
    sub_branch_b2.add(Leaf("LeafB3"))
    sub_branch_b2.add(Leaf("LeafB4"))
    
    branch_b.add(sub_branch_b1)
    branch_b.add(sub_branch_b2)
    
    # Build complex tree
    complex_tree.add(branch_a)
    complex_tree.add(branch_b)
    complex_tree.add(Leaf("DirectLeaf"))
    
    print("Complex tree structure:")
    client_code(complex_tree)
    
    # Test parent relationships
    print("\n5. Parent relationships:")
    print(f"Branch A parent: {branch_a.parent.name if branch_a.parent else 'None'}")
    print(f"Sub-branch B1 parent: {sub_branch_b1.parent.name if sub_branch_b1.parent else 'None'}")
    
    # Test removal
    print("\n6. Removing components:")
    print(f"Before removal: {len(complex_tree.get_children())} children")
    complex_tree.remove(branch_a)
    print(f"After removal: {len(complex_tree.get_children())} children")
    print("Complex tree after removal:")
    client_code(complex_tree)


if __name__ == "__main__":
    main()