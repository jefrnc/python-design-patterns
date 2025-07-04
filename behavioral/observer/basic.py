"""
Observer Design Pattern - Gang of Four Implementation

Intent: Define a one-to-many dependency between objects so that when one
object changes state, all its dependents are notified and updated automatically.

Structure:
- Subject: knows its observers and provides an interface for attaching and detaching observers
- Observer: defines an updating interface for objects that should be notified of changes
- ConcreteSubject: stores state of interest to ConcreteObserver objects
- ConcreteObserver: implements the Observer updating interface
"""

from abc import ABC, abstractmethod
from typing import List


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """
    
    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        """
        Attach an observer to the subject.
        """
        pass
    
    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        """
        Detach an observer from the subject.
        """
        pass
    
    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass


class ConcreteSubject(Subject):
    """
    The Subject owns some important state and notifies observers when the state
    changes.
    """
    
    def __init__(self) -> None:
        self._state: int = 0
        self._observers: List[Observer] = []
    
    def attach(self, observer: 'Observer') -> None:
        print(f"Subject: Attached observer {observer.__class__.__name__}")
        self._observers.append(observer)
    
    def detach(self, observer: 'Observer') -> None:
        print(f"Subject: Detached observer {observer.__class__.__name__}")
        self._observers.remove(observer)
    
    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """
        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)
    
    def some_business_logic(self) -> None:
        """
        Usually, the subscription logic is only a fraction of what a Subject can
        really do. Subjects commonly hold some important business logic, that
        triggers a notification method whenever something important is about to
        happen (or after it).
        """
        print("\nSubject: I'm doing something important.")
        self._state = 42
        
        print(f"Subject: My state has just changed to: {self._state}")
        self.notify()
    
    @property
    def state(self) -> int:
        return self._state


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """
    
    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass


class ConcreteObserverA(Observer):
    """
    Concrete Observers react to the updates issued by the Subject they had been
    attached to.
    """
    
    def update(self, subject: Subject) -> None:
        if isinstance(subject, ConcreteSubject) and subject.state < 3:
            print("ConcreteObserverA: Reacted to the event")


class ConcreteObserverB(Observer):
    """
    Concrete Observers react to the updates issued by the Subject they had been
    attached to.
    """
    
    def update(self, subject: Subject) -> None:
        if isinstance(subject, ConcreteSubject) and (subject.state == 0 or subject.state >= 2):
            print("ConcreteObserverB: Reacted to the event")


def main():
    """
    The client code.
    """
    print("=== Observer Pattern Demo ===")
    
    # Create subject
    subject = ConcreteSubject()
    
    # Create observers
    observer_a = ConcreteObserverA()
    observer_b = ConcreteObserverB()
    
    # Attach observers
    subject.attach(observer_a)
    subject.attach(observer_b)
    
    # Trigger business logic
    subject.some_business_logic()
    
    # Detach an observer
    print("\nDetaching observer A...")
    subject.detach(observer_a)
    
    # Trigger business logic again
    subject.some_business_logic()


if __name__ == "__main__":
    main()