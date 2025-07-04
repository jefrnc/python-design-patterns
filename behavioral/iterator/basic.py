"""
Iterator Design Pattern - Gang of Four Implementation

Intent: Provide a way to access the elements of an aggregate object sequentially
without exposing its underlying representation.

Structure:
- Iterator: defines an interface for accessing and traversing elements
- ConcreteIterator: implements the Iterator interface and keeps track of current position
- Aggregate: defines an interface for creating an Iterator object
- ConcreteAggregate: implements the Iterator creation interface
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Generic, TypeVar

T = TypeVar('T')


class Iterator(ABC, Generic[T]):
    """
    The Iterator interface declares the operations required for traversing a collection.
    """
    
    @abstractmethod
    def __next__(self) -> T:
        """
        Return the next element in the iteration.
        """
        pass
    
    def __iter__(self):
        """
        Return the iterator object itself.
        """
        return self


class Aggregate(ABC, Generic[T]):
    """
    The Aggregate interface declares one or several methods for getting
    iterators compatible with the collection.
    """
    
    @abstractmethod
    def create_iterator(self) -> Iterator[T]:
        """
        Create and return an iterator for this aggregate.
        """
        pass


class ConcreteIterator(Iterator[T]):
    """
    Concrete Iterators implement various traversal algorithms. These classes
    store the current traversal position at all times.
    """
    
    def __init__(self, collection: 'ConcreteAggregate[T]', reverse: bool = False):
        self._collection = collection
        self._reverse = reverse
        self._position = -1 if reverse else 0
    
    def __next__(self) -> T:
        """
        The __next__() method must return the next item in the sequence. On
        reaching the end, and in subsequent calls, it must raise StopIteration.
        """
        try:
            if self._reverse:
                value = self._collection[self._position]
                self._position -= 1
            else:
                value = self._collection[self._position]
                self._position += 1
        except IndexError:
            raise StopIteration()
        
        return value


class ConcreteAggregate(Aggregate[T]):
    """
    Concrete Aggregates provide one or several methods for retrieving fresh
    iterator instances, compatible with the collection class.
    """
    
    def __init__(self, collection: List[T] = None):
        self._collection = collection or []
    
    def __iter__(self) -> Iterator[T]:
        """
        The __iter__() method returns the iterator object itself, by default we
        return the forward iterator.
        """
        return self.create_iterator()
    
    def create_iterator(self) -> Iterator[T]:
        """
        Create a forward iterator.
        """
        return ConcreteIterator(self)
    
    def create_reverse_iterator(self) -> Iterator[T]:
        """
        Create a reverse iterator.
        """
        return ConcreteIterator(self, reverse=True)
    
    def __getitem__(self, index: int) -> T:
        """
        Allow indexing access to the collection.
        """
        return self._collection[index]
    
    def __len__(self) -> int:
        """
        Return the length of the collection.
        """
        return len(self._collection)
    
    def add_item(self, item: T) -> None:
        """
        Add an item to the collection.
        """
        self._collection.append(item)
    
    def remove_item(self, item: T) -> bool:
        """
        Remove an item from the collection.
        """
        try:
            self._collection.remove(item)
            return True
        except ValueError:
            return False


# More advanced example: Tree Iterator
class TreeNode(Generic[T]):
    """
    A simple tree node class.
    """
    
    def __init__(self, value: T):
        self.value = value
        self.children: List['TreeNode[T]'] = []
    
    def add_child(self, child: 'TreeNode[T]') -> None:
        """
        Add a child node.
        """
        self.children.append(child)
    
    def __str__(self) -> str:
        return str(self.value)


class TreeIterator(Iterator[T]):
    """
    Iterator for tree traversal (depth-first).
    """
    
    def __init__(self, root: TreeNode[T]):
        self._stack: List[TreeNode[T]] = [root] if root else []
    
    def __next__(self) -> T:
        if not self._stack:
            raise StopIteration()
        
        node = self._stack.pop()
        
        # Add children to stack in reverse order for correct traversal
        for child in reversed(node.children):
            self._stack.append(child)
        
        return node.value


class BreadthFirstTreeIterator(Iterator[T]):
    """
    Iterator for tree traversal (breadth-first).
    """
    
    def __init__(self, root: TreeNode[T]):
        self._queue: List[TreeNode[T]] = [root] if root else []
    
    def __next__(self) -> T:
        if not self._queue:
            raise StopIteration()
        
        node = self._queue.pop(0)  # Remove from front (queue behavior)
        
        # Add children to queue
        for child in node.children:
            self._queue.append(child)
        
        return node.value


class Tree(Aggregate[T]):
    """
    Tree aggregate that can create different types of iterators.
    """
    
    def __init__(self, root: TreeNode[T] = None):
        self._root = root
    
    def create_iterator(self) -> Iterator[T]:
        """
        Create a depth-first iterator.
        """
        return TreeIterator(self._root)
    
    def create_breadth_first_iterator(self) -> Iterator[T]:
        """
        Create a breadth-first iterator.
        """
        return BreadthFirstTreeIterator(self._root)
    
    def set_root(self, root: TreeNode[T]) -> None:
        """
        Set the root node of the tree.
        """
        self._root = root
    
    def get_root(self) -> Optional[TreeNode[T]]:
        """
        Get the root node of the tree.
        """
        return self._root


# Matrix Iterator Example
class MatrixIterator(Iterator[T]):
    """
    Iterator for 2D matrix traversal.
    """
    
    def __init__(self, matrix: List[List[T]], row_wise: bool = True):
        self._matrix = matrix
        self._row_wise = row_wise
        self._row = 0
        self._col = 0
        self._rows = len(matrix)
        self._cols = len(matrix[0]) if matrix else 0
    
    def __next__(self) -> T:
        if self._row_wise:
            return self._next_row_wise()
        else:
            return self._next_column_wise()
    
    def _next_row_wise(self) -> T:
        """
        Traverse row by row (left to right, top to bottom).
        """
        if self._row >= self._rows:
            raise StopIteration()
        
        value = self._matrix[self._row][self._col]
        
        self._col += 1
        if self._col >= self._cols:
            self._col = 0
            self._row += 1
        
        return value
    
    def _next_column_wise(self) -> T:
        """
        Traverse column by column (top to bottom, left to right).
        """
        if self._col >= self._cols:
            raise StopIteration()
        
        value = self._matrix[self._row][self._col]
        
        self._row += 1
        if self._row >= self._rows:
            self._row = 0
            self._col += 1
        
        return value


class Matrix(Aggregate[T]):
    """
    Matrix aggregate that supports different iteration patterns.
    """
    
    def __init__(self, data: List[List[T]]):
        self._data = data
    
    def create_iterator(self) -> Iterator[T]:
        """
        Create a row-wise iterator.
        """
        return MatrixIterator(self._data, row_wise=True)
    
    def create_column_iterator(self) -> Iterator[T]:
        """
        Create a column-wise iterator.
        """
        return MatrixIterator(self._data, row_wise=False)
    
    def get_data(self) -> List[List[T]]:
        """
        Get the matrix data.
        """
        return self._data


# Range Iterator (like Python's range)
class RangeIterator(Iterator[int]):
    """
    Iterator that generates a range of numbers.
    """
    
    def __init__(self, start: int, stop: int, step: int = 1):
        self._current = start
        self._stop = stop
        self._step = step
    
    def __next__(self) -> int:
        if (self._step > 0 and self._current >= self._stop) or \
           (self._step < 0 and self._current <= self._stop):
            raise StopIteration()
        
        value = self._current
        self._current += self._step
        return value


class Range(Aggregate[int]):
    """
    Range aggregate that generates sequences of numbers.
    """
    
    def __init__(self, start: int, stop: int, step: int = 1):
        self._start = start
        self._stop = stop
        self._step = step
    
    def create_iterator(self) -> Iterator[int]:
        """
        Create a range iterator.
        """
        return RangeIterator(self._start, self._stop, self._step)


# Filtered Iterator
class FilteredIterator(Iterator[T]):
    """
    Iterator that filters elements based on a predicate.
    """
    
    def __init__(self, iterator: Iterator[T], predicate: callable):
        self._iterator = iterator
        self._predicate = predicate
    
    def __next__(self) -> T:
        while True:
            try:
                item = next(self._iterator)
                if self._predicate(item):
                    return item
            except StopIteration:
                raise StopIteration()


def main():
    """
    The client code demonstrates the Iterator pattern.
    """
    print("=== Iterator Pattern Demo ===")
    
    # Basic iterator usage
    print("\n1. Basic Concrete Iterator:")
    
    collection = ConcreteAggregate([1, 2, 3, 4, 5])
    
    print("Forward iteration:")
    for item in collection:
        print(f"  {item}")
    
    print("Reverse iteration:")
    reverse_iterator = collection.create_reverse_iterator()
    for item in reverse_iterator:
        print(f"  {item}")
    
    # Manual iteration
    print("\nManual iteration:")
    iterator = collection.create_iterator()
    try:
        while True:
            item = next(iterator)
            print(f"  {item}")
    except StopIteration:
        print("  End of iteration")
    
    # Tree iteration
    print("\n2. Tree Iterator:")
    
    # Build a tree
    #       A
    #      / \\
    #     B   C
    #    / \\   \\
    #   D   E   F
    
    root = TreeNode("A")
    child_b = TreeNode("B")
    child_c = TreeNode("C")
    child_d = TreeNode("D")
    child_e = TreeNode("E")
    child_f = TreeNode("F")
    
    root.add_child(child_b)
    root.add_child(child_c)
    child_b.add_child(child_d)
    child_b.add_child(child_e)
    child_c.add_child(child_f)
    
    tree = Tree(root)
    
    print("Depth-first traversal:")
    for value in tree.create_iterator():
        print(f"  {value}")
    
    print("Breadth-first traversal:")
    for value in tree.create_breadth_first_iterator():
        print(f"  {value}")
    
    # Matrix iteration
    print("\n3. Matrix Iterator:")
    
    matrix_data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    matrix = Matrix(matrix_data)
    
    print("Matrix:")
    for row in matrix_data:
        print(f"  {row}")
    
    print("Row-wise iteration:")
    row_values = []
    for value in matrix.create_iterator():
        row_values.append(value)
    print(f"  {row_values}")
    
    print("Column-wise iteration:")
    col_values = []
    for value in matrix.create_column_iterator():
        col_values.append(value)
    print(f"  {col_values}")
    
    # Range iterator
    print("\n4. Range Iterator:")
    
    ranges = [
        Range(1, 6),
        Range(0, 10, 2),
        Range(10, 0, -2)
    ]
    
    for i, range_obj in enumerate(ranges):
        values = list(range_obj.create_iterator())
        print(f"Range {i+1}: {values}")
    
    # Filtered iterator
    print("\n5. Filtered Iterator:")
    
    numbers = ConcreteAggregate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # Filter even numbers
    even_filter = lambda x: x % 2 == 0
    filtered_iterator = FilteredIterator(numbers.create_iterator(), even_filter)
    
    print("Original numbers:", [x for x in numbers])
    print("Even numbers:", [x for x in filtered_iterator])
    
    # Filter numbers greater than 5
    greater_than_5 = lambda x: x > 5
    filtered_iterator2 = FilteredIterator(numbers.create_iterator(), greater_than_5)
    
    print("Numbers > 5:", [x for x in filtered_iterator2])
    
    # Multiple iterators on same collection
    print("\n6. Multiple Iterators:")
    
    words = ConcreteAggregate(["apple", "banana", "cherry", "date"])
    
    print("Two independent iterators:")
    iter1 = words.create_iterator()
    iter2 = words.create_iterator()
    
    print(f"Iterator 1 - first item: {next(iter1)}")
    print(f"Iterator 2 - first item: {next(iter2)}")
    print(f"Iterator 1 - second item: {next(iter1)}")
    print(f"Iterator 2 - second item: {next(iter2)}")
    
    # Nested iteration
    print("\n7. Nested Iteration:")
    
    nested_data = [
        ConcreteAggregate([1, 2, 3]),
        ConcreteAggregate([4, 5, 6]),
        ConcreteAggregate([7, 8, 9])
    ]
    
    print("Nested iteration:")
    for i, inner_collection in enumerate(nested_data):
        print(f"  Collection {i+1}:")
        for item in inner_collection:
            print(f"    {item}")
    
    # Iterator with state
    print("\n8. Iterator State Demonstration:")
    
    large_collection = ConcreteAggregate(list(range(1, 11)))
    iterator = large_collection.create_iterator()
    
    print("Processing first 3 items:")
    for _ in range(3):
        try:
            item = next(iterator)
            print(f"  Processing: {item}")
        except StopIteration:
            print("  No more items")
            break
    
    print("Processing remaining items:")
    for item in iterator:  # Continue from where we left off
        print(f"  Processing: {item}")


if __name__ == "__main__":
    main()