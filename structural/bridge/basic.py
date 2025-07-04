"""
Bridge Design Pattern - Gang of Four Implementation

Intent: Decouple an abstraction from its implementation so that the two can vary independently.

Structure:
- Abstraction: defines the abstraction's interface and maintains a reference to Implementor
- RefinedAbstraction: extends the interface defined by Abstraction
- Implementor: defines the interface for implementation classes
- ConcreteImplementor: implements the Implementor interface
"""

from abc import ABC, abstractmethod
from typing import Any, List


class Implementor(ABC):
    """
    The Implementor defines the interface for implementation classes.
    It doesn't have to match the Abstraction's interface. In fact, the two
    interfaces can be entirely different. Typically the Implementor interface
    provides only primitive operations, while the Abstraction defines higher-
    level operations based on those primitives.
    """
    
    @abstractmethod
    def operation_implementation(self) -> str:
        """Basic implementation operation."""
        pass


class ConcreteImplementorA(Implementor):
    """
    Each Concrete Implementor corresponds to a specific platform and implements
    the Implementor interface using that platform's API.
    """
    
    def operation_implementation(self) -> str:
        return "ConcreteImplementorA: Here's the result on platform A."


class ConcreteImplementorB(Implementor):
    """
    Concrete Implementor for platform B.
    """
    
    def operation_implementation(self) -> str:
        return "ConcreteImplementorB: Here's the result on platform B."


class Abstraction:
    """
    The Abstraction defines the interface for the "control" part of the two
    class hierarchies. It maintains a reference to an object of the
    Implementor hierarchy and delegates all of the real work to this object.
    """
    
    def __init__(self, implementor: Implementor):
        self._implementor = implementor
    
    def operation(self) -> str:
        """
        The Abstraction delegates work to the Implementor object.
        """
        return f"Abstraction: Base operation with:\n{self._implementor.operation_implementation()}"


class ExtendedAbstraction(Abstraction):
    """
    You can extend the Abstraction without changing the Implementor classes.
    """
    
    def operation(self) -> str:
        """
        Extended operation that builds upon the base operation.
        """
        return f"ExtendedAbstraction: Extended operation with:\n{self._implementor.operation_implementation()}"
    
    def extended_operation(self) -> str:
        """
        Additional operation specific to ExtendedAbstraction.
        """
        return f"ExtendedAbstraction: Additional operation with:\n{self._implementor.operation_implementation()}"


# More complex example: Media Player Bridge
class MediaPlayerImplementor(ABC):
    """
    Implementor interface for media players.
    """
    
    @abstractmethod
    def play_audio(self, filename: str) -> str:
        """Play audio file."""
        pass
    
    @abstractmethod
    def play_video(self, filename: str) -> str:
        """Play video file."""
        pass
    
    @abstractmethod
    def stop(self) -> str:
        """Stop playback."""
        pass
    
    @abstractmethod
    def get_volume(self) -> int:
        """Get current volume."""
        pass
    
    @abstractmethod
    def set_volume(self, volume: int) -> str:
        """Set volume."""
        pass


class WindowsMediaPlayer(MediaPlayerImplementor):
    """
    Windows implementation of media player.
    """
    
    def __init__(self):
        self._volume = 50
        self._is_playing = False
    
    def play_audio(self, filename: str) -> str:
        self._is_playing = True
        return f"Windows Media Player: Playing audio '{filename}' using DirectSound API"
    
    def play_video(self, filename: str) -> str:
        self._is_playing = True
        return f"Windows Media Player: Playing video '{filename}' using DirectShow API"
    
    def stop(self) -> str:
        self._is_playing = False
        return "Windows Media Player: Stopped playback using Windows API"
    
    def get_volume(self) -> int:
        return self._volume
    
    def set_volume(self, volume: int) -> str:
        self._volume = max(0, min(100, volume))
        return f"Windows Media Player: Volume set to {self._volume}% using Windows Audio API"


class LinuxMediaPlayer(MediaPlayerImplementor):
    """
    Linux implementation of media player.
    """
    
    def __init__(self):
        self._volume = 75
        self._is_playing = False
    
    def play_audio(self, filename: str) -> str:
        self._is_playing = True
        return f"Linux Media Player: Playing audio '{filename}' using ALSA"
    
    def play_video(self, filename: str) -> str:
        self._is_playing = True
        return f"Linux Media Player: Playing video '{filename}' using V4L2"
    
    def stop(self) -> str:
        self._is_playing = False
        return "Linux Media Player: Stopped playback using Linux audio system"
    
    def get_volume(self) -> int:
        return self._volume
    
    def set_volume(self, volume: int) -> str:
        self._volume = max(0, min(100, volume))
        return f"Linux Media Player: Volume set to {self._volume}% using PulseAudio"


class MacOSMediaPlayer(MediaPlayerImplementor):
    """
    macOS implementation of media player.
    """
    
    def __init__(self):
        self._volume = 60
        self._is_playing = False
    
    def play_audio(self, filename: str) -> str:
        self._is_playing = True
        return f"macOS Media Player: Playing audio '{filename}' using Core Audio"
    
    def play_video(self, filename: str) -> str:
        self._is_playing = True
        return f"macOS Media Player: Playing video '{filename}' using AVFoundation"
    
    def stop(self) -> str:
        self._is_playing = False
        return "macOS Media Player: Stopped playback using Core Audio"
    
    def get_volume(self) -> int:
        return self._volume
    
    def set_volume(self, volume: int) -> str:
        self._volume = max(0, min(100, volume))
        return f"macOS Media Player: Volume set to {self._volume}% using Core Audio"


class MediaPlayer:
    """
    Abstraction for media player functionality.
    """
    
    def __init__(self, implementor: MediaPlayerImplementor):
        self._implementor = implementor
        self._playlist: List[str] = []
        self._current_track = 0
    
    def play(self, filename: str) -> str:
        """Play media file."""
        if filename.endswith(('.mp3', '.wav', '.flac')):
            return self._implementor.play_audio(filename)
        elif filename.endswith(('.mp4', '.avi', '.mkv')):
            return self._implementor.play_video(filename)
        else:
            return f"Unsupported file format: {filename}"
    
    def stop(self) -> str:
        """Stop playback."""
        return self._implementor.stop()
    
    def set_volume(self, volume: int) -> str:
        """Set volume."""
        return self._implementor.set_volume(volume)
    
    def get_volume(self) -> int:
        """Get volume."""
        return self._implementor.get_volume()
    
    def add_to_playlist(self, filename: str) -> None:
        """Add file to playlist."""
        self._playlist.append(filename)
    
    def play_playlist(self) -> List[str]:
        """Play entire playlist."""
        results = []
        for filename in self._playlist:
            results.append(self.play(filename))
        return results


class AdvancedMediaPlayer(MediaPlayer):
    """
    Advanced media player with additional features.
    """
    
    def __init__(self, implementor: MediaPlayerImplementor):
        super().__init__(implementor)
        self._shuffle = False
        self._repeat = False
    
    def shuffle_playlist(self) -> str:
        """Enable shuffle mode."""
        self._shuffle = True
        return "Shuffle mode enabled"
    
    def repeat_playlist(self) -> str:
        """Enable repeat mode."""
        self._repeat = True
        return "Repeat mode enabled"
    
    def play_with_effects(self, filename: str, effect: str) -> str:
        """Play with audio effects."""
        base_result = self.play(filename)
        return f"{base_result} with {effect} effect applied"
    
    def get_equalizer_settings(self) -> str:
        """Get equalizer settings (platform-specific)."""
        # This demonstrates how abstraction can add functionality
        # that uses the implementor but isn't directly provided by it
        volume = self._implementor.get_volume()
        if isinstance(self._implementor, WindowsMediaPlayer):
            return f"Windows Equalizer: Bass boost enabled, Volume: {volume}%"
        elif isinstance(self._implementor, LinuxMediaPlayer):
            return f"Linux Equalizer: Custom EQ profile, Volume: {volume}%"
        elif isinstance(self._implementor, MacOSMediaPlayer):
            return f"macOS Equalizer: Spatial audio enabled, Volume: {volume}%"
        else:
            return f"Generic Equalizer: Default settings, Volume: {volume}%"


# Remote Control Bridge Example
class RemoteControlImplementor(ABC):
    """
    Implementor interface for device control.
    """
    
    @abstractmethod
    def power_on(self) -> str:
        """Turn device on."""
        pass
    
    @abstractmethod
    def power_off(self) -> str:
        """Turn device off."""
        pass
    
    @abstractmethod
    def set_channel(self, channel: int) -> str:
        """Set channel/input."""
        pass
    
    @abstractmethod
    def adjust_volume(self, volume: int) -> str:
        """Adjust volume."""
        pass


class TVRemoteImplementor(RemoteControlImplementor):
    """
    TV remote control implementation.
    """
    
    def __init__(self):
        self._is_on = False
        self._channel = 1
        self._volume = 50
    
    def power_on(self) -> str:
        self._is_on = True
        return "TV: Powered on"
    
    def power_off(self) -> str:
        self._is_on = False
        return "TV: Powered off"
    
    def set_channel(self, channel: int) -> str:
        if self._is_on:
            self._channel = channel
            return f"TV: Channel set to {channel}"
        return "TV: Cannot change channel - TV is off"
    
    def adjust_volume(self, volume: int) -> str:
        if self._is_on:
            self._volume = max(0, min(100, volume))
            return f"TV: Volume set to {self._volume}"
        return "TV: Cannot adjust volume - TV is off"


class StereoRemoteImplementor(RemoteControlImplementor):
    """
    Stereo system remote control implementation.
    """
    
    def __init__(self):
        self._is_on = False
        self._input = "CD"
        self._volume = 30
    
    def power_on(self) -> str:
        self._is_on = True
        return "Stereo: Powered on"
    
    def power_off(self) -> str:
        self._is_on = False
        return "Stereo: Powered off"
    
    def set_channel(self, input_num: int) -> str:
        if self._is_on:
            inputs = ["CD", "Radio", "AUX", "Bluetooth"]
            if 0 <= input_num < len(inputs):
                self._input = inputs[input_num]
                return f"Stereo: Input set to {self._input}"
            return "Stereo: Invalid input number"
        return "Stereo: Cannot change input - Stereo is off"
    
    def adjust_volume(self, volume: int) -> str:
        if self._is_on:
            self._volume = max(0, min(100, volume))
            return f"Stereo: Volume set to {self._volume}"
        return "Stereo: Cannot adjust volume - Stereo is off"


class RemoteControl:
    """
    Basic remote control abstraction.
    """
    
    def __init__(self, implementor: RemoteControlImplementor):
        self._implementor = implementor
    
    def power_toggle(self) -> str:
        """Toggle power state."""
        # This is a higher-level operation built on primitive operations
        on_result = self._implementor.power_on()
        off_result = self._implementor.power_off()
        return f"Power toggled: {on_result} -> {off_result}"
    
    def channel_up(self, current_channel: int) -> str:
        """Go to next channel."""
        return self._implementor.set_channel(current_channel + 1)
    
    def channel_down(self, current_channel: int) -> str:
        """Go to previous channel."""
        return self._implementor.set_channel(max(1, current_channel - 1))
    
    def volume_up(self, current_volume: int) -> str:
        """Increase volume."""
        return self._implementor.adjust_volume(current_volume + 10)
    
    def volume_down(self, current_volume: int) -> str:
        """Decrease volume."""
        return self._implementor.adjust_volume(current_volume - 10)


def client_code(abstraction: Abstraction) -> None:
    """
    Client code that works with any abstraction.
    """
    print(abstraction.operation())


def main():
    """
    The client code.
    """
    print("=== Bridge Pattern Demo ===")
    
    # Simple bridge example
    print("\n--- Simple Bridge Example ---")
    
    # Client code can work with any combination of abstraction and implementation
    implementor_a = ConcreteImplementorA()
    abstraction = Abstraction(implementor_a)
    client_code(abstraction)
    
    print()
    
    implementor_b = ConcreteImplementorB()
    abstraction = ExtendedAbstraction(implementor_b)
    client_code(abstraction)
    
    # Extended abstraction with additional functionality
    extended = ExtendedAbstraction(implementor_a)
    print(f"\n{extended.extended_operation()}")
    
    # Media player bridge example
    print("\n--- Media Player Bridge Example ---")
    
    # Test different platform implementations
    platforms = [
        ("Windows", WindowsMediaPlayer()),
        ("Linux", LinuxMediaPlayer()),
        ("macOS", MacOSMediaPlayer())
    ]
    
    test_files = ["music.mp3", "video.mp4", "podcast.wav"]
    
    for platform_name, platform_impl in platforms:
        print(f"\n{platform_name} Platform:")
        
        # Basic media player
        player = MediaPlayer(platform_impl)
        
        for file in test_files:
            print(f"  {player.play(file)}")
        
        # Volume control
        print(f"  Current volume: {player.get_volume()}%")
        print(f"  {player.set_volume(80)}")
        
        # Advanced media player
        advanced_player = AdvancedMediaPlayer(platform_impl)
        print(f"  {advanced_player.play_with_effects('song.mp3', 'reverb')}")
        print(f"  {advanced_player.get_equalizer_settings()}")
    
    # Playlist example
    print("\n--- Playlist Example ---")
    
    playlist_player = AdvancedMediaPlayer(WindowsMediaPlayer())
    playlist_player.add_to_playlist("song1.mp3")
    playlist_player.add_to_playlist("song2.mp3")
    playlist_player.add_to_playlist("video1.mp4")
    
    print("Playing playlist:")
    playlist_results = playlist_player.play_playlist()
    for result in playlist_results:
        print(f"  {result}")
    
    # Remote control bridge example
    print("\n--- Remote Control Bridge Example ---")
    
    # TV remote
    tv_remote = RemoteControl(TVRemoteImplementor())
    print("TV Remote Control:")
    print(f"  {tv_remote.power_toggle()}")
    print(f"  {tv_remote.channel_up(5)}")
    print(f"  {tv_remote.volume_up(50)}")
    
    # Stereo remote
    stereo_remote = RemoteControl(StereoRemoteImplementor())
    print("\nStereo Remote Control:")
    print(f"  {stereo_remote.power_toggle()}")
    print(f"  {stereo_remote.channel_up(0)}")  # Switch to Radio
    print(f"  {stereo_remote.volume_down(30)}")
    
    # Demonstrate bridge benefits
    print("\n--- Bridge Pattern Benefits ---")
    print("Benefits demonstrated:")
    print("1. Abstraction and implementation can vary independently")
    print("2. Platform-specific code is isolated in implementors")
    print("3. New platforms can be added without changing abstractions")
    print("4. New abstractions can be added without changing implementors")
    print("5. Runtime binding between abstraction and implementation")
    
    # Runtime platform switching
    print("\n--- Runtime Platform Switching ---")
    
    # Start with Windows implementation
    media_player = MediaPlayer(WindowsMediaPlayer())
    print(f"Initial: {media_player.play('test.mp3')}")
    
    # Switch to Linux implementation at runtime
    media_player._implementor = LinuxMediaPlayer()
    print(f"After switch: {media_player.play('test.mp3')}")
    
    # This demonstrates that the same abstraction can work with different implementations


if __name__ == "__main__":
    main()