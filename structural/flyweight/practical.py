"""
Flyweight Design Pattern - Real World Implementation

A real-world example demonstrating the Flyweight pattern through a 
text editor/document processing system that efficiently handles millions
of characters and formatting objects by sharing common intrinsic state
while maintaining unique extrinsic state for each instance.

This example shows how to:
- Share intrinsic state among many objects
- Separate intrinsic from extrinsic state
- Reduce memory usage for large numbers of similar objects
- Implement flyweight factories and management
- Handle character formatting, fonts, and styles efficiently
- Support document operations with minimal memory overhead
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import weakref
from collections import defaultdict
import sys


class FontWeight(Enum):
    """Font weight options."""
    THIN = 100
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    EXTRABOLD = 800
    BLACK = 900


class FontStyle(Enum):
    """Font style options."""
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class TextAlignment(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass(frozen=True)
class Color:
    """Immutable color representation."""
    red: int
    green: int
    blue: int
    alpha: int = 255
    
    def __post_init__(self):
        # Validate color values
        for value in [self.red, self.green, self.blue, self.alpha]:
            if not 0 <= value <= 255:
                raise ValueError("Color values must be between 0 and 255")
    
    def to_hex(self) -> str:
        """Convert to hex representation."""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
    
    def to_rgba(self) -> str:
        """Convert to RGBA representation."""
        return f"rgba({self.red}, {self.green}, {self.blue}, {self.alpha/255:.2f})"


# Flyweight Interface
class TextFlyweight(ABC):
    """
    Abstract flyweight interface for text elements.
    Contains intrinsic state that can be shared.
    """
    
    @abstractmethod
    def render(self, context: 'RenderContext') -> str:
        """Render the text element with given context (extrinsic state)."""
        pass
    
    @abstractmethod
    def get_memory_footprint(self) -> int:
        """Get the memory footprint of this flyweight."""
        pass
    
    @abstractmethod
    def get_intrinsic_state(self) -> Dict[str, Any]:
        """Get the intrinsic state of this flyweight."""
        pass


# Concrete Flyweight for Characters
class CharacterFlyweight(TextFlyweight):
    """
    Concrete flyweight for individual characters.
    Stores intrinsic state: character value, font family, size, weight, style, color.
    """
    
    def __init__(self, character: str, font_family: str, font_size: int, 
                 font_weight: FontWeight, font_style: FontStyle, color: Color):
        if len(character) != 1:
            raise ValueError("CharacterFlyweight can only represent single characters")
        
        # Intrinsic state - shared among all instances with same properties
        self._character = character
        self._font_family = font_family
        self._font_size = font_size
        self._font_weight = font_weight
        self._font_style = font_style
        self._color = color
        
        # Calculate hash for efficient comparison and storage
        self._hash = hash((character, font_family, font_size, font_weight, font_style, color))
    
    def render(self, context: 'RenderContext') -> str:
        """Render character with extrinsic context."""
        return (f"<span style=\""
                f"font-family: {self._font_family}; "
                f"font-size: {self._font_size}px; "
                f"font-weight: {self._font_weight.value}; "
                f"font-style: {self._font_style.value}; "
                f"color: {self._color.to_hex()}; "
                f"position: absolute; "
                f"left: {context.x}px; "
                f"top: {context.y}px;"
                f"\">{self._character}</span>")
    
    def get_memory_footprint(self) -> int:
        """Calculate approximate memory footprint."""
        # Base object overhead + string storage + enum references
        base_size = sys.getsizeof(self)
        char_size = sys.getsizeof(self._character)
        font_family_size = sys.getsizeof(self._font_family)
        return base_size + char_size + font_family_size
    
    def get_intrinsic_state(self) -> Dict[str, Any]:
        """Get intrinsic state information."""
        return {
            "character": self._character,
            "font_family": self._font_family,
            "font_size": self._font_size,
            "font_weight": self._font_weight.value,
            "font_style": self._font_style.value,
            "color": self._color.to_hex()
        }
    
    @property
    def character(self) -> str:
        return self._character
    
    @property
    def font_family(self) -> str:
        return self._font_family
    
    @property
    def font_size(self) -> int:
        return self._font_size
    
    def __hash__(self) -> int:
        return self._hash
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, CharacterFlyweight):
            return False
        return (self._character == other._character and
                self._font_family == other._font_family and
                self._font_size == other._font_size and
                self._font_weight == other._font_weight and
                self._font_style == other._font_style and
                self._color == other._color)


# Concrete Flyweight for Formatting Styles
class StyleFlyweight(TextFlyweight):
    """
    Concrete flyweight for text formatting styles.
    Stores intrinsic style properties that can be applied to text ranges.
    """
    
    def __init__(self, name: str, font_family: str, font_size: int,
                 font_weight: FontWeight, font_style: FontStyle, 
                 color: Color, background_color: Optional[Color] = None,
                 line_height: float = 1.2, letter_spacing: float = 0.0):
        # Intrinsic state
        self._name = name
        self._font_family = font_family
        self._font_size = font_size
        self._font_weight = font_weight
        self._font_style = font_style
        self._color = color
        self._background_color = background_color
        self._line_height = line_height
        self._letter_spacing = letter_spacing
        
        self._hash = hash((name, font_family, font_size, font_weight, font_style, 
                          color, background_color, line_height, letter_spacing))
    
    def render(self, context: 'RenderContext') -> str:
        """Render style with extrinsic context."""
        style_parts = [
            f"font-family: {self._font_family}",
            f"font-size: {self._font_size}px",
            f"font-weight: {self._font_weight.value}",
            f"font-style: {self._font_style.value}",
            f"color: {self._color.to_hex()}",
            f"line-height: {self._line_height}",
            f"letter-spacing: {self._letter_spacing}px"
        ]
        
        if self._background_color:
            style_parts.append(f"background-color: {self._background_color.to_hex()}")
        
        return f"<span class=\"{self._name}\" style=\"{'; '.join(style_parts)}\">"
    
    def get_memory_footprint(self) -> int:
        """Calculate approximate memory footprint."""
        base_size = sys.getsizeof(self)
        name_size = sys.getsizeof(self._name)
        font_family_size = sys.getsizeof(self._font_family)
        return base_size + name_size + font_family_size
    
    def get_intrinsic_state(self) -> Dict[str, Any]:
        """Get intrinsic state information."""
        return {
            "name": self._name,
            "font_family": self._font_family,
            "font_size": self._font_size,
            "font_weight": self._font_weight.value,
            "font_style": self._font_style.value,
            "color": self._color.to_hex(),
            "background_color": self._background_color.to_hex() if self._background_color else None,
            "line_height": self._line_height,
            "letter_spacing": self._letter_spacing
        }
    
    @property
    def name(self) -> str:
        return self._name
    
    def __hash__(self) -> int:
        return self._hash
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, StyleFlyweight):
            return False
        return self._hash == other._hash


# Flyweight Factory
class TextFlyweightFactory:
    """
    Factory for managing flyweight instances.
    Ensures that flyweights are shared and not duplicated.
    """
    
    def __init__(self):
        self._character_flyweights: Dict[Tuple, CharacterFlyweight] = {}
        self._style_flyweights: Dict[str, StyleFlyweight] = {}
        self._access_count = defaultdict(int)
        
    def get_character_flyweight(self, character: str, font_family: str, font_size: int,
                              font_weight: FontWeight, font_style: FontStyle, 
                              color: Color) -> CharacterFlyweight:
        """Get or create character flyweight."""
        key = (character, font_family, font_size, font_weight, font_style, color)
        
        if key not in self._character_flyweights:
            self._character_flyweights[key] = CharacterFlyweight(
                character, font_family, font_size, font_weight, font_style, color
            )
        
        self._access_count[key] += 1
        return self._character_flyweights[key]
    
    def get_style_flyweight(self, name: str, font_family: str, font_size: int,
                          font_weight: FontWeight, font_style: FontStyle,
                          color: Color, background_color: Optional[Color] = None,
                          line_height: float = 1.2, letter_spacing: float = 0.0) -> StyleFlyweight:
        """Get or create style flyweight."""
        if name not in self._style_flyweights:
            self._style_flyweights[name] = StyleFlyweight(
                name, font_family, font_size, font_weight, font_style,
                color, background_color, line_height, letter_spacing
            )
        
        self._access_count[name] += 1
        return self._style_flyweights[name]
    
    def create_predefined_styles(self) -> None:
        """Create common predefined styles."""
        # Standard text styles
        black = Color(0, 0, 0)
        gray = Color(128, 128, 128)
        blue = Color(0, 0, 255)
        red = Color(255, 0, 0)
        
        # Heading styles
        self.get_style_flyweight(
            "h1", "Arial", 32, FontWeight.BOLD, FontStyle.NORMAL, black, line_height=1.2
        )
        self.get_style_flyweight(
            "h2", "Arial", 24, FontWeight.BOLD, FontStyle.NORMAL, black, line_height=1.3
        )
        self.get_style_flyweight(
            "h3", "Arial", 18, FontWeight.SEMIBOLD, FontStyle.NORMAL, black, line_height=1.4
        )
        
        # Body text styles
        self.get_style_flyweight(
            "body", "Arial", 12, FontWeight.NORMAL, FontStyle.NORMAL, black, line_height=1.5
        )
        self.get_style_flyweight(
            "emphasis", "Arial", 12, FontWeight.BOLD, FontStyle.ITALIC, black
        )
        
        # Special styles
        self.get_style_flyweight(
            "code", "Courier New", 10, FontWeight.NORMAL, FontStyle.NORMAL, 
            black, Color(240, 240, 240), line_height=1.2
        )
        self.get_style_flyweight(
            "link", "Arial", 12, FontWeight.NORMAL, FontStyle.NORMAL, blue
        )
        self.get_style_flyweight(
            "error", "Arial", 12, FontWeight.BOLD, FontStyle.NORMAL, red
        )
    
    def get_factory_statistics(self) -> Dict[str, Any]:
        """Get factory usage statistics."""
        total_character_flyweights = len(self._character_flyweights)
        total_style_flyweights = len(self._style_flyweights)
        
        total_memory = sum(fw.get_memory_footprint() for fw in self._character_flyweights.values())
        total_memory += sum(fw.get_memory_footprint() for fw in self._style_flyweights.values())
        
        return {
            "character_flyweights": total_character_flyweights,
            "style_flyweights": total_style_flyweights,
            "total_flyweights": total_character_flyweights + total_style_flyweights,
            "total_memory_bytes": total_memory,
            "most_used_character": max(
                (k for k in self._access_count.keys() if isinstance(k, tuple)), 
                key=lambda k: self._access_count[k], default=None
            ),
            "most_used_style": max(
                (k for k in self._access_count.keys() if isinstance(k, str)), 
                key=lambda k: self._access_count[k], default=None
            )
        }
    
    def cleanup_unused_flyweights(self, min_usage: int = 1) -> int:
        """Remove flyweights with usage below threshold."""
        removed_count = 0
        
        # Clean up character flyweights
        keys_to_remove = [k for k, count in self._access_count.items() 
                         if isinstance(k, tuple) and count < min_usage]
        for key in keys_to_remove:
            if key in self._character_flyweights:
                del self._character_flyweights[key]
                del self._access_count[key]
                removed_count += 1
        
        # Clean up style flyweights (be more conservative)
        style_keys_to_remove = [k for k, count in self._access_count.items() 
                               if isinstance(k, str) and count < min_usage and not k.startswith(('h', 'body'))]
        for key in style_keys_to_remove:
            if key in self._style_flyweights:
                del self._style_flyweights[key]
                del self._access_count[key]
                removed_count += 1
        
        return removed_count


# Context for Extrinsic State
@dataclass
class RenderContext:
    """
    Context containing extrinsic state for rendering.
    This state varies for each use of a flyweight.
    """
    x: int  # Position
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    alignment: TextAlignment = TextAlignment.LEFT
    selected: bool = False
    cursor_position: Optional[int] = None
    
    def offset(self, dx: int, dy: int) -> 'RenderContext':
        """Create new context with position offset."""
        return RenderContext(
            self.x + dx, self.y + dy, self.width, self.height,
            self.alignment, self.selected, self.cursor_position
        )


# Context Object (uses flyweights)
class TextCharacter:
    """
    Context object that uses character flyweight.
    Stores extrinsic state and reference to shared flyweight.
    """
    
    def __init__(self, flyweight: CharacterFlyweight, x: int, y: int):
        self._flyweight = flyweight  # Reference to shared flyweight
        self._x = x  # Extrinsic state
        self._y = y
        self._selected = False
        self._visible = True
    
    def render(self) -> str:
        """Render character using flyweight and extrinsic state."""
        if not self._visible:
            return ""
        
        context = RenderContext(self._x, self._y, selected=self._selected)
        return self._flyweight.render(context)
    
    def move_to(self, x: int, y: int) -> None:
        """Move character to new position."""
        self._x = x
        self._y = y
    
    def set_selected(self, selected: bool) -> None:
        """Set selection state."""
        self._selected = selected
    
    def set_visible(self, visible: bool) -> None:
        """Set visibility."""
        self._visible = visible
    
    @property
    def flyweight(self) -> CharacterFlyweight:
        return self._flyweight
    
    @property
    def position(self) -> Tuple[int, int]:
        return (self._x, self._y)
    
    @property
    def character(self) -> str:
        return self._flyweight.character


class TextSpan:
    """
    Context object representing a span of text with shared styling.
    Uses style flyweight for efficient formatting.
    """
    
    def __init__(self, style_flyweight: StyleFlyweight, text: str, 
                 x: int, y: int, width: int):
        self._style_flyweight = style_flyweight
        self._text = text
        self._x = x
        self._y = y
        self._width = width
        self._visible = True
        self._selected_range: Optional[Tuple[int, int]] = None
    
    def render(self) -> str:
        """Render text span using style flyweight."""
        if not self._visible or not self._text:
            return ""
        
        context = RenderContext(self._x, self._y, self._width)
        style_start = self._style_flyweight.render(context)
        
        # Handle selection highlighting
        if self._selected_range:
            start, end = self._selected_range
            before = self._text[:start]
            selected = self._text[start:end]
            after = self._text[end:]
            
            content = (f"{before}"
                      f"<mark>{selected}</mark>"
                      f"{after}")
        else:
            content = self._text
        
        return f"{style_start}{content}</span>"
    
    def set_text(self, text: str) -> None:
        """Update text content."""
        self._text = text
    
    def set_position(self, x: int, y: int) -> None:
        """Update position."""
        self._x = x
        self._y = y
    
    def set_selection(self, start: int, end: int) -> None:
        """Set text selection range."""
        if 0 <= start <= end <= len(self._text):
            self._selected_range = (start, end)
    
    def clear_selection(self) -> None:
        """Clear text selection."""
        self._selected_range = None
    
    @property
    def style_name(self) -> str:
        return self._style_flyweight.name
    
    @property
    def text(self) -> str:
        return self._text
    
    @property
    def length(self) -> int:
        return len(self._text)


# Document Class (Client)
class Document:
    """
    Document class that manages text content using flyweights.
    Demonstrates the client's role in the Flyweight pattern.
    """
    
    def __init__(self, name: str, factory: TextFlyweightFactory):
        self.name = name
        self._factory = factory
        self._characters: List[TextCharacter] = []
        self._text_spans: List[TextSpan] = []
        self._cursor_position = 0
        self._selection_start: Optional[int] = None
        self._selection_end: Optional[int] = None
        
        # Document properties
        self._line_height = 16
        self._character_width = 8
        
    def insert_text(self, text: str, style_name: str = "body") -> None:
        """Insert text at cursor position with specified style."""
        style_flyweight = self._factory._style_flyweights.get(style_name)
        if not style_flyweight:
            # Create default style if not found
            style_flyweight = self._factory.get_style_flyweight(
                style_name, "Arial", 12, FontWeight.NORMAL, FontStyle.NORMAL, Color(0, 0, 0)
            )
        
        # Calculate position for new text span
        x = len(self._text_spans) * 10  # Simple positioning
        y = len(self._text_spans) * self._line_height
        width = len(text) * self._character_width
        
        text_span = TextSpan(style_flyweight, text, x, y, width)
        self._text_spans.insert(self._cursor_position, text_span)
        self._cursor_position += 1
    
    def insert_character(self, char: str, font_family: str = "Arial", 
                        font_size: int = 12, color: Color = None) -> None:
        """Insert individual character using character flyweight."""
        if color is None:
            color = Color(0, 0, 0)
        
        char_flyweight = self._factory.get_character_flyweight(
            char, font_family, font_size, FontWeight.NORMAL, FontStyle.NORMAL, color
        )
        
        # Calculate position
        x = len(self._characters) * self._character_width
        y = 0  # Single line for simplicity
        
        char_obj = TextCharacter(char_flyweight, x, y)
        self._characters.append(char_obj)
    
    def apply_style_to_range(self, start: int, end: int, style_name: str) -> bool:
        """Apply style to a range of text spans."""
        if not (0 <= start < end <= len(self._text_spans)):
            return False
        
        style_flyweight = self._factory._style_flyweights.get(style_name)
        if not style_flyweight:
            return False
        
        for i in range(start, end):
            span = self._text_spans[i]
            # Create new span with same text but different style
            new_span = TextSpan(
                style_flyweight, span.text, span._x, span._y, span._width
            )
            self._text_spans[i] = new_span
        
        return True
    
    def delete_range(self, start: int, end: int) -> bool:
        """Delete text spans in range."""
        if not (0 <= start < end <= len(self._text_spans)):
            return False
        
        del self._text_spans[start:end]
        self._cursor_position = min(self._cursor_position, len(self._text_spans))
        return True
    
    def find_text(self, search_text: str) -> List[Tuple[int, int]]:
        """Find occurrences of text in document."""
        matches = []
        
        for i, span in enumerate(self._text_spans):
            text = span.text.lower()
            search_lower = search_text.lower()
            start = 0
            
            while True:
                pos = text.find(search_lower, start)
                if pos == -1:
                    break
                matches.append((i, pos))
                start = pos + 1
        
        return matches
    
    def get_text_content(self) -> str:
        """Get plain text content of document."""
        return " ".join(span.text for span in self._text_spans)
    
    def get_character_content(self) -> str:
        """Get character-level content."""
        return "".join(char.character for char in self._characters)
    
    def render_html(self) -> str:
        """Render document as HTML."""
        html_parts = ["<div class=\"document\">"]
        
        # Render text spans
        for span in self._text_spans:
            html_parts.append(span.render())
        
        # Render individual characters
        for char in self._characters:
            html_parts.append(char.render())
        
        html_parts.append("</div>")
        return "\n".join(html_parts)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Calculate document memory usage."""
        # Calculate memory for context objects
        context_memory = sys.getsizeof(self._characters) + sys.getsizeof(self._text_spans)
        context_memory += sum(sys.getsizeof(char) for char in self._characters)
        context_memory += sum(sys.getsizeof(span) for span in self._text_spans)
        
        # Get flyweight memory (shared)
        factory_stats = self._factory.get_factory_statistics()
        flyweight_memory = factory_stats["total_memory_bytes"]
        
        return {
            "context_objects_memory": context_memory,
            "flyweight_memory_share": flyweight_memory,
            "total_characters": len(self._characters),
            "total_text_spans": len(self._text_spans),
            "text_length": len(self.get_text_content()),
            "memory_per_character": context_memory / max(1, len(self._characters)) if self._characters else 0
        }
    
    def get_style_usage(self) -> Dict[str, int]:
        """Get statistics on style usage."""
        style_counts = defaultdict(int)
        for span in self._text_spans:
            style_counts[span.style_name] += 1
        return dict(style_counts)


# Performance Comparison Class
class PerformanceComparison:
    """
    Class to demonstrate memory savings achieved by flyweight pattern.
    """
    
    @staticmethod
    def naive_implementation_memory(text_length: int, unique_styles: int) -> int:
        """Calculate memory usage without flyweight pattern."""
        # Each character would store all formatting information
        bytes_per_char = (
            1 +  # character
            50 +  # font family string
            4 +   # font size
            4 +   # font weight
            4 +   # font style
            4 +   # color (RGBA)
            8 +   # position (x, y)
            1     # flags
        )
        return text_length * bytes_per_char
    
    @staticmethod
    def flyweight_implementation_memory(text_length: int, unique_flyweights: int) -> int:
        """Calculate memory usage with flyweight pattern."""
        # Flyweight objects (shared)
        flyweight_memory = unique_flyweights * 76  # Approximate flyweight size
        
        # Context objects (one per character)
        context_memory = text_length * 16  # Position + flags per character
        
        return flyweight_memory + context_memory
    
    @staticmethod
    def calculate_savings(text_length: int, unique_styles: int) -> Dict[str, Any]:
        """Calculate memory savings percentage."""
        naive_memory = PerformanceComparison.naive_implementation_memory(text_length, unique_styles)
        flyweight_memory = PerformanceComparison.flyweight_implementation_memory(text_length, unique_styles)
        
        savings = naive_memory - flyweight_memory
        savings_percentage = (savings / naive_memory) * 100
        
        return {
            "naive_memory_bytes": naive_memory,
            "flyweight_memory_bytes": flyweight_memory,
            "memory_saved_bytes": savings,
            "memory_saved_percentage": savings_percentage,
            "compression_ratio": naive_memory / flyweight_memory
        }


# Demonstration Function
def demonstrate_flyweight_pattern():
    """Demonstrate the Flyweight pattern with text editor system."""
    
    print("=== Text Editor System - Flyweight Pattern Demo ===\n")
    
    # Create flyweight factory and setup predefined styles
    factory = TextFlyweightFactory()
    factory.create_predefined_styles()
    
    print("1. Flyweight Factory Setup:")
    print("-" * 35)
    
    initial_stats = factory.get_factory_statistics()
    print(f"Predefined styles created: {initial_stats['style_flyweights']}")
    print(f"Initial memory usage: {initial_stats['total_memory_bytes']} bytes")
    print()
    
    # Create document and add content
    doc = Document("Sample Document", factory)
    
    print("2. Document Content Creation:")
    print("-" * 35)
    
    # Add title
    doc.insert_text("Document Title", "h1")
    doc.insert_text("This is a subtitle", "h2")
    
    # Add body content
    doc.insert_text("This is the main body text of the document. ", "body")
    doc.insert_text("This text is emphasized for important information. ", "emphasis")
    doc.insert_text("Here is some code: print('Hello World') ", "code")
    doc.insert_text("This is a link to more information. ", "link")
    
    # Add more content to show flyweight sharing
    for i in range(10):
        doc.insert_text(f"Paragraph {i+1} with repeated body styling. ", "body")
    
    print(f"Document created with {len(doc._text_spans)} text spans")
    print(f"Total text length: {len(doc.get_text_content())} characters")
    print()
    
    # Add individual characters to demonstrate character flyweights
    print("3. Character-Level Flyweights:")
    print("-" * 35)
    
    sample_text = "Hello World! This demonstrates character flyweights."
    for char in sample_text:
        if char != ' ':  # Skip spaces for clarity
            doc.insert_character(char)
    
    print(f"Added {len(doc._characters)} individual character objects")
    print()
    
    # Show flyweight sharing
    print("4. Flyweight Sharing Analysis:")
    print("-" * 35)
    
    factory_stats = factory.get_factory_statistics()
    print(f"Total flyweights created: {factory_stats['total_flyweights']}")
    print(f"Character flyweights: {factory_stats['character_flyweights']}")
    print(f"Style flyweights: {factory_stats['style_flyweights']}")
    print(f"Flyweight memory usage: {factory_stats['total_memory_bytes']} bytes")
    
    if factory_stats['most_used_character']:
        char_info = factory_stats['most_used_character']
        print(f"Most reused character: '{char_info[0]}' (Arial, 12px)")
    
    if factory_stats['most_used_style']:
        print(f"Most used style: '{factory_stats['most_used_style']}'")
    print()
    
    # Document memory analysis
    print("5. Memory Usage Analysis:")
    print("-" * 35)
    
    doc_memory = doc.get_memory_usage()
    print(f"Context objects memory: {doc_memory['context_objects_memory']} bytes")
    print(f"Shared flyweight memory: {doc_memory['flyweight_memory_share']} bytes")
    print(f"Total document objects: {doc_memory['total_characters'] + doc_memory['total_text_spans']}")
    print(f"Memory per character context: {doc_memory['memory_per_character']:.2f} bytes")
    print()
    
    # Style usage statistics
    print("6. Style Usage Statistics:")
    print("-" * 35)
    
    style_usage = doc.get_style_usage()
    for style_name, count in style_usage.items():
        print(f"Style '{style_name}': used {count} times")
    print()
    
    # Performance comparison
    print("7. Performance Comparison:")
    print("-" * 35)
    
    text_length = len(doc.get_text_content()) + len(doc.get_character_content())
    unique_styles = factory_stats['total_flyweights']
    
    comparison = PerformanceComparison.calculate_savings(text_length, unique_styles)
    
    print(f"Text length: {text_length} characters")
    print(f"Unique flyweights: {unique_styles}")
    print(f"\nMemory usage comparison:")
    print(f"  Without flyweight: {comparison['naive_memory_bytes']:,} bytes")
    print(f"  With flyweight: {comparison['flyweight_memory_bytes']:,} bytes")
    print(f"  Memory saved: {comparison['memory_saved_bytes']:,} bytes")
    print(f"  Savings percentage: {comparison['memory_saved_percentage']:.1f}%")
    print(f"  Compression ratio: {comparison['compression_ratio']:.1f}x")
    print()
    
    # Document operations
    print("8. Document Operations:")
    print("-" * 30)
    
    # Search functionality
    search_results = doc.find_text("body")
    print(f"Search for 'body': found {len(search_results)} occurrences")
    
    # Apply formatting
    doc.apply_style_to_range(0, 2, "error")  # Make title and subtitle red
    print("Applied error style to title and subtitle")
    
    # Show updated style usage
    updated_style_usage = doc.get_style_usage()
    print(f"Style usage after formatting change:")
    for style_name, count in updated_style_usage.items():
        print(f"  {style_name}: {count} times")
    print()
    
    # Demonstrate scalability
    print("9. Scalability Demonstration:")
    print("-" * 35)
    
    # Create larger document to show flyweight benefits
    large_doc = Document("Large Document", factory)
    
    # Add 1000 paragraphs with repeated styles
    for i in range(1000):
        style = "body" if i % 3 == 0 else "emphasis" if i % 3 == 1 else "code"
        large_doc.insert_text(f"Paragraph {i} text content. ", style)
    
    large_doc_memory = large_doc.get_memory_usage()
    large_factory_stats = factory.get_factory_statistics()
    
    print(f"Large document with 1000 spans:")
    print(f"  Context memory: {large_doc_memory['context_objects_memory']:,} bytes")
    print(f"  Flyweight memory (shared): {large_doc_memory['flyweight_memory_share']:,} bytes")
    print(f"  Total flyweights: {large_factory_stats['total_flyweights']} (minimal increase)")
    
    # Calculate what memory would be without flyweights
    large_text_length = len(large_doc.get_text_content())
    large_comparison = PerformanceComparison.calculate_savings(large_text_length, large_factory_stats['total_flyweights'])
    
    print(f"  Memory savings: {large_comparison['memory_saved_percentage']:.1f}%")
    print(f"  Without flyweight: {large_comparison['naive_memory_bytes']:,} bytes")
    print(f"  With flyweight: {large_comparison['flyweight_memory_bytes']:,} bytes")
    print()
    
    # Cleanup demonstration
    print("10. Flyweight Cleanup:")
    print("-" * 25)
    
    # Show flyweight cleanup
    removed_count = factory.cleanup_unused_flyweights(min_usage=2)
    print(f"Cleaned up {removed_count} rarely used flyweights")
    
    final_stats = factory.get_factory_statistics()
    print(f"Flyweights after cleanup: {final_stats['total_flyweights']}")
    print()
    
    print("=== Flyweight Pattern Benefits Demonstrated ===")
    print("✓ Massive memory savings through object sharing")
    print("✓ Intrinsic state separated from extrinsic state")
    print("✓ Scalable to millions of objects")
    print("✓ Flyweight factory manages object lifecycle")
    print("✓ Performance benefits increase with scale")
    print("✓ Transparent to client code")


if __name__ == "__main__":
    demonstrate_flyweight_pattern()