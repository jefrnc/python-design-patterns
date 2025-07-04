"""
Command Design Pattern - Gang of Four Implementation

Intent: Encapsulate a request as an object, thereby letting you parameterize clients
with different requests, queue or log requests, and support undoable operations.

Structure:
- Command: declares an interface for executing an operation
- ConcreteCommand: defines a binding between a Receiver object and an action
- Receiver: knows how to perform the operations associated with carrying out a request
- Invoker: asks the command to carry out the request
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Command(ABC):
    """
    The Command interface declares a method for executing a command.
    """
    
    @abstractmethod
    def execute(self) -> str:
        pass
    
    def undo(self) -> str:
        """
        Optional undo method. Not all commands need to support undo.
        """
        return "Undo not supported for this command"


class SimpleCommand(Command):
    """
    Some commands can implement simple operations on their own.
    """
    
    def __init__(self, payload: str):
        self._payload = payload
    
    def execute(self) -> str:
        return f"SimpleCommand: See, I can do simple things like printing ({self._payload})"


class ComplexCommand(Command):
    """
    However, some commands can delegate more complex operations to other objects,
    called "receivers."
    """
    
    def __init__(self, receiver: 'Receiver', action_a: str, action_b: str):
        """
        Complex commands can accept one or several receiver objects along with
        any context data via the constructor.
        """
        self._receiver = receiver
        self._action_a = action_a
        self._action_b = action_b
    
    def execute(self) -> str:
        """
        Commands can delegate to any methods of a receiver.
        """
        result = []
        result.append("ComplexCommand: Complex stuff should be done by a receiver object")
        result.append(self._receiver.do_something(self._action_a))
        result.append(self._receiver.do_something_else(self._action_b))
        return "\n".join(result)


class Receiver:
    """
    The Receiver classes contain some important business logic. They know how to
    perform all kinds of operations, associated with carrying out a request. In
    fact, any class may serve as a Receiver.
    """
    
    def do_something(self, action: str) -> str:
        return f"Receiver: Working on ({action})"
    
    def do_something_else(self, action: str) -> str:
        return f"Receiver: Also working on ({action})"


class Invoker:
    """
    The Invoker is associated with one or several commands. It sends a request
    to the command.
    """
    
    def __init__(self):
        self._on_start: Optional[Command] = None
        self._on_finish: Optional[Command] = None
        self._commands: List[Command] = []
        self._history: List[Command] = []
    
    def set_on_start(self, command: Command) -> None:
        """
        Initialize a command.
        """
        self._on_start = command
    
    def set_on_finish(self, command: Command) -> None:
        """
        Finalize a command.
        """
        self._on_finish = command
    
    def add_command(self, command: Command) -> None:
        """
        Add a command to the queue.
        """
        self._commands.append(command)
    
    def execute_commands(self) -> List[str]:
        """
        The Invoker does not depend on concrete command or receiver classes. The
        Invoker passes a request to a receiver indirectly, by executing a command.
        """
        results = []
        
        if self._on_start:
            result = self._on_start.execute()
            results.append(f"Start: {result}")
            self._history.append(self._on_start)
        
        for command in self._commands:
            result = command.execute()
            results.append(f"Command: {result}")
            self._history.append(command)
        
        if self._on_finish:
            result = self._on_finish.execute()
            results.append(f"Finish: {result}")
            self._history.append(self._on_finish)
        
        # Clear commands after execution
        self._commands.clear()
        
        return results
    
    def undo_last(self) -> str:
        """
        Undo the last executed command.
        """
        if self._history:
            last_command = self._history.pop()
            return last_command.undo()
        return "No commands to undo"
    
    def get_history_size(self) -> int:
        """
        Get the number of commands in history.
        """
        return len(self._history)


# Extended example with undoable commands
class UndoableCommand(Command):
    """
    Base class for commands that support undo operations.
    """
    
    def __init__(self):
        self._executed = False
    
    @abstractmethod
    def execute(self) -> str:
        pass
    
    @abstractmethod
    def undo(self) -> str:
        pass


class Calculator:
    """
    Receiver class that performs calculations.
    """
    
    def __init__(self):
        self._value = 0
        self._history: List[tuple] = []
    
    def add(self, amount: int) -> str:
        old_value = self._value
        self._value += amount
        self._history.append(('add', amount, old_value))
        return f"Added {amount}: {old_value} + {amount} = {self._value}"
    
    def subtract(self, amount: int) -> str:
        old_value = self._value
        self._value -= amount
        self._history.append(('subtract', amount, old_value))
        return f"Subtracted {amount}: {old_value} - {amount} = {self._value}"
    
    def multiply(self, amount: int) -> str:
        old_value = self._value
        self._value *= amount
        self._history.append(('multiply', amount, old_value))
        return f"Multiplied by {amount}: {old_value} * {amount} = {self._value}"
    
    def get_value(self) -> int:
        return self._value
    
    def set_value(self, value: int) -> None:
        self._value = value


class AddCommand(UndoableCommand):
    """
    Command to add a value to the calculator.
    """
    
    def __init__(self, calculator: Calculator, amount: int):
        super().__init__()
        self._calculator = calculator
        self._amount = amount
        self._previous_value = 0
    
    def execute(self) -> str:
        self._previous_value = self._calculator.get_value()
        result = self._calculator.add(self._amount)
        self._executed = True
        return result
    
    def undo(self) -> str:
        if self._executed:
            self._calculator.set_value(self._previous_value)
            self._executed = False
            return f"Undid add {self._amount}: restored to {self._previous_value}"
        return "Cannot undo: command was not executed"


class SubtractCommand(UndoableCommand):
    """
    Command to subtract a value from the calculator.
    """
    
    def __init__(self, calculator: Calculator, amount: int):
        super().__init__()
        self._calculator = calculator
        self._amount = amount
        self._previous_value = 0
    
    def execute(self) -> str:
        self._previous_value = self._calculator.get_value()
        result = self._calculator.subtract(self._amount)
        self._executed = True
        return result
    
    def undo(self) -> str:
        if self._executed:
            self._calculator.set_value(self._previous_value)
            self._executed = False
            return f"Undid subtract {self._amount}: restored to {self._previous_value}"
        return "Cannot undo: command was not executed"


class MacroCommand(Command):
    """
    A command that executes multiple commands.
    """
    
    def __init__(self, commands: List[Command]):
        self._commands = commands
    
    def execute(self) -> str:
        results = []
        results.append("MacroCommand: Executing multiple commands")
        
        for i, command in enumerate(self._commands):
            result = command.execute()
            results.append(f"  Step {i+1}: {result}")
        
        return "\n".join(results)
    
    def undo(self) -> str:
        results = []
        results.append("MacroCommand: Undoing multiple commands")
        
        # Undo in reverse order
        for i, command in enumerate(reversed(self._commands)):
            result = command.undo()
            results.append(f"  Undo step {i+1}: {result}")
        
        return "\n".join(results)


def main():
    """
    The client code can parameterize an invoker with any commands.
    """
    print("=== Command Pattern Demo ===")
    
    # Basic command pattern
    print("\n1. Basic Command Pattern:")
    
    # The client code can parameterize an invoker with any commands.
    invoker = Invoker()
    invoker.set_on_start(SimpleCommand("Say Hi!"))
    
    receiver = Receiver()
    invoker.add_command(ComplexCommand(receiver, "Send email", "Save report"))
    invoker.add_command(SimpleCommand("Say Bye!"))
    invoker.set_on_finish(SimpleCommand("Process completed"))
    
    results = invoker.execute_commands()
    for result in results:
        print(result)
    
    print(f"\nCommands in history: {invoker.get_history_size()}")
    
    # Calculator with undoable commands
    print("\n2. Calculator with Undoable Commands:")
    
    calculator = Calculator()
    print(f"Initial value: {calculator.get_value()}")
    
    # Create and execute commands
    add5 = AddCommand(calculator, 5)
    add10 = AddCommand(calculator, 10)
    subtract3 = SubtractCommand(calculator, 3)
    
    print(f"\nExecuting commands:")
    print(add5.execute())
    print(add10.execute())
    print(subtract3.execute())
    
    print(f"\nFinal value: {calculator.get_value()}")
    
    # Undo operations
    print(f"\nUndoing operations:")
    print(subtract3.undo())
    print(f"After undo subtract: {calculator.get_value()}")
    
    print(add10.undo())
    print(f"After undo add 10: {calculator.get_value()}")
    
    print(add5.undo())
    print(f"After undo add 5: {calculator.get_value()}")
    
    # Macro command
    print("\n3. Macro Command:")
    calc2 = Calculator()
    
    macro_commands = [
        AddCommand(calc2, 100),
        SubtractCommand(calc2, 25),
        AddCommand(calc2, 50)
    ]
    
    macro = MacroCommand(macro_commands)
    print(f"Initial calc2 value: {calc2.get_value()}")
    print(macro.execute())
    print(f"Final calc2 value: {calc2.get_value()}")
    
    print("\nUndoing macro:")
    print(macro.undo())
    print(f"After macro undo: {calc2.get_value()}")
    
    # Command queue
    print("\n4. Command Queue:")
    queue_invoker = Invoker()
    calc3 = Calculator()
    
    # Add multiple commands to queue
    queue_invoker.add_command(AddCommand(calc3, 1))
    queue_invoker.add_command(AddCommand(calc3, 2))
    queue_invoker.add_command(AddCommand(calc3, 3))
    queue_invoker.add_command(SubtractCommand(calc3, 1))
    
    print(f"Initial calc3 value: {calc3.get_value()}")
    
    # Execute all queued commands
    results = queue_invoker.execute_commands()
    for result in results:
        print(result)
    
    print(f"Final calc3 value: {calc3.get_value()}")
    
    # Test undo history
    print(f"\nUndoing last command:")
    print(queue_invoker.undo_last())
    print(f"After undo: {calc3.get_value()}")


if __name__ == "__main__":
    main()