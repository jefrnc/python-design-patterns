"""
Facade Design Pattern - Real World Implementation

A real-world example demonstrating the Facade pattern through a 
smart home automation system that provides a simplified interface
to control complex subsystems like lighting, security, climate,
entertainment, and energy management.

This example shows how to:
- Simplify complex subsystem interactions
- Provide a unified interface for multiple systems
- Hide implementation details from clients
- Support both basic and advanced operations
- Integrate multiple third-party services
- Manage system states and configurations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, time, timedelta
import logging


# Enums for system states and modes
class DeviceStatus(Enum):
    """Status of smart home devices."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class SecurityLevel(Enum):
    """Security system levels."""
    DISARMED = "disarmed"
    HOME = "home"
    AWAY = "away"
    VACATION = "vacation"


class ClimateMode(Enum):
    """Climate control modes."""
    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    ECO = "eco"


class SceneType(Enum):
    """Predefined scene types."""
    MORNING = "morning"
    WORK = "work"
    EVENING = "evening"
    NIGHT = "night"
    PARTY = "party"
    MOVIE = "movie"
    VACATION = "vacation"


@dataclass
class DeviceInfo:
    """Information about a smart device."""
    device_id: str
    name: str
    device_type: str
    location: str
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_update: datetime = field(default_factory=datetime.now)
    battery_level: Optional[int] = None
    firmware_version: str = "1.0.0"
    manufacturer: str = "Generic"


@dataclass
class SensorReading:
    """Sensor reading data."""
    sensor_id: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)


# Complex Subsystem 1: Lighting Control
class LightingController:
    """Complex lighting control subsystem."""
    
    def __init__(self):
        self.lights: Dict[str, Dict] = {}
        self.zones: Dict[str, List[str]] = {}
        self.schedules: Dict[str, List] = {}
        
    def register_light(self, light_id: str, name: str, location: str, 
                      max_brightness: int = 100, supports_color: bool = False) -> None:
        """Register a new smart light."""
        self.lights[light_id] = {
            "name": name,
            "location": location,
            "is_on": False,
            "brightness": 0,
            "color": (255, 255, 255) if supports_color else None,
            "max_brightness": max_brightness,
            "supports_color": supports_color,
            "energy_usage": 0.0,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered light: {name} in {location}")
    
    def turn_on_light(self, light_id: str, brightness: int = 100) -> bool:
        """Turn on a specific light."""
        if light_id in self.lights:
            light = self.lights[light_id]
            light["is_on"] = True
            light["brightness"] = min(brightness, light["max_brightness"])
            light["energy_usage"] = light["brightness"] * 0.1  # Watts
            logging.info(f"Turned on {light['name']} at {brightness}% brightness")
            return True
        return False
    
    def turn_off_light(self, light_id: str) -> bool:
        """Turn off a specific light."""
        if light_id in self.lights:
            light = self.lights[light_id]
            light["is_on"] = False
            light["brightness"] = 0
            light["energy_usage"] = 0.0
            logging.info(f"Turned off {light['name']}")
            return True
        return False
    
    def set_color(self, light_id: str, rgb: Tuple[int, int, int]) -> bool:
        """Set light color (if supported)."""
        if light_id in self.lights and self.lights[light_id]["supports_color"]:
            self.lights[light_id]["color"] = rgb
            logging.info(f"Set color for {self.lights[light_id]['name']} to RGB{rgb}")
            return True
        return False
    
    def create_zone(self, zone_name: str, light_ids: List[str]) -> None:
        """Create a lighting zone."""
        self.zones[zone_name] = light_ids
        logging.info(f"Created lighting zone: {zone_name} with {len(light_ids)} lights")
    
    def control_zone(self, zone_name: str, is_on: bool, brightness: int = 100) -> bool:
        """Control all lights in a zone."""
        if zone_name in self.zones:
            for light_id in self.zones[zone_name]:
                if is_on:
                    self.turn_on_light(light_id, brightness)
                else:
                    self.turn_off_light(light_id)
            return True
        return False
    
    def get_total_energy_usage(self) -> float:
        """Get total energy usage of all lights."""
        return sum(light["energy_usage"] for light in self.lights.values())


# Complex Subsystem 2: Security System
class SecuritySystem:
    """Complex security system subsystem."""
    
    def __init__(self):
        self.sensors: Dict[str, Dict] = {}
        self.cameras: Dict[str, Dict] = {}
        self.locks: Dict[str, Dict] = {}
        self.alarm_level = SecurityLevel.DISARMED
        self.alarm_history: List[Dict] = []
        self.is_monitoring = False
        
    def register_sensor(self, sensor_id: str, sensor_type: str, location: str) -> None:
        """Register a security sensor."""
        self.sensors[sensor_id] = {
            "type": sensor_type,  # motion, door, window, glass_break
            "location": location,
            "is_active": True,
            "last_triggered": None,
            "battery_level": 85,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered {sensor_type} sensor in {location}")
    
    def register_camera(self, camera_id: str, location: str, resolution: str = "1080p") -> None:
        """Register a security camera."""
        self.cameras[camera_id] = {
            "location": location,
            "resolution": resolution,
            "is_recording": False,
            "night_vision": True,
            "motion_detection": True,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered camera in {location}")
    
    def register_lock(self, lock_id: str, location: str, lock_type: str = "smart") -> None:
        """Register a smart lock."""
        self.locks[lock_id] = {
            "location": location,
            "type": lock_type,
            "is_locked": True,
            "auto_lock_delay": 30,  # seconds
            "access_codes": [],
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered {lock_type} lock at {location}")
    
    def set_security_level(self, level: SecurityLevel) -> bool:
        """Set the security system level."""
        self.alarm_level = level
        
        if level == SecurityLevel.DISARMED:
            self.is_monitoring = False
            self._deactivate_all_sensors()
        elif level == SecurityLevel.HOME:
            self.is_monitoring = True
            self._activate_perimeter_sensors()
        elif level in [SecurityLevel.AWAY, SecurityLevel.VACATION]:
            self.is_monitoring = True
            self._activate_all_sensors()
            self._lock_all_doors()
        
        logging.info(f"Security level set to: {level.value}")
        return True
    
    def _activate_all_sensors(self) -> None:
        """Activate all security sensors."""
        for sensor in self.sensors.values():
            sensor["is_active"] = True
    
    def _activate_perimeter_sensors(self) -> None:
        """Activate only perimeter sensors (doors, windows)."""
        for sensor in self.sensors.values():
            sensor["is_active"] = sensor["type"] in ["door", "window", "glass_break"]
    
    def _deactivate_all_sensors(self) -> None:
        """Deactivate all sensors."""
        for sensor in self.sensors.values():
            sensor["is_active"] = False
    
    def _lock_all_doors(self) -> None:
        """Lock all smart locks."""
        for lock in self.locks.values():
            lock["is_locked"] = True
    
    def trigger_alarm(self, sensor_id: str, alert_type: str) -> None:
        """Trigger security alarm."""
        alarm_event = {
            "timestamp": datetime.now(),
            "sensor_id": sensor_id,
            "alert_type": alert_type,
            "security_level": self.alarm_level.value
        }
        self.alarm_history.append(alarm_event)
        logging.warning(f"SECURITY ALERT: {alert_type} detected by {sensor_id}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive security system status."""
        return {
            "security_level": self.alarm_level.value,
            "monitoring_active": self.is_monitoring,
            "sensors_count": len(self.sensors),
            "cameras_count": len(self.cameras),
            "locks_count": len(self.locks),
            "recent_alerts": len([a for a in self.alarm_history 
                                if a["timestamp"] > datetime.now() - timedelta(hours=24)])
        }


# Complex Subsystem 3: Climate Control
class ClimateController:
    """Complex climate control subsystem."""
    
    def __init__(self):
        self.thermostats: Dict[str, Dict] = {}
        self.hvac_zones: Dict[str, Dict] = {}
        self.sensors: Dict[str, Dict] = {}
        self.schedules: Dict[str, List] = {}
        
    def register_thermostat(self, thermostat_id: str, location: str) -> None:
        """Register a smart thermostat."""
        self.thermostats[thermostat_id] = {
            "location": location,
            "current_temp": 22.0,
            "target_temp": 22.0,
            "mode": ClimateMode.AUTO,
            "fan_speed": "auto",
            "humidity": 45,
            "is_online": True,
            "energy_usage": 0.0
        }
        logging.info(f"Registered thermostat in {location}")
    
    def register_sensor(self, sensor_id: str, location: str, sensor_type: str) -> None:
        """Register climate sensor."""
        self.sensors[sensor_id] = {
            "location": location,
            "type": sensor_type,  # temperature, humidity, air_quality
            "current_reading": 0.0,
            "last_update": datetime.now(),
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered {sensor_type} sensor in {location}")
    
    def set_temperature(self, thermostat_id: str, target_temp: float, mode: ClimateMode = None) -> bool:
        """Set target temperature for a thermostat."""
        if thermostat_id in self.thermostats:
            thermostat = self.thermostats[thermostat_id]
            thermostat["target_temp"] = target_temp
            
            if mode:
                thermostat["mode"] = mode
            
            # Simulate energy usage calculation
            temp_diff = abs(target_temp - thermostat["current_temp"])
            thermostat["energy_usage"] = temp_diff * 100  # Watts
            
            logging.info(f"Set {thermostat['location']} thermostat to {target_temp}°C")
            return True
        return False
    
    def create_hvac_zone(self, zone_name: str, thermostat_ids: List[str]) -> None:
        """Create an HVAC zone."""
        self.hvac_zones[zone_name] = {
            "thermostats": thermostat_ids,
            "average_temp": 0.0,
            "target_temp": 22.0,
            "mode": ClimateMode.AUTO
        }
        logging.info(f"Created HVAC zone: {zone_name}")
    
    def control_zone(self, zone_name: str, target_temp: float, mode: ClimateMode) -> bool:
        """Control entire HVAC zone."""
        if zone_name in self.hvac_zones:
            zone = self.hvac_zones[zone_name]
            zone["target_temp"] = target_temp
            zone["mode"] = mode
            
            for thermostat_id in zone["thermostats"]:
                self.set_temperature(thermostat_id, target_temp, mode)
            
            return True
        return False
    
    def get_average_temperature(self) -> float:
        """Get average temperature across all thermostats."""
        if not self.thermostats:
            return 0.0
        
        total_temp = sum(t["current_temp"] for t in self.thermostats.values())
        return total_temp / len(self.thermostats)
    
    def get_total_energy_usage(self) -> float:
        """Get total HVAC energy usage."""
        return sum(t["energy_usage"] for t in self.thermostats.values())


# Complex Subsystem 4: Entertainment System
class EntertainmentSystem:
    """Complex entertainment system subsystem."""
    
    def __init__(self):
        self.devices: Dict[str, Dict] = {}
        self.speakers: Dict[str, Dict] = {}
        self.streaming_services: Dict[str, Dict] = {}
        self.playlists: Dict[str, List] = {}
        
    def register_tv(self, tv_id: str, location: str, brand: str = "Generic") -> None:
        """Register a smart TV."""
        self.devices[tv_id] = {
            "type": "tv",
            "location": location,
            "brand": brand,
            "is_on": False,
            "volume": 30,
            "current_input": "HDMI1",
            "current_channel": None,
            "apps": ["Netflix", "YouTube", "Spotify"],
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered {brand} TV in {location}")
    
    def register_speaker(self, speaker_id: str, location: str, is_smart: bool = True) -> None:
        """Register a speaker."""
        self.speakers[speaker_id] = {
            "location": location,
            "is_smart": is_smart,
            "is_on": False,
            "volume": 50,
            "current_source": None,
            "supports_multiroom": is_smart,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered speaker in {location}")
    
    def register_streaming_service(self, service_name: str, credentials: Dict) -> None:
        """Register streaming service."""
        self.streaming_services[service_name] = {
            "credentials": credentials,
            "is_authenticated": True,
            "subscription_type": "premium",
            "available_content": []
        }
        logging.info(f"Registered streaming service: {service_name}")
    
    def power_on_device(self, device_id: str) -> bool:
        """Power on entertainment device."""
        if device_id in self.devices:
            self.devices[device_id]["is_on"] = True
            logging.info(f"Powered on {self.devices[device_id]['type']} in {self.devices[device_id]['location']}")
            return True
        elif device_id in self.speakers:
            self.speakers[device_id]["is_on"] = True
            logging.info(f"Powered on speaker in {self.speakers[device_id]['location']}")
            return True
        return False
    
    def set_volume(self, device_id: str, volume: int) -> bool:
        """Set device volume."""
        volume = max(0, min(100, volume))  # Clamp between 0-100
        
        if device_id in self.devices:
            self.devices[device_id]["volume"] = volume
            return True
        elif device_id in self.speakers:
            self.speakers[device_id]["volume"] = volume
            return True
        return False
    
    def play_content(self, device_id: str, content_type: str, content_id: str) -> bool:
        """Play specific content."""
        if device_id in self.devices or device_id in self.speakers:
            logging.info(f"Playing {content_type}: {content_id} on {device_id}")
            return True
        return False
    
    def create_multiroom_session(self, speaker_ids: List[str], playlist: str) -> bool:
        """Create multiroom audio session."""
        smart_speakers = [sid for sid in speaker_ids 
                         if sid in self.speakers and self.speakers[sid]["supports_multiroom"]]
        
        if smart_speakers:
            for speaker_id in smart_speakers:
                self.speakers[speaker_id]["current_source"] = f"multiroom_{playlist}"
                self.power_on_device(speaker_id)
            
            logging.info(f"Started multiroom session with {len(smart_speakers)} speakers")
            return True
        return False


# Complex Subsystem 5: Energy Management
class EnergyManager:
    """Complex energy management subsystem."""
    
    def __init__(self):
        self.smart_outlets: Dict[str, Dict] = {}
        self.solar_panels: Dict[str, Dict] = {}
        self.battery_storage: Dict[str, Dict] = {}
        self.energy_usage_history: List[Dict] = []
        
    def register_smart_outlet(self, outlet_id: str, location: str, max_power: float = 1800) -> None:
        """Register a smart outlet."""
        self.smart_outlets[outlet_id] = {
            "location": location,
            "is_on": False,
            "current_power": 0.0,
            "max_power": max_power,
            "total_energy": 0.0,
            "connected_device": None,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered smart outlet in {location}")
    
    def register_solar_panel(self, panel_id: str, capacity: float, efficiency: float = 0.2) -> None:
        """Register solar panel."""
        self.solar_panels[panel_id] = {
            "capacity": capacity,  # Watts
            "efficiency": efficiency,
            "current_generation": 0.0,
            "total_generated": 0.0,
            "status": DeviceStatus.ONLINE
        }
        logging.info(f"Registered solar panel with {capacity}W capacity")
    
    def control_outlet(self, outlet_id: str, is_on: bool) -> bool:
        """Control smart outlet."""
        if outlet_id in self.smart_outlets:
            outlet = self.smart_outlets[outlet_id]
            outlet["is_on"] = is_on
            outlet["current_power"] = outlet["max_power"] * 0.7 if is_on else 0.0
            logging.info(f"{'Turned on' if is_on else 'Turned off'} outlet in {outlet['location']}")
            return True
        return False
    
    def get_total_consumption(self) -> float:
        """Get total energy consumption."""
        return sum(outlet["current_power"] for outlet in self.smart_outlets.values())
    
    def get_total_generation(self) -> float:
        """Get total solar generation."""
        return sum(panel["current_generation"] for panel in self.solar_panels.values())
    
    def get_energy_balance(self) -> Dict[str, float]:
        """Get energy consumption vs generation balance."""
        consumption = self.get_total_consumption()
        generation = self.get_total_generation()
        
        return {
            "consumption": consumption,
            "generation": generation,
            "net_usage": consumption - generation,
            "efficiency": (generation / consumption * 100) if consumption > 0 else 0
        }


# Main Facade Class
class SmartHomeFacade:
    """
    Smart Home System Facade
    
    Provides a simplified interface to control all smart home subsystems.
    This is the main Facade class that hides the complexity of individual subsystems.
    """
    
    def __init__(self):
        # Initialize all subsystems
        self.lighting = LightingController()
        self.security = SecuritySystem()
        self.climate = ClimateController()
        self.entertainment = EntertainmentSystem()
        self.energy = EnergyManager()
        
        # System state
        self.is_initialized = False
        self.current_scene = None
        self.system_settings = {
            "auto_mode": True,
            "energy_saving": True,
            "security_notifications": True
        }
        
        self._setup_default_configuration()
    
    def _setup_default_configuration(self) -> None:
        """Setup default smart home configuration."""
        # Setup default lighting
        self.lighting.register_light("living_room_main", "Living Room Main", "living_room", supports_color=True)
        self.lighting.register_light("bedroom_main", "Bedroom Main", "bedroom")
        self.lighting.register_light("kitchen_main", "Kitchen Main", "kitchen")
        self.lighting.create_zone("main_floor", ["living_room_main", "kitchen_main"])
        
        # Setup security system
        self.security.register_sensor("front_door", "door", "front_entrance")
        self.security.register_sensor("living_room_motion", "motion", "living_room")
        self.security.register_camera("front_camera", "front_entrance")
        self.security.register_lock("front_lock", "front_door")
        
        # Setup climate control
        self.climate.register_thermostat("main_thermostat", "living_room")
        self.climate.register_sensor("temp_sensor_lr", "living_room", "temperature")
        
        # Setup entertainment
        self.entertainment.register_tv("living_room_tv", "living_room", "Samsung")
        self.entertainment.register_speaker("living_room_speaker", "living_room")
        self.entertainment.register_streaming_service("Netflix", {"username": "user", "password": "pass"})
        
        # Setup energy management
        self.energy.register_smart_outlet("living_room_outlet1", "living_room")
        self.energy.register_smart_outlet("bedroom_outlet1", "bedroom")
        self.energy.register_solar_panel("roof_panel1", 300)  # 300W panel
        
        self.is_initialized = True
        logging.info("Smart home system initialized with default configuration")
    
    # High-level Scene Control Methods
    def activate_scene(self, scene: SceneType) -> bool:
        """Activate a predefined scene that controls multiple subsystems."""
        if not self.is_initialized:
            return False
        
        self.current_scene = scene
        logging.info(f"Activating scene: {scene.value}")
        
        if scene == SceneType.MORNING:
            return self._morning_scene()
        elif scene == SceneType.WORK:
            return self._work_scene()
        elif scene == SceneType.EVENING:
            return self._evening_scene()
        elif scene == SceneType.NIGHT:
            return self._night_scene()
        elif scene == SceneType.PARTY:
            return self._party_scene()
        elif scene == SceneType.MOVIE:
            return self._movie_scene()
        elif scene == SceneType.VACATION:
            return self._vacation_scene()
        
        return False
    
    def _morning_scene(self) -> bool:
        """Morning routine scene."""
        # Gradually increase lighting
        self.lighting.control_zone("main_floor", True, 60)
        
        # Set comfortable temperature
        self.climate.set_temperature("main_thermostat", 22.0, ClimateMode.AUTO)
        
        # Security to home mode
        self.security.set_security_level(SecurityLevel.HOME)
        
        # Turn on morning news
        self.entertainment.power_on_device("living_room_tv")
        self.entertainment.play_content("living_room_tv", "channel", "news")
        
        logging.info("Morning scene activated: lighting on, comfortable temperature, news playing")
        return True
    
    def _work_scene(self) -> bool:
        """Work from home scene."""
        # Bright, focused lighting
        self.lighting.turn_on_light("living_room_main", 90)
        
        # Optimal work temperature
        self.climate.set_temperature("main_thermostat", 21.0, ClimateMode.AUTO)
        
        # Security monitoring
        self.security.set_security_level(SecurityLevel.HOME)
        
        # Background music
        self.entertainment.power_on_device("living_room_speaker")
        self.entertainment.play_content("living_room_speaker", "playlist", "focus_music")
        self.entertainment.set_volume("living_room_speaker", 30)
        
        logging.info("Work scene activated: bright lighting, optimal temperature, focus music")
        return True
    
    def _evening_scene(self) -> bool:
        """Evening relaxation scene."""
        # Warm, dim lighting
        self.lighting.control_zone("main_floor", True, 40)
        self.lighting.set_color("living_room_main", (255, 200, 100))  # Warm white
        
        # Comfortable evening temperature
        self.climate.set_temperature("main_thermostat", 23.0, ClimateMode.AUTO)
        
        # Home security mode
        self.security.set_security_level(SecurityLevel.HOME)
        
        # Entertainment ready
        self.entertainment.power_on_device("living_room_tv")
        self.entertainment.set_volume("living_room_tv", 40)
        
        logging.info("Evening scene activated: warm lighting, comfortable temperature, entertainment ready")
        return True
    
    def _night_scene(self) -> bool:
        """Night time scene."""
        # Turn off most lights, keep minimal lighting
        self.lighting.control_zone("main_floor", False)
        self.lighting.turn_on_light("bedroom_main", 10)  # Night light
        
        # Lower temperature for sleep
        self.climate.set_temperature("main_thermostat", 19.0, ClimateMode.AUTO)
        
        # Full security mode
        self.security.set_security_level(SecurityLevel.AWAY)
        
        # Turn off entertainment
        self.entertainment.power_on_device("living_room_tv")  # Turn off
        
        # Energy saving mode
        self.energy.control_outlet("living_room_outlet1", False)
        
        logging.info("Night scene activated: minimal lighting, cool temperature, full security, energy saving")
        return True
    
    def _party_scene(self) -> bool:
        """Party scene."""
        # Bright, colorful lighting
        self.lighting.control_zone("main_floor", True, 80)
        self.lighting.set_color("living_room_main", (255, 0, 255))  # Party colors
        
        # Comfortable party temperature
        self.climate.set_temperature("main_thermostat", 20.0, ClimateMode.COOL)
        
        # Home security (guests present)
        self.security.set_security_level(SecurityLevel.HOME)
        
        # Party music throughout the house
        speakers = ["living_room_speaker"]
        self.entertainment.create_multiroom_session(speakers, "party_playlist")
        self.entertainment.set_volume("living_room_speaker", 70)
        
        logging.info("Party scene activated: bright colorful lighting, cool temperature, party music")
        return True
    
    def _movie_scene(self) -> bool:
        """Movie watching scene."""
        # Dim lighting for movie watching
        self.lighting.control_zone("main_floor", True, 20)
        
        # Comfortable temperature
        self.climate.set_temperature("main_thermostat", 22.0, ClimateMode.AUTO)
        
        # Home security
        self.security.set_security_level(SecurityLevel.HOME)
        
        # Optimize entertainment system
        self.entertainment.power_on_device("living_room_tv")
        self.entertainment.set_volume("living_room_tv", 60)
        self.entertainment.play_content("living_room_tv", "app", "Netflix")
        
        logging.info("Movie scene activated: dim lighting, optimized entertainment system")
        return True
    
    def _vacation_scene(self) -> bool:
        """Vacation/away scene."""
        # Random lighting patterns to simulate presence
        self.lighting.turn_on_light("living_room_main", 50)
        
        # Energy saving temperature
        self.climate.set_temperature("main_thermostat", 18.0, ClimateMode.ECO)
        
        # Maximum security
        self.security.set_security_level(SecurityLevel.VACATION)
        
        # Turn off non-essential devices
        self.energy.control_outlet("living_room_outlet1", False)
        self.energy.control_outlet("bedroom_outlet1", False)
        
        logging.info("Vacation scene activated: security mode, energy saving, presence simulation")
        return True
    
    # Simplified Control Methods
    def turn_on_lights(self, location: str = "all", brightness: int = 70) -> bool:
        """Simple method to turn on lights."""
        if location == "all":
            return self.lighting.control_zone("main_floor", True, brightness)
        else:
            # Find light by location
            for light_id, light_info in self.lighting.lights.items():
                if light_info["location"] == location:
                    return self.lighting.turn_on_light(light_id, brightness)
        return False
    
    def turn_off_lights(self, location: str = "all") -> bool:
        """Simple method to turn off lights."""
        if location == "all":
            return self.lighting.control_zone("main_floor", False)
        else:
            for light_id, light_info in self.lighting.lights.items():
                if light_info["location"] == location:
                    return self.lighting.turn_off_light(light_id)
        return False
    
    def set_temperature(self, temperature: float) -> bool:
        """Simple method to set house temperature."""
        return self.climate.set_temperature("main_thermostat", temperature)
    
    def arm_security(self, level: str = "away") -> bool:
        """Simple method to arm security system."""
        level_map = {
            "disarm": SecurityLevel.DISARMED,
            "home": SecurityLevel.HOME,
            "away": SecurityLevel.AWAY,
            "vacation": SecurityLevel.VACATION
        }
        
        if level in level_map:
            return self.security.set_security_level(level_map[level])
        return False
    
    def play_music(self, location: str = "living_room", volume: int = 50) -> bool:
        """Simple method to play music."""
        speaker_id = f"{location}_speaker"
        
        if self.entertainment.power_on_device(speaker_id):
            self.entertainment.set_volume(speaker_id, volume)
            return self.entertainment.play_content(speaker_id, "playlist", "default")
        return False
    
    def watch_tv(self, location: str = "living_room", volume: int = 40) -> bool:
        """Simple method to start watching TV."""
        tv_id = f"{location}_tv"
        
        if self.entertainment.power_on_device(tv_id):
            self.entertainment.set_volume(tv_id, volume)
            return True
        return False
    
    # Status and Monitoring Methods
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "current_scene": self.current_scene.value if self.current_scene else None,
            "lighting": {
                "lights_on": sum(1 for light in self.lighting.lights.values() if light["is_on"]),
                "total_lights": len(self.lighting.lights),
                "energy_usage": self.lighting.get_total_energy_usage()
            },
            "security": self.security.get_system_status(),
            "climate": {
                "average_temperature": self.climate.get_average_temperature(),
                "energy_usage": self.climate.get_total_energy_usage()
            },
            "energy": self.energy.get_energy_balance(),
            "entertainment": {
                "devices_on": sum(1 for device in self.entertainment.devices.values() if device["is_on"]),
                "speakers_on": sum(1 for speaker in self.entertainment.speakers.values() if speaker["is_on"])
            }
        }
    
    def get_energy_report(self) -> Dict[str, float]:
        """Get energy consumption report."""
        lighting_usage = self.lighting.get_total_energy_usage()
        climate_usage = self.climate.get_total_energy_usage()
        outlet_usage = self.energy.get_total_consumption()
        solar_generation = self.energy.get_total_generation()
        
        total_consumption = lighting_usage + climate_usage + outlet_usage
        
        return {
            "lighting_watts": lighting_usage,
            "climate_watts": climate_usage,
            "outlets_watts": outlet_usage,
            "total_consumption_watts": total_consumption,
            "solar_generation_watts": solar_generation,
            "net_usage_watts": total_consumption - solar_generation,
            "energy_efficiency_percent": (solar_generation / total_consumption * 100) if total_consumption > 0 else 0
        }
    
    def emergency_mode(self) -> bool:
        """Activate emergency mode - override all systems for safety."""
        logging.warning("EMERGENCY MODE ACTIVATED")
        
        # Turn on all lights to maximum
        self.lighting.control_zone("main_floor", True, 100)
        
        # Disarm security to allow emergency access
        self.security.set_security_level(SecurityLevel.DISARMED)
        
        # Set comfortable temperature
        self.climate.set_temperature("main_thermostat", 22.0, ClimateMode.AUTO)
        
        # Turn off all entertainment to reduce power load
        for device_id in self.entertainment.devices.keys():
            self.entertainment.power_on_device(device_id)  # Turn off
        
        return True


# Demonstration Function
def demonstrate_facade_pattern():
    """Demonstrate the Facade pattern with smart home automation."""
    
    print("=== Smart Home Automation - Facade Pattern Demo ===\n")
    
    # Create the smart home facade
    smart_home = SmartHomeFacade()
    
    # Demonstrate simple high-level operations
    print("1. Simple High-Level Operations:")
    print("-" * 40)
    
    # Basic controls using simplified interface
    smart_home.turn_on_lights("all", 60)
    smart_home.set_temperature(22.5)
    smart_home.arm_security("home")
    smart_home.play_music("living_room", 40)
    smart_home.watch_tv("living_room", 35)
    
    print()
    
    # Show system status
    status = smart_home.get_system_status()
    print("System Status After Basic Setup:")
    print(f"  Lights on: {status['lighting']['lights_on']}/{status['lighting']['total_lights']}")
    print(f"  Security level: {status['security']['security_level']}")
    print(f"  Average temperature: {status['climate']['average_temperature']:.1f}°C")
    print(f"  Entertainment devices on: {status['entertainment']['devices_on']}")
    print()
    
    # Demonstrate scene activation
    print("2. Scene-Based Automation:")
    print("-" * 35)
    
    scenes_to_demo = [
        SceneType.MORNING,
        SceneType.WORK,
        SceneType.EVENING,
        SceneType.MOVIE,
        SceneType.NIGHT
    ]
    
    for scene in scenes_to_demo:
        print(f"\nActivating {scene.value.upper()} scene:")
        smart_home.activate_scene(scene)
        
        # Show relevant status for each scene
        status = smart_home.get_system_status()
        print(f"  Security: {status['security']['security_level']}")
        print(f"  Lights: {status['lighting']['lights_on']} on")
        print(f"  Temperature: {status['climate']['average_temperature']:.1f}°C")
        
        if scene == SceneType.MOVIE:
            print("  Entertainment: TV optimized for movie watching")
        elif scene == SceneType.WORK:
            print("  Entertainment: Background music playing")
    
    print()
    
    # Demonstrate energy management
    print("3. Energy Management:")
    print("-" * 25)
    
    # Activate different scenes to show energy impact
    smart_home.activate_scene(SceneType.PARTY)
    energy_party = smart_home.get_energy_report()
    
    smart_home.activate_scene(SceneType.NIGHT)
    energy_night = smart_home.get_energy_report()
    
    print("Energy Usage Comparison:")
    print(f"Party Scene:")
    print(f"  Total consumption: {energy_party['total_consumption_watts']:.1f}W")
    print(f"  Solar generation: {energy_party['solar_generation_watts']:.1f}W")
    print(f"  Net usage: {energy_party['net_usage_watts']:.1f}W")
    
    print(f"Night Scene:")
    print(f"  Total consumption: {energy_night['total_consumption_watts']:.1f}W")
    print(f"  Solar generation: {energy_night['solar_generation_watts']:.1f}W")
    print(f"  Net usage: {energy_night['net_usage_watts']:.1f}W")
    
    savings = energy_party['total_consumption_watts'] - energy_night['total_consumption_watts']
    print(f"Energy savings (Night vs Party): {savings:.1f}W")
    print()
    
    # Demonstrate complex operations made simple
    print("4. Complex Operations Made Simple:")
    print("-" * 40)
    
    # What would normally require multiple subsystem calls
    print("Traditional approach would require:")
    print("  - 5+ calls to lighting subsystem")
    print("  - 3+ calls to security subsystem")
    print("  - 2+ calls to climate subsystem")
    print("  - 4+ calls to entertainment subsystem")
    print("  - 2+ calls to energy subsystem")
    print("  Total: 16+ individual subsystem calls")
    print()
    
    print("With Facade pattern:")
    print("  smart_home.activate_scene(SceneType.EVENING)")
    print("  Total: 1 simple call")
    print()
    
    # Emergency demonstration
    print("5. Emergency Mode:")
    print("-" * 20)
    
    print("Activating emergency mode...")
    smart_home.emergency_mode()
    
    status = smart_home.get_system_status()
    print("Emergency mode status:")
    print(f"  All lights: ON at maximum brightness")
    print(f"  Security: {status['security']['security_level']} (emergency access)")
    print(f"  Climate: Stable temperature maintained")
    print(f"  Entertainment: Powered down to reduce load")
    print()
    
    # Show the complexity hidden by facade
    print("6. Complexity Hidden by Facade:")
    print("-" * 40)
    
    print("Subsystems managed:")
    print(f"  Lighting: {len(smart_home.lighting.lights)} lights, {len(smart_home.lighting.zones)} zones")
    print(f"  Security: {len(smart_home.security.sensors)} sensors, {len(smart_home.security.cameras)} cameras")
    print(f"  Climate: {len(smart_home.climate.thermostats)} thermostats, {len(smart_home.climate.sensors)} sensors")
    print(f"  Entertainment: {len(smart_home.entertainment.devices)} devices, {len(smart_home.entertainment.speakers)} speakers")
    print(f"  Energy: {len(smart_home.energy.smart_outlets)} outlets, {len(smart_home.energy.solar_panels)} solar panels")
    print()
    
    print("=== Facade Pattern Benefits Demonstrated ===")
    print("✓ Simplified interface to complex subsystems")
    print("✓ Single point of control for multiple systems")
    print("✓ High-level operations (scenes) hide complexity")
    print("✓ Easy to use for end users")
    print("✓ Subsystem independence maintained")
    print("✓ Coordination between subsystems simplified")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the demonstration
    demonstrate_facade_pattern()