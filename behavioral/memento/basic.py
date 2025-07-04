"""
Memento Design Pattern - Gang of Four Implementation

Intent: Without violating encapsulation, capture and externalize an object's
internal state so that the object can be restored to this state later.

Structure:
- Memento: stores internal state of the Originator object
- Originator: creates a memento containing a snapshot of its current internal state
- Caretaker: is responsible for the memento's safekeeping and never examines its contents
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict
from datetime import datetime
import copy


class Memento(ABC):
    """
    The Memento interface provides a way to retrieve the memento's metadata,
    such as creation date or name. However, it doesn't expose the Originator's state.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_date(self) -> str:
        pass


class ConcreteMemento(Memento):
    """
    The Concrete Memento contains the infrastructure for storing the Originator's
    state.
    """
    
    def __init__(self, state: str):
        self._state = state
        self._date = str(datetime.now())[:19]
    
    def get_state(self) -> str:
        """
        The Originator uses this method when restoring its state.
        """
        return self._state
    
    def get_name(self) -> str:
        """
        The rest of the methods are used by the Caretaker to display metadata.
        """
        return f"{self._date} / ({self._state[0:9]}...)"
    
    def get_date(self) -> str:
        return self._date


class Originator:
    """
    The Originator holds some important state that may change over time. It also
    defines a method for saving the state inside a memento and another method
    for restoring the state from it.
    """
    
    def __init__(self, state: str):
        self._state = state
        print(f"Originator: My initial state is: {self._state}")
    
    def do_something(self) -> None:
        """
        The Originator's business logic may affect its internal state.
        Therefore, the client should backup the state before launching
        methods of the business logic via the save() method.
        """
        print("Originator: I'm doing something important.")
        self._state = self._generate_random_string(30)
        print(f"Originator: and my state has changed to: {self._state}")
    
    def _generate_random_string(self, length: int = 10) -> str:
        """
        Generate a random string for demonstration purposes.
        """
        import random
        import string
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    def save(self) -> Memento:
        """
        Saves the current state inside a memento.
        """
        return ConcreteMemento(self._state)
    
    def restore(self, memento: Memento) -> None:
        """
        Restores the Originator's state from a memento object.
        """
        if isinstance(memento, ConcreteMemento):
            self._state = memento.get_state()
            print(f"Originator: My state has changed to: {self._state}")
        else:
            print("Originator: Cannot restore from unknown memento type")
    
    def get_state(self) -> str:
        """
        Get the current state for display purposes.
        """
        return self._state


class Caretaker:
    """
    The Caretaker doesn't depend on the Concrete Memento class. Therefore, it
    doesn't have access to the originator's state, stored inside the memento. It
    works with all mementos via the base Memento interface.
    """
    
    def __init__(self, originator: Originator):
        self._mementos: List[Memento] = []
        self._originator = originator
    
    def backup(self) -> None:
        """
        Create a backup of the originator's current state.
        """
        print("\nCaretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save())
    
    def undo(self) -> None:
        """
        Restore the originator to its previous state.
        """
        if not len(self._mementos):
            print("Caretaker: No backups available")
            return
        
        memento = self._mementos.pop()
        print(f"Caretaker: Restoring state to: {memento.get_name()}")
        
        try:
            self._originator.restore(memento)
        except Exception:
            self.undo()
    
    def show_history(self) -> None:
        """
        Show the history of saved states.
        """
        print("Caretaker: Here's the list of mementos:")
        for i, memento in enumerate(self._mementos):
            print(f"  {i}: {memento.get_name()}")


# More practical example: Text Editor
class TextEditor:
    """
    Text editor that supports undo/redo functionality using memento pattern.
    """
    
    def __init__(self):
        self._content = ""
        self._cursor_position = 0
        self._selection_start = 0
        self._selection_end = 0
    
    def type_text(self, text: str) -> None:
        """
        Type text at the current cursor position.
        """
        self._content = (self._content[:self._cursor_position] + 
                        text + 
                        self._content[self._cursor_position:])
        self._cursor_position += len(text)
        print(f"Typed: '{text}'")
    
    def delete_text(self, count: int) -> None:
        """
        Delete text before cursor position.
        """
        start_pos = max(0, self._cursor_position - count)
        deleted_text = self._content[start_pos:self._cursor_position]
        self._content = (self._content[:start_pos] + 
                        self._content[self._cursor_position:])
        self._cursor_position = start_pos
        print(f"Deleted: '{deleted_text}'")
    
    def set_cursor_position(self, position: int) -> None:
        """
        Set cursor position.
        """
        self._cursor_position = max(0, min(position, len(self._content)))
    
    def select_text(self, start: int, end: int) -> None:
        """
        Select text range.
        """
        self._selection_start = max(0, min(start, len(self._content)))
        self._selection_end = max(0, min(end, len(self._content)))
    
    def get_content(self) -> str:
        """
        Get the current content.
        """
        return self._content
    
    def get_state_info(self) -> str:
        """
        Get current state information for display.
        """
        return f"Content: '{self._content}' | Cursor: {self._cursor_position}"
    
    def create_memento(self) -> 'TextEditorMemento':
        """
        Create a memento of the current state.
        """
        return TextEditorMemento(
            self._content,
            self._cursor_position,
            self._selection_start,
            self._selection_end
        )
    
    def restore_from_memento(self, memento: 'TextEditorMemento') -> None:
        """
        Restore state from memento.
        """
        self._content = memento.get_content()
        self._cursor_position = memento.get_cursor_position()
        self._selection_start = memento.get_selection_start()
        self._selection_end = memento.get_selection_end()


class TextEditorMemento:
    """
    Memento for text editor state.
    """
    
    def __init__(self, content: str, cursor_position: int, 
                 selection_start: int, selection_end: int):
        self._content = content
        self._cursor_position = cursor_position
        self._selection_start = selection_start
        self._selection_end = selection_end
        self._timestamp = datetime.now()
    
    def get_content(self) -> str:
        return self._content
    
    def get_cursor_position(self) -> int:
        return self._cursor_position
    
    def get_selection_start(self) -> int:
        return self._selection_start
    
    def get_selection_end(self) -> int:
        return self._selection_end
    
    def get_timestamp(self) -> datetime:
        return self._timestamp
    
    def get_name(self) -> str:
        content_preview = self._content[:20] + "..." if len(self._content) > 20 else self._content
        return f"{self._timestamp.strftime('%H:%M:%S')} - '{content_preview}'"


class TextEditorHistory:
    """
    History manager for text editor using memento pattern.
    """
    
    def __init__(self, editor: TextEditor):
        self._editor = editor
        self._history: List[TextEditorMemento] = []
        self._current_index = -1
        self._max_history_size = 50
    
    def save_state(self) -> None:
        """
        Save current editor state.
        """
        # Remove any future states if we're not at the end
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        # Add new state
        memento = self._editor.create_memento()
        self._history.append(memento)
        self._current_index += 1
        
        # Limit history size
        if len(self._history) > self._max_history_size:
            self._history.pop(0)
            self._current_index -= 1
        
        print(f"State saved: {memento.get_name()}")
    
    def undo(self) -> bool:
        """
        Undo to previous state.
        """
        if self._current_index > 0:
            self._current_index -= 1
            memento = self._history[self._current_index]
            self._editor.restore_from_memento(memento)
            print(f"Undo to: {memento.get_name()}")
            return True
        else:
            print("Cannot undo: No previous states")
            return False
    
    def redo(self) -> bool:
        """
        Redo to next state.
        """
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            memento = self._history[self._current_index]
            self._editor.restore_from_memento(memento)
            print(f"Redo to: {memento.get_name()}")
            return True
        else:
            print("Cannot redo: No future states")
            return False
    
    def show_history(self) -> None:
        """
        Show the edit history.
        """
        print("Edit History:")
        for i, memento in enumerate(self._history):
            marker = " -> " if i == self._current_index else "    "
            print(f"{marker}{i}: {memento.get_name()}")


# Game State example
class GameState:
    """
    Game state that can be saved and restored.
    """
    
    def __init__(self):
        self._level = 1
        self._score = 0
        self._lives = 3
        self._position = {"x": 0, "y": 0}
        self._inventory = []
    
    def play_level(self) -> None:
        """
        Simulate playing a level.
        """
        self._score += 100
        self._position["x"] += 10
        self._position["y"] += 5
        print(f"Level {self._level} completed! Score: {self._score}")
    
    def next_level(self) -> None:
        """
        Advance to next level.
        """
        self._level += 1
        self._position = {"x": 0, "y": 0}
        print(f"Advanced to level {self._level}")
    
    def lose_life(self) -> None:
        """
        Lose a life.
        """
        self._lives -= 1
        print(f"Lost a life! Lives remaining: {self._lives}")
    
    def add_item(self, item: str) -> None:
        """
        Add item to inventory.
        """
        self._inventory.append(item)
        print(f"Found item: {item}")
    
    def get_state_info(self) -> str:
        """
        Get current state information.
        """
        return (f"Level: {self._level}, Score: {self._score}, "
                f"Lives: {self._lives}, Position: {self._position}, "
                f"Inventory: {self._inventory}")
    
    def create_save_data(self) -> 'GameSaveData':
        """
        Create save data memento.
        """
        return GameSaveData(
            copy.deepcopy({
                "level": self._level,
                "score": self._score,
                "lives": self._lives,
                "position": self._position,
                "inventory": self._inventory
            })
        )
    
    def load_save_data(self, save_data: 'GameSaveData') -> None:
        """
        Load state from save data.
        """
        data = save_data.get_save_data()
        self._level = data["level"]
        self._score = data["score"]
        self._lives = data["lives"]
        self._position = data["position"]
        self._inventory = data["inventory"]


class GameSaveData:
    """
    Game save data memento.
    """
    
    def __init__(self, save_data: Dict[str, Any]):
        self._save_data = copy.deepcopy(save_data)
        self._save_time = datetime.now()
    
    def get_save_data(self) -> Dict[str, Any]:
        return copy.deepcopy(self._save_data)
    
    def get_save_time(self) -> datetime:
        return self._save_time
    
    def get_save_name(self) -> str:
        data = self._save_data
        return (f"Level {data['level']} - Score {data['score']} - "
                f"{self._save_time.strftime('%H:%M:%S')}")


class GameSaveManager:
    """
    Game save manager.
    """
    
    def __init__(self, game: GameState):
        self._game = game
        self._saves: List[GameSaveData] = []
        self._auto_saves: List[GameSaveData] = []
        self._max_saves = 10
        self._max_auto_saves = 5
    
    def save_game(self, save_name: str = None) -> None:
        """
        Create a manual save.
        """
        save_data = self._game.create_save_data()
        self._saves.append(save_data)
        
        # Limit number of saves
        if len(self._saves) > self._max_saves:
            self._saves.pop(0)
        
        name = save_name or save_data.get_save_name()
        print(f"Game saved: {name}")
    
    def auto_save(self) -> None:
        """
        Create an automatic save.
        """
        save_data = self._game.create_save_data()
        self._auto_saves.append(save_data)
        
        # Limit number of auto-saves
        if len(self._auto_saves) > self._max_auto_saves:
            self._auto_saves.pop(0)
        
        print(f"Auto-saved: {save_data.get_save_name()}")
    
    def load_game(self, save_index: int) -> bool:
        """
        Load a manual save.
        """
        if 0 <= save_index < len(self._saves):
            save_data = self._saves[save_index]
            self._game.load_save_data(save_data)
            print(f"Game loaded: {save_data.get_save_name()}")
            return True
        else:
            print("Invalid save index")
            return False
    
    def load_auto_save(self, save_index: int) -> bool:
        """
        Load an automatic save.
        """
        if 0 <= save_index < len(self._auto_saves):
            save_data = self._auto_saves[save_index]
            self._game.load_save_data(save_data)
            print(f"Auto-save loaded: {save_data.get_save_name()}")
            return True
        else:
            print("Invalid auto-save index")
            return False
    
    def list_saves(self) -> None:
        """
        List all available saves.
        """
        print("Manual Saves:")
        for i, save_data in enumerate(self._saves):
            print(f"  {i}: {save_data.get_save_name()}")
        
        print("Auto Saves:")
        for i, save_data in enumerate(self._auto_saves):
            print(f"  {i}: {save_data.get_save_name()}")


def main():
    """
    The client code demonstrates the Memento pattern.
    """
    print("=== Memento Pattern Demo ===")
    
    # Basic memento pattern
    print("\n1. Basic Memento Pattern:")
    
    originator = Originator("Super-duper-super-puper-super.")
    caretaker = Caretaker(originator)
    
    caretaker.backup()
    originator.do_something()
    
    caretaker.backup()
    originator.do_something()
    
    caretaker.backup()
    originator.do_something()
    
    print()
    caretaker.show_history()
    
    print("\nClient: Now, let's rollback!\n")
    caretaker.undo()
    
    print("\nClient: Once more!\n")
    caretaker.undo()
    
    # Text editor example
    print("\n2. Text Editor with Undo/Redo:")
    
    editor = TextEditor()
    history = TextEditorHistory(editor)
    
    # Initial state
    history.save_state()
    print(f"Initial: {editor.get_state_info()}")
    
    # Type some text
    editor.type_text("Hello")
    history.save_state()
    print(f"After typing 'Hello': {editor.get_state_info()}")
    
    editor.type_text(" World")
    history.save_state()
    print(f"After typing ' World': {editor.get_state_info()}")
    
    editor.type_text("!")
    history.save_state()
    print(f"After typing '!': {editor.get_state_info()}")
    
    # Undo operations
    print("\nUndo operations:")
    history.undo()
    print(f"After undo: {editor.get_state_info()}")
    
    history.undo()
    print(f"After undo: {editor.get_state_info()}")
    
    # Redo operations
    print("\nRedo operations:")
    history.redo()
    print(f"After redo: {editor.get_state_info()}")
    
    # New text after undo (should clear redo history)
    editor.type_text(" Python")
    history.save_state()
    print(f"After typing ' Python': {editor.get_state_info()}")
    
    # Try to redo (should fail)
    print("\nTrying to redo (should fail):")
    history.redo()
    
    print("\nEdit history:")
    history.show_history()
    
    # Game save example
    print("\n3. Game Save System:")
    
    game = GameState()
    save_manager = GameSaveManager(game)
    
    print(f"Initial state: {game.get_state_info()}")
    
    # Play the game
    game.play_level()
    game.add_item("sword")
    save_manager.auto_save()  # Auto-save after level completion
    
    game.next_level()
    game.play_level()
    game.add_item("shield")
    save_manager.save_game("Before boss fight")  # Manual save
    
    game.next_level()
    game.play_level()
    game.lose_life()  # Died fighting boss
    save_manager.auto_save()
    
    print(f"\nCurrent state: {game.get_state_info()}")
    
    # Show available saves
    print("\nAvailable saves:")
    save_manager.list_saves()
    
    # Load previous save
    print("\nLoading save before boss fight:")
    save_manager.load_game(0)
    print(f"Loaded state: {game.get_state_info()}")
    
    # Continue playing
    game.add_item("potion")
    game.next_level()
    save_manager.auto_save()
    
    print(f"Final state: {game.get_state_info()}")
    
    # Demonstrate multiple save slots
    print("\n4. Multiple Save Slots:")
    
    # Create multiple saves at different points
    game2 = GameState()
    save_manager2 = GameSaveManager(game2)
    
    for i in range(3):
        game2.play_level()
        game2.add_item(f"item_{i}")
        if i < 2:
            game2.next_level()
        save_manager2.save_game(f"Save slot {i+1}")
    
    print(f"Final game state: {game2.get_state_info()}")
    
    print("\nAll saves:")
    save_manager2.list_saves()
    
    # Load different saves
    print("\nLoading first save:")
    save_manager2.load_game(0)
    print(f"State after loading save 1: {game2.get_state_info()}")


if __name__ == "__main__":
    main()