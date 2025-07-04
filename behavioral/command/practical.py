"""
Command Design Pattern - Real World Implementation

Real-world example: Smart Home Automation System
A comprehensive smart home system that uses commands to control various devices,
supports scheduling, macros, and undo operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import time
import json


class DeviceState(Enum):
    """Device states."""
    ON = "on"
    OFF = "off"
    STANDBY = "standby"


class SmartDevice(ABC):
    """
    Abstract base class for smart home devices.
    """
    
    def __init__(self, device_id: str, name: str, room: str):
        self.device_id = device_id
        self.name = name
        self.room = room
        self.state = DeviceState.OFF
        self.last_updated = datetime.now()
    
    @abstractmethod
    def turn_on(self) -> str:
        pass
    
    @abstractmethod
    def turn_off(self) -> str:
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass
    
    def update_timestamp(self) -> None:
        self.last_updated = datetime.now()


class SmartLight(SmartDevice):
    """Smart light with dimming capabilities."""
    
    def __init__(self, device_id: str, name: str, room: str):
        super().__init__(device_id, name, room)
        self.brightness = 0
        self.color = "white"
    
    def turn_on(self) -> str:
        self.state = DeviceState.ON
        if self.brightness == 0:
            self.brightness = 100
        self.update_timestamp()
        return f"Smart light '{self.name}' turned ON at {self.brightness}% brightness"
    
    def turn_off(self) -> str:
        self.state = DeviceState.OFF
        self.brightness = 0
        self.update_timestamp()
        return f"Smart light '{self.name}' turned OFF"
    
    def set_brightness(self, level: int) -> str:
        old_brightness = self.brightness
        self.brightness = max(0, min(100, level))
        if self.brightness > 0:
            self.state = DeviceState.ON
        else:
            self.state = DeviceState.OFF
        self.update_timestamp()
        return f"Light '{self.name}' brightness changed from {old_brightness}% to {self.brightness}%"
    
    def set_color(self, color: str) -> str:
        old_color = self.color
        self.color = color
        self.update_timestamp()
        return f"Light '{self.name}' color changed from {old_color} to {color}"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "room": self.room,
            "state": self.state.value,
            "brightness": self.brightness,
            "color": self.color,
            "last_updated": self.last_updated.isoformat()
        }


class SmartThermostat(SmartDevice):
    """Smart thermostat with temperature control."""
    
    def __init__(self, device_id: str, name: str, room: str):
        super().__init__(device_id, name, room)
        self.target_temperature = 20
        self.current_temperature = 22
        self.mode = "auto"
    
    def turn_on(self) -> str:
        self.state = DeviceState.ON
        self.update_timestamp()
        return f"Thermostat '{self.name}' turned ON (mode: {self.mode})"
    
    def turn_off(self) -> str:
        self.state = DeviceState.OFF
        self.update_timestamp()
        return f"Thermostat '{self.name}' turned OFF"
    
    def set_temperature(self, temperature: int) -> str:
        old_temp = self.target_temperature
        self.target_temperature = temperature
        if self.state == DeviceState.OFF:
            self.state = DeviceState.ON
        self.update_timestamp()
        return f"Thermostat '{self.name}' temperature changed from {old_temp}°C to {temperature}°C"
    
    def set_mode(self, mode: str) -> str:
        old_mode = self.mode
        self.mode = mode
        self.update_timestamp()
        return f"Thermostat '{self.name}' mode changed from {old_mode} to {mode}"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "room": self.room,
            "state": self.state.value,
            "target_temperature": self.target_temperature,
            "current_temperature": self.current_temperature,
            "mode": self.mode,
            "last_updated": self.last_updated.isoformat()
        }


class SmartSpeaker(SmartDevice):
    """Smart speaker with volume and playlist control."""
    
    def __init__(self, device_id: str, name: str, room: str):
        super().__init__(device_id, name, room)
        self.volume = 50
        self.current_song = None
        self.playlist = []
    
    def turn_on(self) -> str:
        self.state = DeviceState.ON
        self.update_timestamp()
        return f"Smart speaker '{self.name}' turned ON"
    
    def turn_off(self) -> str:
        self.state = DeviceState.OFF
        self.current_song = None
        self.update_timestamp()
        return f"Smart speaker '{self.name}' turned OFF"
    
    def set_volume(self, volume: int) -> str:
        old_volume = self.volume
        self.volume = max(0, min(100, volume))
        self.update_timestamp()
        return f"Speaker '{self.name}' volume changed from {old_volume} to {self.volume}"
    
    def play_song(self, song: str) -> str:
        if self.state == DeviceState.OFF:
            self.state = DeviceState.ON
        self.current_song = song
        self.update_timestamp()
        return f"Speaker '{self.name}' now playing: {song}"
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "room": self.room,
            "state": self.state.value,
            "volume": self.volume,
            "current_song": self.current_song,
            "last_updated": self.last_updated.isoformat()
        }


class Command(ABC):
    """
    Abstract command interface.
    """
    
    @abstractmethod
    def execute(self) -> str:
        pass
    
    @abstractmethod
    def undo(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass


class TurnOnCommand(Command):
    """Command to turn on a device."""
    
    def __init__(self, device: SmartDevice):
        self.device = device
        self.previous_state = device.state
    
    def execute(self) -> str:
        self.previous_state = self.device.state
        return self.device.turn_on()
    
    def undo(self) -> str:
        if self.previous_state == DeviceState.OFF:
            return self.device.turn_off()
        return f"Device '{self.device.name}' restored to previous state"
    
    def get_description(self) -> str:
        return f"Turn ON {self.device.name}"


class TurnOffCommand(Command):
    """Command to turn off a device."""
    
    def __init__(self, device: SmartDevice):
        self.device = device
        self.previous_state = device.state
    
    def execute(self) -> str:
        self.previous_state = self.device.state
        return self.device.turn_off()
    
    def undo(self) -> str:
        if self.previous_state == DeviceState.ON:
            return self.device.turn_on()
        return f"Device '{self.device.name}' restored to previous state"
    
    def get_description(self) -> str:
        return f"Turn OFF {self.device.name}"


class SetBrightnessCommand(Command):
    """Command to set light brightness."""
    
    def __init__(self, light: SmartLight, brightness: int):
        self.light = light
        self.brightness = brightness
        self.previous_brightness = light.brightness
    
    def execute(self) -> str:
        self.previous_brightness = self.light.brightness
        return self.light.set_brightness(self.brightness)
    
    def undo(self) -> str:
        return self.light.set_brightness(self.previous_brightness)
    
    def get_description(self) -> str:
        return f"Set {self.light.name} brightness to {self.brightness}%"


class SetTemperatureCommand(Command):
    """Command to set thermostat temperature."""
    
    def __init__(self, thermostat: SmartThermostat, temperature: int):
        self.thermostat = thermostat
        self.temperature = temperature
        self.previous_temperature = thermostat.target_temperature
    
    def execute(self) -> str:
        self.previous_temperature = self.thermostat.target_temperature
        return self.thermostat.set_temperature(self.temperature)
    
    def undo(self) -> str:
        return self.thermostat.set_temperature(self.previous_temperature)
    
    def get_description(self) -> str:
        return f"Set {self.thermostat.name} to {self.temperature}°C"


class PlayMusicCommand(Command):
    """Command to play music on smart speaker."""
    
    def __init__(self, speaker: SmartSpeaker, song: str):
        self.speaker = speaker
        self.song = song
        self.previous_song = speaker.current_song
    
    def execute(self) -> str:
        self.previous_song = self.speaker.current_song
        return self.speaker.play_song(self.song)
    
    def undo(self) -> str:
        if self.previous_song:
            return self.speaker.play_song(self.previous_song)
        else:
            return self.speaker.turn_off()
    
    def get_description(self) -> str:
        return f"Play '{self.song}' on {self.speaker.name}"


class MacroCommand(Command):
    """Command that executes multiple commands as a group."""
    
    def __init__(self, name: str, commands: List[Command]):
        self.name = name
        self.commands = commands
        self.executed_commands: List[Command] = []
    
    def execute(self) -> str:
        results = [f"Executing macro '{self.name}':"]
        self.executed_commands.clear()
        
        for command in self.commands:
            try:
                result = command.execute()
                results.append(f"  ✓ {result}")
                self.executed_commands.append(command)
            except Exception as e:
                results.append(f"  ✗ Failed: {command.get_description()} - {str(e)}")
                break
        
        return "\n".join(results)
    
    def undo(self) -> str:
        results = [f"Undoing macro '{self.name}':"]
        
        # Undo in reverse order
        for command in reversed(self.executed_commands):
            try:
                result = command.undo()
                results.append(f"  ✓ Undone: {result}")
            except Exception as e:
                results.append(f"  ✗ Failed to undo: {command.get_description()} - {str(e)}")
        
        self.executed_commands.clear()
        return "\n".join(results)
    
    def get_description(self) -> str:
        return f"Macro '{self.name}' ({len(self.commands)} commands)"


class ScheduledCommand:
    """A command scheduled to execute at a specific time."""
    
    def __init__(self, command: Command, execution_time: datetime, repeat: bool = False):
        self.command = command
        self.execution_time = execution_time
        self.repeat = repeat
        self.executed = False
    
    def is_ready_to_execute(self) -> bool:
        return datetime.now() >= self.execution_time and not self.executed
    
    def execute(self) -> str:
        if self.is_ready_to_execute():
            result = self.command.execute()
            if not self.repeat:
                self.executed = True
            else:
                # For repeating commands, schedule for next day
                self.execution_time += timedelta(days=1)
            return result
        return f"Command not ready to execute (scheduled for {self.execution_time})"


class SmartHomeController:
    """
    Smart home controller that manages devices and executes commands.
    """
    
    def __init__(self):
        self.devices: Dict[str, SmartDevice] = {}
        self.command_history: List[Command] = []
        self.scheduled_commands: List[ScheduledCommand] = []
        self.macros: Dict[str, MacroCommand] = {}
    
    def add_device(self, device: SmartDevice) -> None:
        """Add a device to the smart home system."""
        self.devices[device.device_id] = device
        print(f"Added device: {device.name} ({device.device_id}) in {device.room}")
    
    def execute_command(self, command: Command) -> str:
        """Execute a command and add it to history."""
        try:
            result = command.execute()
            self.command_history.append(command)
            print(f"🔧 Executed: {command.get_description()}")
            print(f"   Result: {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to execute {command.get_description()}: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def undo_last_command(self) -> str:
        """Undo the last executed command."""
        if not self.command_history:
            return "No commands to undo"
        
        last_command = self.command_history.pop()
        try:
            result = last_command.undo()
            print(f"↩️  Undone: {last_command.get_description()}")
            print(f"   Result: {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to undo {last_command.get_description()}: {str(e)}"
            print(f"❌ {error_msg}")
            # Re-add to history if undo failed
            self.command_history.append(last_command)
            return error_msg
    
    def create_macro(self, name: str, commands: List[Command]) -> None:
        """Create a macro command."""
        macro = MacroCommand(name, commands)
        self.macros[name] = macro
        print(f"📋 Created macro '{name}' with {len(commands)} commands")
    
    def execute_macro(self, name: str) -> str:
        """Execute a macro by name."""
        if name not in self.macros:
            return f"Macro '{name}' not found"
        
        macro = self.macros[name]
        return self.execute_command(macro)
    
    def schedule_command(self, command: Command, execution_time: datetime, repeat: bool = False) -> None:
        """Schedule a command to execute at a specific time."""
        scheduled_cmd = ScheduledCommand(command, execution_time, repeat)
        self.scheduled_commands.append(scheduled_cmd)
        repeat_text = " (repeating daily)" if repeat else ""
        print(f"⏰ Scheduled: {command.get_description()} for {execution_time}{repeat_text}")
    
    def process_scheduled_commands(self) -> List[str]:
        """Process any scheduled commands that are ready to execute."""
        results = []
        for scheduled_cmd in self.scheduled_commands[:]:  # Copy list to avoid modification during iteration
            if scheduled_cmd.is_ready_to_execute():
                result = scheduled_cmd.execute()
                results.append(f"⏰ Scheduled: {result}")
                
                # Remove non-repeating commands after execution
                if scheduled_cmd.executed:
                    self.scheduled_commands.remove(scheduled_cmd)
        
        return results
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status of a specific device."""
        if device_id in self.devices:
            return self.devices[device_id].get_status()
        return {"error": f"Device {device_id} not found"}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "total_devices": len(self.devices),
            "devices": {device_id: device.get_status() for device_id, device in self.devices.items()},
            "command_history_count": len(self.command_history),
            "scheduled_commands_count": len(self.scheduled_commands),
            "macros_count": len(self.macros),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_configuration(self) -> str:
        """Export system configuration as JSON."""
        config = {
            "devices": [device.get_status() for device in self.devices.values()],
            "macros": {name: {"name": macro.name, "commands": [cmd.get_description() for cmd in macro.commands]} 
                      for name, macro in self.macros.items()},
            "scheduled_commands": [
                {
                    "command": cmd.command.get_description(),
                    "execution_time": cmd.execution_time.isoformat(),
                    "repeat": cmd.repeat,
                    "executed": cmd.executed
                }
                for cmd in self.scheduled_commands
            ]
        }
        return json.dumps(config, indent=2)


def main():
    """
    Demonstrate the Smart Home Command system.
    """
    print("=== Smart Home Command System Demo ===")
    
    # Create smart home controller
    controller = SmartHomeController()
    
    # Create devices
    living_room_light = SmartLight("light_001", "Living Room Light", "Living Room")
    bedroom_light = SmartLight("light_002", "Bedroom Light", "Bedroom")
    thermostat = SmartThermostat("thermo_001", "Main Thermostat", "Living Room")
    speaker = SmartSpeaker("speaker_001", "Living Room Speaker", "Living Room")
    
    # Add devices to controller
    controller.add_device(living_room_light)
    controller.add_device(bedroom_light)
    controller.add_device(thermostat)
    controller.add_device(speaker)
    
    print(f"\n📱 Smart Home System initialized with {len(controller.devices)} devices")
    
    # Test individual commands
    print("\n🔧 Testing Individual Commands:")
    
    # Turn on living room light
    controller.execute_command(TurnOnCommand(living_room_light))
    
    # Set brightness
    controller.execute_command(SetBrightnessCommand(living_room_light, 75))
    
    # Set thermostat
    controller.execute_command(SetTemperatureCommand(thermostat, 22))
    
    # Play music
    controller.execute_command(PlayMusicCommand(speaker, "Relaxing Jazz Playlist"))
    
    # Test undo functionality
    print("\n↩️  Testing Undo Functionality:")
    controller.undo_last_command()  # Undo music
    controller.undo_last_command()  # Undo thermostat
    
    # Create and test macro commands
    print("\n📋 Testing Macro Commands:")
    
    # "Good Morning" macro
    good_morning_commands = [
        TurnOnCommand(living_room_light),
        SetBrightnessCommand(living_room_light, 80),
        SetTemperatureCommand(thermostat, 21),
        PlayMusicCommand(speaker, "Morning News")
    ]
    controller.create_macro("Good Morning", good_morning_commands)
    
    # "Movie Night" macro
    movie_night_commands = [
        SetBrightnessCommand(living_room_light, 20),
        TurnOffCommand(bedroom_light),
        SetTemperatureCommand(thermostat, 19),
        PlayMusicCommand(speaker, "Movie Soundtrack")
    ]
    controller.create_macro("Movie Night", movie_night_commands)
    
    # Execute macros
    print("\n🌅 Executing 'Good Morning' macro:")
    controller.execute_macro("Good Morning")
    
    print("\n🎬 Executing 'Movie Night' macro:")
    controller.execute_macro("Movie Night")
    
    # Test undo on macro
    print("\n↩️  Undoing 'Movie Night' macro:")
    controller.undo_last_command()
    
    # Test scheduled commands
    print("\n⏰ Testing Scheduled Commands:")
    
    # Schedule commands for immediate execution (for demo purposes)
    now = datetime.now()
    
    # Schedule a command for 1 second from now
    wake_up_time = now + timedelta(seconds=1)
    controller.schedule_command(
        TurnOnCommand(bedroom_light),
        wake_up_time
    )
    
    # Schedule a repeating command
    daily_temp_time = now + timedelta(seconds=2)
    controller.schedule_command(
        SetTemperatureCommand(thermostat, 20),
        daily_temp_time,
        repeat=True
    )
    
    # Wait and process scheduled commands
    print("⏳ Waiting for scheduled commands...")
    time.sleep(3)
    
    scheduled_results = controller.process_scheduled_commands()
    for result in scheduled_results:
        print(result)
    
    # Display system status
    print("\n📊 System Status:")
    status = controller.get_system_status()
    print(f"  Total Devices: {status['total_devices']}")
    print(f"  Command History: {status['command_history_count']} commands")
    print(f"  Scheduled Commands: {status['scheduled_commands_count']} pending")
    print(f"  Macros: {status['macros_count']} defined")
    
    # Show device statuses
    print("\n💡 Device Statuses:")
    for device_id, device_status in status['devices'].items():
        print(f"  {device_status['name']} ({device_status['room']}):")
        print(f"    State: {device_status['state']}")
        if 'brightness' in device_status:
            print(f"    Brightness: {device_status['brightness']}%")
        if 'target_temperature' in device_status:
            print(f"    Temperature: {device_status['target_temperature']}°C")
        if 'current_song' in device_status:
            print(f"    Playing: {device_status['current_song'] or 'Nothing'}")
    
    # Export configuration
    print("\n💾 Exporting System Configuration:")
    config_json = controller.export_configuration()
    print("Configuration exported successfully!")
    print(f"Configuration size: {len(config_json)} characters")
    
    # Test complex scenario
    print("\n🏠 Complex Scenario - 'Leaving Home':")
    
    leaving_home_commands = [
        TurnOffCommand(living_room_light),
        TurnOffCommand(bedroom_light),
        TurnOffCommand(speaker),
        SetTemperatureCommand(thermostat, 16)  # Energy saving mode
    ]
    
    controller.create_macro("Leaving Home", leaving_home_commands)
    controller.execute_macro("Leaving Home")
    
    print("\n📊 Final System Status:")
    final_status = controller.get_system_status()
    print(f"  Commands executed: {final_status['command_history_count']}")
    print(f"  Macros available: {list(controller.macros.keys())}")


if __name__ == "__main__":
    main()