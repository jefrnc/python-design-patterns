"""
Decorator Design Pattern - Real World Implementation

Real-world example: Library System
A library system where books and videos can be made borrowable by decorating
them with borrowing functionality.
"""

from abc import ABC, abstractmethod
from typing import List


class LibraryItem(ABC):
    """
    The Component interface defines operations that can be altered by decorators.
    """
    
    def __init__(self, num_copies: int = 1):
        self._num_copies = num_copies
    
    @property
    def num_copies(self) -> int:
        return self._num_copies
    
    @num_copies.setter
    def num_copies(self, value: int) -> None:
        self._num_copies = value
    
    @abstractmethod
    def display(self) -> str:
        pass


class Book(LibraryItem):
    """
    A concrete component representing a book in the library.
    """
    
    def __init__(self, author: str, title: str, num_copies: int = 1):
        super().__init__(num_copies)
        self.author = author
        self.title = title
    
    def display(self) -> str:
        return f"""
Book ------
 Author: {self.author}
 Title: {self.title}
 # Copies: {self.num_copies}"""


class Video(LibraryItem):
    """
    A concrete component representing a video in the library.
    """
    
    def __init__(self, director: str, title: str, num_copies: int = 1, play_time: int = 0):
        super().__init__(num_copies)
        self.director = director
        self.title = title
        self.play_time = play_time
    
    def display(self) -> str:
        return f"""
Video -----
 Director: {self.director}
 Title: {self.title}
 # Copies: {self.num_copies}
 Playtime: {self.play_time} mins"""


class LibraryItemDecorator(LibraryItem):
    """
    The base decorator class follows the same interface as the other components.
    """
    
    def __init__(self, library_item: LibraryItem):
        super().__init__(library_item.num_copies)
        self._library_item = library_item
    
    @property
    def num_copies(self) -> int:
        return self._library_item.num_copies
    
    @num_copies.setter
    def num_copies(self, value: int) -> None:
        self._library_item.num_copies = value
    
    def display(self) -> str:
        return self._library_item.display()


class Borrowable(LibraryItemDecorator):
    """
    A concrete decorator that adds borrowing functionality to library items.
    """
    
    def __init__(self, library_item: LibraryItem):
        super().__init__(library_item)
        self._borrowers: List[str] = []
    
    def borrow_item(self, borrower_name: str) -> bool:
        """
        Borrow an item if copies are available.
        Returns True if successful, False otherwise.
        """
        if self.num_copies > 0:
            self._borrowers.append(borrower_name)
            self.num_copies -= 1
            print(f"✓ {borrower_name} borrowed the item")
            return True
        else:
            print(f"✗ {borrower_name} cannot borrow - no copies available")
            return False
    
    def return_item(self, borrower_name: str) -> bool:
        """
        Return an item if the borrower had borrowed it.
        Returns True if successful, False otherwise.
        """
        if borrower_name in self._borrowers:
            self._borrowers.remove(borrower_name)
            self.num_copies += 1
            print(f"✓ {borrower_name} returned the item")
            return True
        else:
            print(f"✗ {borrower_name} cannot return - item not borrowed by them")
            return False
    
    def get_borrowers(self) -> List[str]:
        """Get a copy of the current borrowers list."""
        return self._borrowers.copy()
    
    def display(self) -> str:
        result = super().display()
        if self._borrowers:
            result += "\n Borrowers:"
            for borrower in self._borrowers:
                result += f"\n  - {borrower}"
        return result


class Reservable(LibraryItemDecorator):
    """
    A concrete decorator that adds reservation functionality to library items.
    """
    
    def __init__(self, library_item: LibraryItem):
        super().__init__(library_item)
        self._reservations: List[str] = []
    
    def reserve_item(self, reserver_name: str) -> bool:
        """
        Reserve an item for future borrowing.
        Returns True if successful, False if already reserved by this person.
        """
        if reserver_name not in self._reservations:
            self._reservations.append(reserver_name)
            print(f"✓ {reserver_name} reserved the item")
            return True
        else:
            print(f"✗ {reserver_name} already has a reservation")
            return False
    
    def cancel_reservation(self, reserver_name: str) -> bool:
        """
        Cancel a reservation.
        Returns True if successful, False if no reservation found.
        """
        if reserver_name in self._reservations:
            self._reservations.remove(reserver_name)
            print(f"✓ {reserver_name} cancelled reservation")
            return True
        else:
            print(f"✗ {reserver_name} has no reservation to cancel")
            return False
    
    def get_reservations(self) -> List[str]:
        """Get a copy of the current reservations list."""
        return self._reservations.copy()
    
    def display(self) -> str:
        result = super().display()
        if self._reservations:
            result += "\n Reservations:"
            for reservation in self._reservations:
                result += f"\n  - {reservation}"
        return result


def main():
    """
    Real-world client code demonstrating library system usage.
    """
    print("=== Library System Decorator Demo ===")
    
    # Create library items
    book = Book("Robert Martin", "Clean Code", 3)
    video = Video("Christopher Nolan", "Inception", 2, 148)
    
    print("Original items:")
    print(book.display())
    print(video.display())
    
    # Make video borrowable
    print("\n" + "="*50)
    print("Making video borrowable...")
    borrowable_video = Borrowable(video)
    
    # Borrow the video
    print("\nBorrowing attempts:")
    borrowable_video.borrow_item("Alice")
    borrowable_video.borrow_item("Bob")
    borrowable_video.borrow_item("Charlie")  # Should fail - no copies left
    
    print("\nVideo status after borrowing:")
    print(borrowable_video.display())
    
    # Return one video
    print("\nReturning video:")
    borrowable_video.return_item("Alice")
    borrowable_video.return_item("Dave")  # Should fail - didn't borrow
    
    print("\nVideo status after return:")
    print(borrowable_video.display())
    
    # Make book both borrowable and reservable
    print("\n" + "="*50)
    print("Making book borrowable and reservable...")
    borrowable_book = Borrowable(book)
    reservable_borrowable_book = Reservable(borrowable_book)
    
    # Reserve and borrow
    print("\nReservations and borrowing:")
    reservable_borrowable_book.reserve_item("Eve")
    reservable_borrowable_book.reserve_item("Frank")
    reservable_borrowable_book.borrow_item("Grace")
    reservable_borrowable_book.borrow_item("Henry")
    
    print("\nBook status with multiple decorators:")
    print(reservable_borrowable_book.display())


if __name__ == "__main__":
    main()