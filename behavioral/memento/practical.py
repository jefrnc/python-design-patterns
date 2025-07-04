"""
Memento Design Pattern - Real World Implementation

Real-world example: Document Editor with Undo/Redo System
A comprehensive document editor that supports unlimited undo/redo operations,
auto-save functionality, version history, and collaborative editing with snapshots.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import copy
import hashlib
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be performed on a document."""
    INSERT_TEXT = "insert_text"
    DELETE_TEXT = "delete_text"
    REPLACE_TEXT = "replace_text"
    FORMAT_TEXT = "format_text"
    INSERT_IMAGE = "insert_image"
    DELETE_IMAGE = "delete_image"
    SET_TITLE = "set_title"
    ADD_COMMENT = "add_comment"
    DELETE_COMMENT = "delete_comment"
    BULK_OPERATION = "bulk_operation"


class TextFormat:
    """Text formatting attributes."""
    
    def __init__(self, bold: bool = False, italic: bool = False, 
                 underline: bool = False, font_size: int = 12, 
                 color: str = "black", font_family: str = "Arial"):
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.font_size = font_size
        self.color = color
        self.font_family = font_family
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "font_size": self.font_size,
            "color": self.color,
            "font_family": self.font_family
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextFormat':
        return cls(**data)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TextFormat):
            return False
        return self.to_dict() == other.to_dict()


class DocumentElement:
    """Base class for document elements."""
    
    def __init__(self, element_type: str, content: Any, 
                 format_attrs: Optional[TextFormat] = None):
        self.element_type = element_type
        self.content = content
        self.format_attrs = format_attrs or TextFormat()
        self.created_at = datetime.now()
        self.element_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for the element."""
        timestamp = str(self.created_at.timestamp())
        content_str = str(self.content)
        return hashlib.md5((timestamp + content_str).encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "content": self.content,
            "format_attrs": self.format_attrs.to_dict(),
            "created_at": self.created_at.isoformat(),
            "element_id": self.element_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentElement':
        element = cls(
            data["element_type"],
            data["content"],
            TextFormat.from_dict(data["format_attrs"])
        )
        element.created_at = datetime.fromisoformat(data["created_at"])
        element.element_id = data["element_id"]
        return element


class Comment:
    """Document comment/annotation."""
    
    def __init__(self, author: str, text: str, position: int):
        self.author = author
        self.text = text
        self.position = position  # Character position in document
        self.created_at = datetime.now()
        self.comment_id = self._generate_id()
    
    def _generate_id(self) -> str:
        timestamp = str(self.created_at.timestamp())
        return hashlib.md5((timestamp + self.author + self.text).encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "author": self.author,
            "text": self.text,
            "position": self.position,
            "created_at": self.created_at.isoformat(),
            "comment_id": self.comment_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        comment = cls(data["author"], data["text"], data["position"])
        comment.created_at = datetime.fromisoformat(data["created_at"])
        comment.comment_id = data["comment_id"]
        return comment


class DocumentMemento:
    """
    Memento storing the complete state of a document.
    """
    
    def __init__(self, title: str, elements: List[DocumentElement], 
                 comments: List[Comment], metadata: Dict[str, Any],
                 action_type: ActionType, description: str, author: str):
        self._title = title
        self._elements = copy.deepcopy(elements)
        self._comments = copy.deepcopy(comments)
        self._metadata = copy.deepcopy(metadata)
        self._action_type = action_type
        self._description = description
        self._author = author
        self._timestamp = datetime.now()
        self._checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for data integrity verification."""
        content = json.dumps({
            "title": self._title,
            "elements": [e.to_dict() for e in self._elements],
            "comments": [c.to_dict() for c in self._comments],
            "metadata": self._metadata
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_title(self) -> str:
        return self._title
    
    def get_elements(self) -> List[DocumentElement]:
        return copy.deepcopy(self._elements)
    
    def get_comments(self) -> List[Comment]:
        return copy.deepcopy(self._comments)
    
    def get_metadata(self) -> Dict[str, Any]:
        return copy.deepcopy(self._metadata)
    
    def get_action_info(self) -> Dict[str, Any]:
        return {
            "action_type": self._action_type.value,
            "description": self._description,
            "author": self._author,
            "timestamp": self._timestamp.isoformat(),
            "checksum": self._checksum
        }
    
    def verify_integrity(self) -> bool:
        """Verify memento data integrity."""
        return self._checksum == self._calculate_checksum()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the memento without full data."""
        return {
            "action_type": self._action_type.value,
            "description": self._description,
            "author": self._author,
            "timestamp": self._timestamp.isoformat(),
            "title": self._title,
            "element_count": len(self._elements),
            "comment_count": len(self._comments),
            "character_count": sum(len(str(e.content)) for e in self._elements if e.element_type == "text"),
            "checksum": self._checksum[:8]  # Shortened for display
        }


class VersionSnapshot:
    """Extended memento for version control with additional metadata."""
    
    def __init__(self, memento: DocumentMemento, version_number: str,
                 tag: str = "", branch: str = "main"):
        self.memento = memento
        self.version_number = version_number
        self.tag = tag
        self.branch = branch
        self.created_at = datetime.now()
    
    def get_version_info(self) -> Dict[str, Any]:
        return {
            "version_number": self.version_number,
            "tag": self.tag,
            "branch": self.branch,
            "created_at": self.created_at.isoformat(),
            "action_info": self.memento.get_action_info(),
            "summary": self.memento.get_summary()
        }


class Document:
    """
    Document originator that creates and restores from mementos.
    """
    
    def __init__(self, title: str = "Untitled Document", author: str = "Anonymous"):
        self.title = title
        self.elements: List[DocumentElement] = []
        self.comments: List[Comment] = []
        self.metadata = {
            "author": author,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "word_count": 0,
            "character_count": 0,
            "version": "1.0"
        }
        self._current_author = author
    
    def set_current_author(self, author: str) -> None:
        """Set the current author for operations."""
        self._current_author = author
    
    def create_memento(self, action_type: ActionType, description: str) -> DocumentMemento:
        """Create a memento of the current document state."""
        self._update_metadata()
        return DocumentMemento(
            self.title,
            self.elements,
            self.comments,
            self.metadata,
            action_type,
            description,
            self._current_author
        )
    
    def restore_from_memento(self, memento: DocumentMemento) -> None:
        """Restore document state from a memento."""
        if not memento.verify_integrity():
            raise ValueError("Memento data integrity check failed")
        
        self.title = memento.get_title()
        self.elements = memento.get_elements()
        self.comments = memento.get_comments()
        self.metadata = memento.get_metadata()
        self._update_metadata()
    
    def _update_metadata(self) -> None:
        """Update document metadata."""
        text_content = ""
        for element in self.elements:
            if element.element_type == "text":
                text_content += str(element.content) + " "
        
        words = text_content.split()
        self.metadata.update({
            "last_modified": datetime.now().isoformat(),
            "word_count": len(words),
            "character_count": len(text_content),
            "element_count": len(self.elements),
            "comment_count": len(self.comments)
        })
    
    # Document editing operations
    
    def set_title(self, new_title: str) -> None:
        """Set document title."""
        self.title = new_title
    
    def insert_text(self, text: str, position: int = -1, 
                   text_format: Optional[TextFormat] = None) -> None:
        """Insert text at specified position."""
        element = DocumentElement("text", text, text_format)
        if position == -1:
            self.elements.append(element)
        else:
            self.elements.insert(position, element)
    
    def delete_element(self, element_id: str) -> bool:
        """Delete element by ID."""
        for i, element in enumerate(self.elements):
            if element.element_id == element_id:
                del self.elements[i]
                return True
        return False
    
    def replace_text(self, element_id: str, new_text: str) -> bool:
        """Replace text in specific element."""
        for element in self.elements:
            if element.element_id == element_id and element.element_type == "text":
                element.content = new_text
                return True
        return False
    
    def format_element(self, element_id: str, text_format: TextFormat) -> bool:
        """Apply formatting to element."""
        for element in self.elements:
            if element.element_id == element_id:
                element.format_attrs = text_format
                return True
        return False
    
    def insert_image(self, image_path: str, alt_text: str = "", 
                    position: int = -1) -> None:
        """Insert image element."""
        image_data = {"path": image_path, "alt_text": alt_text}
        element = DocumentElement("image", image_data)
        if position == -1:
            self.elements.append(element)
        else:
            self.elements.insert(position, element)
    
    def add_comment(self, author: str, text: str, position: int) -> str:
        """Add comment to document."""
        comment = Comment(author, text, position)
        self.comments.append(comment)
        return comment.comment_id
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete comment by ID."""
        for i, comment in enumerate(self.comments):
            if comment.comment_id == comment_id:
                del self.comments[i]
                return True
        return False
    
    def get_text_content(self) -> str:
        """Get all text content as a single string."""
        text_parts = []
        for element in self.elements:
            if element.element_type == "text":
                text_parts.append(str(element.content))
        return " ".join(text_parts)
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get document summary."""
        return {
            "title": self.title,
            "metadata": self.metadata,
            "element_count": len(self.elements),
            "comment_count": len(self.comments),
            "text_preview": self.get_text_content()[:100] + "..." if len(self.get_text_content()) > 100 else self.get_text_content()
        }


class UndoRedoManager:
    """
    Caretaker managing document mementos for undo/redo operations.
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.undo_stack: List[DocumentMemento] = []
        self.redo_stack: List[DocumentMemento] = []
    
    def save_state(self, memento: DocumentMemento) -> None:
        """Save a document state for potential undo."""
        self.undo_stack.append(memento)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
        # Maintain maximum history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        print(f"💾 Saved state: {memento.get_action_info()['description']}")
    
    def undo(self) -> Optional[DocumentMemento]:
        """Get the previous state for undo operation."""
        if not self.undo_stack:
            return None
        
        # Move current state to redo stack
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        
        # Return previous state if available
        if self.undo_stack:
            return self.undo_stack[-1]
        return None
    
    def redo(self) -> Optional[DocumentMemento]:
        """Get the next state for redo operation."""
        if not self.redo_stack:
            return None
        
        # Move state back to undo stack
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        
        return next_state
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 1  # Need at least 2 states to undo
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
    
    def get_history_summary(self) -> List[Dict[str, Any]]:
        """Get summary of undo history."""
        return [memento.get_summary() for memento in self.undo_stack]
    
    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get information about memory usage."""
        return {
            "undo_stack_size": len(self.undo_stack),
            "redo_stack_size": len(self.redo_stack),
            "max_history": self.max_history,
            "memory_efficiency": f"{(len(self.undo_stack) / self.max_history * 100):.1f}%"
        }


class VersionControlManager:
    """
    Advanced caretaker for version control with branching and tagging.
    """
    
    def __init__(self):
        self.versions: Dict[str, VersionSnapshot] = {}
        self.branches: Dict[str, List[str]] = {"main": []}
        self.current_branch = "main"
        self.version_counter = 0
    
    def create_version(self, memento: DocumentMemento, tag: str = "") -> str:
        """Create a new version snapshot."""
        self.version_counter += 1
        version_number = f"v{self.version_counter}.0"
        
        snapshot = VersionSnapshot(memento, version_number, tag, self.current_branch)
        self.versions[version_number] = snapshot
        
        # Add to current branch
        if self.current_branch not in self.branches:
            self.branches[self.current_branch] = []
        self.branches[self.current_branch].append(version_number)
        
        print(f"📋 Created version {version_number} on branch '{self.current_branch}'" + 
              (f" with tag '{tag}'" if tag else ""))
        
        return version_number
    
    def get_version(self, version_number: str) -> Optional[DocumentMemento]:
        """Get a specific version."""
        if version_number in self.versions:
            return self.versions[version_number].memento
        return None
    
    def create_branch(self, branch_name: str, from_version: str = None) -> bool:
        """Create a new branch."""
        if branch_name in self.branches:
            return False
        
        self.branches[branch_name] = []
        
        if from_version and from_version in self.versions:
            # Branch from specific version
            self.branches[branch_name].append(from_version)
        
        print(f"🌿 Created branch '{branch_name}'")
        return True
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a different branch."""
        if branch_name in self.branches:
            self.current_branch = branch_name
            print(f"🔄 Switched to branch '{branch_name}'")
            return True
        return False
    
    def merge_branch(self, source_branch: str, target_branch: str = None) -> bool:
        """Merge one branch into another."""
        if target_branch is None:
            target_branch = self.current_branch
        
        if source_branch not in self.branches or target_branch not in self.branches:
            return False
        
        # Simple merge: add all versions from source to target
        source_versions = self.branches[source_branch]
        self.branches[target_branch].extend(source_versions)
        
        print(f"🔀 Merged branch '{source_branch}' into '{target_branch}'")
        return True
    
    def get_version_history(self, branch: str = None) -> List[Dict[str, Any]]:
        """Get version history for a branch."""
        if branch is None:
            branch = self.current_branch
        
        if branch not in self.branches:
            return []
        
        version_numbers = self.branches[branch]
        return [self.versions[v].get_version_info() for v in version_numbers if v in self.versions]
    
    def find_versions_by_tag(self, tag: str) -> List[str]:
        """Find versions with specific tag."""
        matching_versions = []
        for version_number, snapshot in self.versions.items():
            if snapshot.tag == tag:
                matching_versions.append(version_number)
        return matching_versions
    
    def get_branch_info(self) -> Dict[str, Any]:
        """Get information about all branches."""
        branch_info = {}
        for branch_name, versions in self.branches.items():
            branch_info[branch_name] = {
                "version_count": len(versions),
                "latest_version": versions[-1] if versions else None,
                "is_current": branch_name == self.current_branch
            }
        return branch_info


class DocumentEditor:
    """
    Complete document editor with undo/redo and version control.
    """
    
    def __init__(self, author: str = "Default User"):
        self.document = Document("New Document", author)
        self.undo_manager = UndoRedoManager()
        self.version_manager = VersionControlManager()
        self.auto_save_enabled = True
        self.auto_save_interval = 5  # operations
        self.operation_count = 0
        
        # Save initial state
        initial_memento = self.document.create_memento(ActionType.SET_TITLE, "Document created")
        self.undo_manager.save_state(initial_memento)
    
    def _auto_save_check(self, action_type: ActionType, description: str) -> None:
        """Check if auto-save should be triggered."""
        memento = self.document.create_memento(action_type, description)
        self.undo_manager.save_state(memento)
        self.operation_count += 1
        
        if (self.auto_save_enabled and 
            self.operation_count % self.auto_save_interval == 0):
            self.create_auto_save_version()
    
    def create_auto_save_version(self) -> str:
        """Create an auto-save version."""
        memento = self.document.create_memento(ActionType.BULK_OPERATION, "Auto-save")
        return self.version_manager.create_version(memento, "auto-save")
    
    # Document operations with memento pattern
    
    def set_title(self, title: str) -> None:
        """Set document title."""
        self.document.set_title(title)
        self._auto_save_check(ActionType.SET_TITLE, f"Set title to '{title}'")
    
    def insert_text(self, text: str, position: int = -1, 
                   text_format: Optional[TextFormat] = None) -> None:
        """Insert text with undo support."""
        self.document.insert_text(text, position, text_format)
        self._auto_save_check(ActionType.INSERT_TEXT, f"Inserted text: '{text[:20]}...'")
    
    def delete_element(self, element_id: str) -> bool:
        """Delete element with undo support."""
        success = self.document.delete_element(element_id)
        if success:
            self._auto_save_check(ActionType.DELETE_TEXT, f"Deleted element {element_id}")
        return success
    
    def replace_text(self, element_id: str, new_text: str) -> bool:
        """Replace text with undo support."""
        success = self.document.replace_text(element_id, new_text)
        if success:
            self._auto_save_check(ActionType.REPLACE_TEXT, 
                                f"Replaced text in element {element_id}")
        return success
    
    def format_element(self, element_id: str, text_format: TextFormat) -> bool:
        """Format element with undo support."""
        success = self.document.format_element(element_id, text_format)
        if success:
            self._auto_save_check(ActionType.FORMAT_TEXT, 
                                f"Applied formatting to element {element_id}")
        return success
    
    def insert_image(self, image_path: str, alt_text: str = "", 
                    position: int = -1) -> None:
        """Insert image with undo support."""
        self.document.insert_image(image_path, alt_text, position)
        self._auto_save_check(ActionType.INSERT_IMAGE, f"Inserted image: {image_path}")
    
    def add_comment(self, author: str, text: str, position: int) -> str:
        """Add comment with undo support."""
        comment_id = self.document.add_comment(author, text, position)
        self._auto_save_check(ActionType.ADD_COMMENT, 
                            f"Added comment by {author}: '{text[:20]}...'")
        return comment_id
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete comment with undo support."""
        success = self.document.delete_comment(comment_id)
        if success:
            self._auto_save_check(ActionType.DELETE_COMMENT, 
                                f"Deleted comment {comment_id}")
        return success
    
    # Undo/Redo operations
    
    def undo(self) -> bool:
        """Undo the last operation."""
        if not self.undo_manager.can_undo():
            print("❌ Nothing to undo")
            return False
        
        previous_state = self.undo_manager.undo()
        if previous_state:
            self.document.restore_from_memento(previous_state)
            action_info = previous_state.get_action_info()
            print(f"↶ Undone: {action_info['description']}")
            return True
        return False
    
    def redo(self) -> bool:
        """Redo the last undone operation."""
        if not self.undo_manager.can_redo():
            print("❌ Nothing to redo")
            return False
        
        next_state = self.undo_manager.redo()
        if next_state:
            self.document.restore_from_memento(next_state)
            action_info = next_state.get_action_info()
            print(f"↷ Redone: {action_info['description']}")
            return True
        return False
    
    # Version control operations
    
    def create_version(self, tag: str = "") -> str:
        """Create a new version."""
        memento = self.document.create_memento(ActionType.BULK_OPERATION, 
                                             f"Manual version{' - ' + tag if tag else ''}")
        return self.version_manager.create_version(memento, tag)
    
    def restore_version(self, version_number: str) -> bool:
        """Restore to a specific version."""
        memento = self.version_manager.get_version(version_number)
        if memento:
            self.document.restore_from_memento(memento)
            print(f"🔄 Restored to version {version_number}")
            # Save this as a new state in undo history
            restore_memento = self.document.create_memento(ActionType.BULK_OPERATION, 
                                                         f"Restored to version {version_number}")
            self.undo_manager.save_state(restore_memento)
            return True
        return False
    
    def create_branch(self, branch_name: str, from_version: str = None) -> bool:
        """Create a new branch."""
        return self.version_manager.create_branch(branch_name, from_version)
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a different branch."""
        return self.version_manager.switch_branch(branch_name)
    
    def get_editor_status(self) -> Dict[str, Any]:
        """Get comprehensive editor status."""
        return {
            "document": self.document.get_document_summary(),
            "undo_manager": self.undo_manager.get_memory_usage(),
            "version_manager": self.version_manager.get_branch_info(),
            "auto_save": {
                "enabled": self.auto_save_enabled,
                "interval": self.auto_save_interval,
                "operations_since_save": self.operation_count % self.auto_save_interval
            }
        }


def main():
    """
    Demonstrate the Document Editor Memento System.
    """
    print("=== Document Editor Memento System Demo ===")
    
    # Create editor
    editor = DocumentEditor("Alice Johnson")
    
    print(f"\n📝 Created document editor for {editor.document.metadata['author']}")
    
    # Test 1: Basic document editing
    print("\n✏️  Test 1: Basic Document Editing")
    
    editor.set_title("My Research Paper")
    editor.insert_text("Introduction", 0, TextFormat(bold=True, font_size=16))
    editor.insert_text("This is the introduction to my research paper on design patterns.")
    editor.insert_text("The Memento pattern is particularly useful for implementing undo/redo functionality.")
    
    print("Document content preview:")
    print(f"  Title: {editor.document.title}")
    print(f"  Text: {editor.document.get_text_content()}")
    
    # Test 2: Undo operations
    print("\n↶ Test 2: Undo Operations")
    
    editor.insert_text("This sentence will be undone.")
    print(f"Added text. Word count: {editor.document.metadata['word_count']}")
    
    editor.undo()
    print(f"After undo. Word count: {editor.document.metadata['word_count']}")
    
    editor.undo()
    print(f"After second undo. Word count: {editor.document.metadata['word_count']}")
    
    # Test 3: Redo operations
    print("\n↷ Test 3: Redo Operations")
    
    editor.redo()
    print(f"After redo. Word count: {editor.document.metadata['word_count']}")
    
    # Test 4: Text formatting
    print("\n🎨 Test 4: Text Formatting")
    
    # Get first element ID for formatting
    if editor.document.elements:
        first_element_id = editor.document.elements[0].element_id
        bold_italic_format = TextFormat(bold=True, italic=True, color="blue", font_size=18)
        editor.format_element(first_element_id, bold_italic_format)
        print(f"Applied formatting to element {first_element_id}")
    
    # Test 5: Comments
    print("\n💬 Test 5: Comments")
    
    comment1_id = editor.add_comment("Bob Smith", "Great introduction!", 50)
    comment2_id = editor.add_comment("Carol Davis", "Consider adding more details here.", 120)
    
    print(f"Added comments:")
    for comment in editor.document.comments:
        print(f"  {comment.author}: {comment.text} (pos: {comment.position})")
    
    # Test 6: Images
    print("\n🖼️  Test 6: Image Insertion")
    
    editor.insert_image("/path/to/diagram1.png", "Research methodology diagram")
    editor.insert_image("/path/to/chart1.png", "Results chart", 2)
    
    print(f"Document now has {len(editor.document.elements)} elements")
    for i, element in enumerate(editor.document.elements):
        if element.element_type == "image":
            print(f"  Image {i}: {element.content['path']} - {element.content['alt_text']}")
    
    # Test 7: Version control
    print("\n📋 Test 7: Version Control")
    
    # Create first version
    v1 = editor.create_version("draft-1")
    
    # Make more changes
    editor.insert_text("Methodology", -1, TextFormat(bold=True, font_size=16))
    editor.insert_text("Our research methodology involves analyzing existing design patterns.")
    
    # Create second version
    v2 = editor.create_version("draft-2")
    
    # Make more changes
    editor.insert_text("Results and Discussion", -1, TextFormat(bold=True, font_size=16))
    editor.insert_text("The results show that the Memento pattern significantly improves user experience.")
    
    # Create final version
    v3 = editor.create_version("final-draft")
    
    print(f"Created versions: {v1}, {v2}, {v3}")
    
    # Test 8: Version restoration
    print("\n🔄 Test 8: Version Restoration")
    
    print("Current document summary:")
    current_summary = editor.document.get_document_summary()
    print(f"  Word count: {current_summary['metadata']['word_count']}")
    print(f"  Elements: {current_summary['element_count']}")
    
    # Restore to earlier version
    editor.restore_version(v1)
    
    print("After restoring to v1:")
    restored_summary = editor.document.get_document_summary()
    print(f"  Word count: {restored_summary['metadata']['word_count']}")
    print(f"  Elements: {restored_summary['element_count']}")
    
    # Test 9: Branching
    print("\n🌿 Test 9: Branching")
    
    # Create a branch
    editor.create_branch("experimental", v2)
    editor.switch_branch("experimental")
    
    # Make changes on experimental branch
    editor.insert_text("Experimental section", -1, TextFormat(bold=True, color="red"))
    editor.insert_text("This is experimental content that might not make it to the final version.")
    
    # Create version on experimental branch
    exp_v1 = editor.create_version("experimental-v1")
    
    # Switch back to main
    editor.switch_branch("main")
    editor.restore_version(v3)  # Go back to final draft
    
    print("Branch information:")
    branch_info = editor.version_manager.get_branch_info()
    for branch, info in branch_info.items():
        status = " (current)" if info["is_current"] else ""
        print(f"  {branch}: {info['version_count']} versions{status}")
    
    # Test 10: History and undo management
    print("\n📚 Test 10: History Management")
    
    print("Undo history summary:")
    history = editor.undo_manager.get_history_summary()
    for i, entry in enumerate(history[-5:]):  # Show last 5 entries
        print(f"  {i+1}. {entry['action_type']}: {entry['description']} "
              f"(by {entry['author']} at {entry['timestamp'][-8:-3]})")
    
    # Test memory usage
    memory_info = editor.undo_manager.get_memory_usage()
    print(f"\nMemory usage:")
    print(f"  Undo stack: {memory_info['undo_stack_size']}/{memory_info['max_history']}")
    print(f"  Redo stack: {memory_info['redo_stack_size']}")
    print(f"  Efficiency: {memory_info['memory_efficiency']}")
    
    # Test 11: Bulk operations and auto-save
    print("\n💾 Test 11: Auto-save and Bulk Operations")
    
    print(f"Auto-save enabled: {editor.auto_save_enabled}")
    print(f"Auto-save interval: {editor.auto_save_interval} operations")
    
    # Perform multiple operations to trigger auto-save
    for i in range(3):
        editor.insert_text(f"Auto-save test paragraph {i+1}.")
    
    # Check version history
    version_history = editor.version_manager.get_version_history()
    auto_save_versions = [v for v in version_history if v.get('tag') == 'auto-save']
    print(f"Auto-save versions created: {len(auto_save_versions)}")
    
    # Test 12: Comment management
    print("\n💬 Test 12: Comment Management")
    
    # Delete a comment
    if editor.document.comments:
        comment_to_delete = editor.document.comments[0].comment_id
        editor.delete_comment(comment_to_delete)
        print(f"Deleted comment {comment_to_delete}")
    
    print(f"Remaining comments: {len(editor.document.comments)}")
    
    # Test 13: Complex undo/redo scenario
    print("\n🔄 Test 13: Complex Undo/Redo Scenario")
    
    # Perform several operations
    editor.insert_text("Conclusion")
    editor.insert_text("In conclusion, the Memento pattern provides excellent undo/redo capabilities.")
    conclusion_comment = editor.add_comment("Reviewer", "Strong conclusion!", 200)
    
    print("Performed 3 operations. Testing undo sequence:")
    
    # Undo all three
    for i in range(3):
        if editor.undo_manager.can_undo():
            editor.undo()
            print(f"  Undo {i+1} successful")
        else:
            print(f"  Undo {i+1} failed - no more history")
    
    # Redo two of them
    for i in range(2):
        if editor.undo_manager.can_redo():
            editor.redo()
            print(f"  Redo {i+1} successful")
        else:
            print(f"  Redo {i+1} failed - no more redo history")
    
    # Final status
    print("\n📊 Final Editor Status:")
    final_status = editor.get_editor_status()
    
    print(f"Document: {final_status['document']['title']}")
    print(f"  Words: {final_status['document']['metadata']['word_count']}")
    print(f"  Characters: {final_status['document']['metadata']['character_count']}")
    print(f"  Elements: {final_status['document']['element_count']}")
    print(f"  Comments: {final_status['document']['comment_count']}")
    
    print(f"Undo Manager:")
    print(f"  History size: {final_status['undo_manager']['undo_stack_size']}")
    print(f"  Can undo: {editor.undo_manager.can_undo()}")
    print(f"  Can redo: {editor.undo_manager.can_redo()}")
    
    print(f"Version Control:")
    for branch, info in final_status['version_manager'].items():
        status = " (current)" if info["is_current"] else ""
        print(f"  {branch}: {info['version_count']} versions{status}")


if __name__ == "__main__":
    main()