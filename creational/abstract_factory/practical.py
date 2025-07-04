"""
Abstract Factory Design Pattern - Real World Implementation

Real-world example: Cross-Platform UI Components
A GUI framework that creates different sets of UI components for different platforms
(Windows, macOS, Linux) while ensuring all components in a family work together.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from enum import Enum


class Platform(Enum):
    """Available platforms for UI components."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class Button(ABC):
    """Abstract button component."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the button for the specific platform."""
        pass
    
    @abstractmethod
    def click(self) -> str:
        """Handle button click event."""
        pass


class CheckBox(ABC):
    """Abstract checkbox component."""
    
    @abstractmethod
    def render(self) -> str:
        """Render the checkbox for the specific platform."""
        pass
    
    @abstractmethod
    def check(self) -> str:
        """Handle checkbox check event."""
        pass
    
    @abstractmethod
    def collaborate_with_button(self, button: Button) -> str:
        """Demonstrate how checkbox works with button from same family."""
        pass


class WindowsButton(Button):
    """Windows-specific button implementation."""
    
    def render(self) -> str:
        return "Rendering Windows button with system theme"
    
    def click(self) -> str:
        return "Windows button clicked - opening system dialog"


class WindowsCheckBox(CheckBox):
    """Windows-specific checkbox implementation."""
    
    def render(self) -> str:
        return "Rendering Windows checkbox with system theme"
    
    def check(self) -> str:
        return "Windows checkbox checked - registry setting updated"
    
    def collaborate_with_button(self, button: Button) -> str:
        result = button.click()
        return f"Windows checkbox enables button functionality: {result}"


class MacOSButton(Button):
    """macOS-specific button implementation."""
    
    def render(self) -> str:
        return "Rendering macOS button with Aqua theme"
    
    def click(self) -> str:
        return "macOS button clicked - showing Cocoa dialog"


class MacOSCheckBox(CheckBox):
    """macOS-specific checkbox implementation."""
    
    def render(self) -> str:
        return "Rendering macOS checkbox with Aqua theme"
    
    def check(self) -> str:
        return "macOS checkbox checked - updating preferences plist"
    
    def collaborate_with_button(self, button: Button) -> str:
        result = button.click()
        return f"macOS checkbox coordinates with button: {result}"


class LinuxButton(Button):
    """Linux-specific button implementation."""
    
    def render(self) -> str:
        return "Rendering Linux button with GTK theme"
    
    def click(self) -> str:
        return "Linux button clicked - launching system application"


class LinuxCheckBox(CheckBox):
    """Linux-specific checkbox implementation."""
    
    def render(self) -> str:
        return "Rendering Linux checkbox with GTK theme"
    
    def check(self) -> str:
        return "Linux checkbox checked - updating configuration file"
    
    def collaborate_with_button(self, button: Button) -> str:
        result = button.click()
        return f"Linux checkbox integrates with button: {result}"


class GUIFactory(ABC):
    """
    Abstract factory for creating platform-specific UI components.
    Ensures that all components belong to the same platform family.
    """
    
    @abstractmethod
    def create_button(self) -> Button:
        """Create a platform-specific button."""
        pass
    
    @abstractmethod
    def create_checkbox(self) -> CheckBox:
        """Create a platform-specific checkbox."""
        pass
    
    @abstractmethod
    def get_platform_info(self) -> str:
        """Get information about the platform."""
        pass


class WindowsFactory(GUIFactory):
    """Factory for creating Windows UI components."""
    
    def create_button(self) -> Button:
        return WindowsButton()
    
    def create_checkbox(self) -> CheckBox:
        return WindowsCheckBox()
    
    def get_platform_info(self) -> str:
        return "Windows Platform - Using Win32 API and system themes"


class MacOSFactory(GUIFactory):
    """Factory for creating macOS UI components."""
    
    def create_button(self) -> Button:
        return MacOSButton()
    
    def create_checkbox(self) -> CheckBox:
        return MacOSCheckBox()
    
    def get_platform_info(self) -> str:
        return "macOS Platform - Using Cocoa framework and Aqua theme"


class LinuxFactory(GUIFactory):
    """Factory for creating Linux UI components."""
    
    def create_button(self) -> Button:
        return LinuxButton()
    
    def create_checkbox(self) -> CheckBox:
        return LinuxCheckBox()
    
    def get_platform_info(self) -> str:
        return "Linux Platform - Using GTK toolkit and system theme"


class Application:
    """
    Application that uses the GUI factory to create consistent UI components.
    """
    
    def __init__(self, factory: GUIFactory):
        self.factory = factory
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
    
    def create_ui(self) -> List[str]:
        """Create the user interface with consistent components."""
        ui_elements = []
        ui_elements.append(self.factory.get_platform_info())
        ui_elements.append(self.button.render())
        ui_elements.append(self.checkbox.render())
        return ui_elements
    
    def simulate_user_interaction(self) -> List[str]:
        """Simulate user interactions with the UI components."""
        interactions = []
        interactions.append(self.button.click())
        interactions.append(self.checkbox.check())
        interactions.append(self.checkbox.collaborate_with_button(self.button))
        return interactions


def get_platform_factory(platform: Platform) -> GUIFactory:
    """
    Factory method to get the appropriate GUI factory for the platform.
    """
    factory_map: Dict[Platform, GUIFactory] = {
        Platform.WINDOWS: WindowsFactory(),
        Platform.MACOS: MacOSFactory(),
        Platform.LINUX: LinuxFactory()
    }
    
    return factory_map.get(platform, WindowsFactory())


def main():
    """
    Real-world client code demonstrating cross-platform UI creation.
    """
    print("=== Cross-Platform UI Factory Demo ===")
    
    # Test different platforms
    platforms = [Platform.WINDOWS, Platform.MACOS, Platform.LINUX]
    
    for platform in platforms:
        print(f"\n--- {platform.value.upper()} PLATFORM ---")
        
        # Get platform-specific factory
        factory = get_platform_factory(platform)
        
        # Create application with platform-specific components
        app = Application(factory)
        
        # Create UI
        print("Creating UI:")
        ui_elements = app.create_ui()
        for element in ui_elements:
            print(f"  • {element}")
        
        # Simulate user interaction
        print("\nSimulating user interactions:")
        interactions = app.simulate_user_interaction()
        for interaction in interactions:
            print(f"  • {interaction}")
    
    # Demonstrate the benefit of the pattern
    print("\n=== Pattern Benefits Demonstration ===")
    
    # Easy platform switching
    print("\nEasy platform switching:")
    current_platform = Platform.WINDOWS
    print(f"Current platform: {current_platform.value}")
    
    factory = get_platform_factory(current_platform)
    app = Application(factory)
    
    # Switch to different platform
    new_platform = Platform.MACOS
    print(f"Switching to: {new_platform.value}")
    
    new_factory = get_platform_factory(new_platform)
    app = Application(new_factory)
    
    print("UI elements automatically updated:")
    for element in app.create_ui():
        print(f"  • {element}")
    
    # Component compatibility
    print("\nComponent compatibility guaranteed:")
    linux_factory = get_platform_factory(Platform.LINUX)
    linux_app = Application(linux_factory)
    
    # All components work together seamlessly
    interactions = linux_app.simulate_user_interaction()
    for interaction in interactions:
        print(f"  • {interaction}")


if __name__ == "__main__":
    main()