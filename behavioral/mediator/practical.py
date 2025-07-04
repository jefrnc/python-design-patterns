"""
Mediator Design Pattern - Real World Implementation

Real-world example: Air Traffic Control System
A comprehensive air traffic control system that manages communication between
aircraft, control towers, runways, and ground services through a central mediator.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import time
import random


class AircraftType(Enum):
    """Types of aircraft."""
    COMMERCIAL = "commercial"
    CARGO = "cargo"
    PRIVATE = "private"
    EMERGENCY = "emergency"
    MILITARY = "military"


class FlightStatus(Enum):
    """Flight status enumeration."""
    SCHEDULED = "scheduled"
    APPROACHING = "approaching"
    IN_HOLDING = "in_holding"
    CLEARED_TO_LAND = "cleared_to_land"
    LANDING = "landing"
    LANDED = "landed"
    TAXIING = "taxiing"
    AT_GATE = "at_gate"
    DEPARTING = "departing"
    AIRBORNE = "airborne"
    EMERGENCY = "emergency"


class Priority(Enum):
    """Priority levels for aircraft."""
    EMERGENCY = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class WeatherCondition(Enum):
    """Weather conditions."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    FOGGY = "foggy"
    STORMY = "stormy"


class ATCMediator(ABC):
    """
    Abstract mediator interface for Air Traffic Control operations.
    """
    
    @abstractmethod
    def register_aircraft(self, aircraft: 'Aircraft') -> None:
        pass
    
    @abstractmethod
    def register_runway(self, runway: 'Runway') -> None:
        pass
    
    @abstractmethod
    def register_controller(self, controller: 'AirTrafficController') -> None:
        pass
    
    @abstractmethod
    def request_landing(self, aircraft: 'Aircraft') -> str:
        pass
    
    @abstractmethod
    def request_takeoff(self, aircraft: 'Aircraft') -> str:
        pass
    
    @abstractmethod
    def report_emergency(self, aircraft: 'Aircraft', emergency_type: str) -> str:
        pass
    
    @abstractmethod
    def update_weather(self, condition: WeatherCondition, visibility: int) -> None:
        pass
    
    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        pass


class Aircraft:
    """Aircraft that communicates through the ATC mediator."""
    
    def __init__(self, call_sign: str, aircraft_type: AircraftType, 
                 origin: str, destination: str):
        self.call_sign = call_sign
        self.aircraft_type = aircraft_type
        self.origin = origin
        self.destination = destination
        self.status = FlightStatus.SCHEDULED
        self.priority = Priority.NORMAL
        self.fuel_level = 100  # Percentage
        self.altitude = 0
        self.position = {"x": 0, "y": 0}
        self.mediator: Optional[ATCMediator] = None
        self.assigned_runway: Optional['Runway'] = None
        self.estimated_arrival = datetime.now() + timedelta(hours=random.randint(1, 8))
        self.passengers = random.randint(50, 300) if aircraft_type == AircraftType.COMMERCIAL else 0
        self.cargo_weight = random.randint(1000, 50000) if aircraft_type == AircraftType.CARGO else 0
    
    def set_mediator(self, mediator: ATCMediator) -> None:
        self.mediator = mediator
    
    def request_landing_clearance(self) -> str:
        if not self.mediator:
            return "No ATC mediator assigned"
        
        self.status = FlightStatus.APPROACHING
        print(f"✈️  {self.call_sign}: Requesting landing clearance")
        response = self.mediator.request_landing(self)
        return response
    
    def request_takeoff_clearance(self) -> str:
        if not self.mediator:
            return "No ATC mediator assigned"
        
        self.status = FlightStatus.DEPARTING
        print(f"🛫 {self.call_sign}: Requesting takeoff clearance")
        response = self.mediator.request_takeoff(self)
        return response
    
    def declare_emergency(self, emergency_type: str) -> str:
        if not self.mediator:
            return "No ATC mediator assigned"
        
        self.status = FlightStatus.EMERGENCY
        self.priority = Priority.EMERGENCY
        print(f"🚨 {self.call_sign}: EMERGENCY - {emergency_type}")
        response = self.mediator.report_emergency(self, emergency_type)
        return response
    
    def update_position(self, x: int, y: int, altitude: int) -> None:
        self.position = {"x": x, "y": y}
        self.altitude = altitude
    
    def consume_fuel(self, amount: float) -> None:
        self.fuel_level = max(0, self.fuel_level - amount)
        if self.fuel_level <= 20 and self.status != FlightStatus.EMERGENCY:
            self.declare_emergency("Low fuel")
    
    def land(self, runway: 'Runway') -> str:
        self.status = FlightStatus.LANDING
        self.assigned_runway = runway
        self.altitude = 0
        result = f"{self.call_sign} landing on {runway.runway_id}"
        print(f"🛬 {result}")
        
        # Simulate landing time
        time.sleep(0.1)
        
        self.status = FlightStatus.LANDED
        return f"{self.call_sign} has landed safely on {runway.runway_id}"
    
    def takeoff(self, runway: 'Runway') -> str:
        self.status = FlightStatus.DEPARTING
        self.assigned_runway = runway
        result = f"{self.call_sign} taking off from {runway.runway_id}"
        print(f"🚀 {result}")
        
        # Simulate takeoff time
        time.sleep(0.1)
        
        self.status = FlightStatus.AIRBORNE
        self.altitude = 1000
        return f"{self.call_sign} is now airborne"
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "call_sign": self.call_sign,
            "type": self.aircraft_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "origin": self.origin,
            "destination": self.destination,
            "fuel_level": self.fuel_level,
            "altitude": self.altitude,
            "position": self.position,
            "assigned_runway": self.assigned_runway.runway_id if self.assigned_runway else None,
            "estimated_arrival": self.estimated_arrival.isoformat(),
            "passengers": self.passengers,
            "cargo_weight": self.cargo_weight
        }


class Runway:
    """Airport runway managed by ATC."""
    
    def __init__(self, runway_id: str, length: int, width: int):
        self.runway_id = runway_id
        self.length = length  # meters
        self.width = width    # meters
        self.is_occupied = False
        self.is_operational = True
        self.current_aircraft: Optional[Aircraft] = None
        self.scheduled_landings: List[Aircraft] = []
        self.scheduled_takeoffs: List[Aircraft] = []
        self.maintenance_until: Optional[datetime] = None
    
    def is_available(self) -> bool:
        if self.maintenance_until and datetime.now() < self.maintenance_until:
            return False
        return self.is_operational and not self.is_occupied
    
    def occupy(self, aircraft: Aircraft) -> bool:
        if not self.is_available():
            return False
        
        self.is_occupied = True
        self.current_aircraft = aircraft
        return True
    
    def release(self) -> Optional[Aircraft]:
        released_aircraft = self.current_aircraft
        self.is_occupied = False
        self.current_aircraft = None
        return released_aircraft
    
    def schedule_landing(self, aircraft: Aircraft) -> None:
        if aircraft not in self.scheduled_landings:
            self.scheduled_landings.append(aircraft)
    
    def schedule_takeoff(self, aircraft: Aircraft) -> None:
        if aircraft not in self.scheduled_takeoffs:
            self.scheduled_takeoffs.append(aircraft)
    
    def set_maintenance(self, duration_hours: int) -> None:
        self.maintenance_until = datetime.now() + timedelta(hours=duration_hours)
        self.is_operational = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "runway_id": self.runway_id,
            "length": self.length,
            "width": self.width,
            "is_available": self.is_available(),
            "is_occupied": self.is_occupied,
            "current_aircraft": self.current_aircraft.call_sign if self.current_aircraft else None,
            "scheduled_landings": len(self.scheduled_landings),
            "scheduled_takeoffs": len(self.scheduled_takeoffs),
            "maintenance_until": self.maintenance_until.isoformat() if self.maintenance_until else None
        }


class AirTrafficController:
    """Air traffic controller working with the ATC system."""
    
    def __init__(self, controller_id: str, name: str, shift_hours: tuple):
        self.controller_id = controller_id
        self.name = name
        self.shift_start, self.shift_end = shift_hours
        self.is_on_duty = True
        self.handled_operations = 0
        self.emergency_responses = 0
        self.mediator: Optional[ATCMediator] = None
    
    def set_mediator(self, mediator: ATCMediator) -> None:
        self.mediator = mediator
    
    def is_available(self) -> bool:
        current_hour = datetime.now().hour
        return (self.is_on_duty and 
                self.shift_start <= current_hour <= self.shift_end)
    
    def handle_operation(self, operation_type: str, aircraft: Aircraft) -> str:
        if not self.is_available():
            return f"Controller {self.name} is not available"
        
        self.handled_operations += 1
        
        if operation_type == "emergency":
            self.emergency_responses += 1
            return f"Controller {self.name} handling emergency for {aircraft.call_sign}"
        
        return f"Controller {self.name} handling {operation_type} for {aircraft.call_sign}"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "name": self.name,
            "is_on_duty": self.is_on_duty,
            "is_available": self.is_available(),
            "operations_handled": self.handled_operations,
            "emergency_responses": self.emergency_responses,
            "shift_hours": f"{self.shift_start}:00-{self.shift_end}:00"
        }


class GroundServices:
    """Ground services for aircraft maintenance and support."""
    
    def __init__(self):
        self.refueling_crew = {"available": 3, "busy": 0}
        self.maintenance_crew = {"available": 2, "busy": 0}
        self.catering_crew = {"available": 4, "busy": 0}
        self.cleaning_crew = {"available": 3, "busy": 0}
        self.services_queue: List[Dict[str, Any]] = []
    
    def request_service(self, aircraft: Aircraft, service_type: str) -> str:
        service_request = {
            "aircraft": aircraft,
            "service_type": service_type,
            "requested_at": datetime.now(),
            "status": "pending"
        }
        
        self.services_queue.append(service_request)
        return f"Service {service_type} requested for {aircraft.call_sign}"
    
    def process_services(self) -> List[str]:
        results = []
        for service in self.services_queue[:]:
            if service["status"] == "pending":
                crew_type = f"{service['service_type']}_crew"
                if crew_type in self.__dict__ and self.__dict__[crew_type]["available"] > 0:
                    # Assign crew
                    self.__dict__[crew_type]["available"] -= 1
                    self.__dict__[crew_type]["busy"] += 1
                    
                    service["status"] = "in_progress"
                    results.append(f"Started {service['service_type']} for {service['aircraft'].call_sign}")
                    
                    # Simulate service completion (in real system this would be async)
                    if random.random() > 0.7:  # 30% chance to complete immediately
                        self.complete_service(service)
                        results.append(f"Completed {service['service_type']} for {service['aircraft'].call_sign}")
        
        return results
    
    def complete_service(self, service: Dict[str, Any]) -> None:
        crew_type = f"{service['service_type']}_crew"
        if crew_type in self.__dict__:
            self.__dict__[crew_type]["available"] += 1
            self.__dict__[crew_type]["busy"] -= 1
        
        service["status"] = "completed"
        if service in self.services_queue:
            self.services_queue.remove(service)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "refueling_crew": self.refueling_crew,
            "maintenance_crew": self.maintenance_crew,
            "catering_crew": self.catering_crew,
            "cleaning_crew": self.cleaning_crew,
            "pending_services": len([s for s in self.services_queue if s["status"] == "pending"]),
            "in_progress_services": len([s for s in self.services_queue if s["status"] == "in_progress"])
        }


class AirportATCSystem(ATCMediator):
    """
    Concrete mediator implementing the Air Traffic Control system.
    """
    
    def __init__(self, airport_code: str, airport_name: str):
        self.airport_code = airport_code
        self.airport_name = airport_name
        
        # Components
        self.aircraft: List[Aircraft] = []
        self.runways: List[Runway] = []
        self.controllers: List[AirTrafficController] = []
        self.ground_services = GroundServices()
        
        # State
        self.weather_condition = WeatherCondition.CLEAR
        self.visibility = 100  # percentage
        self.operations_count = 0
        self.emergency_count = 0
        self.landing_queue: List[Aircraft] = []
        self.takeoff_queue: List[Aircraft] = []
        
        # Logs
        self.operation_log: List[Dict[str, Any]] = []
    
    def register_aircraft(self, aircraft: Aircraft) -> None:
        aircraft.set_mediator(self)
        self.aircraft.append(aircraft)
        self.log_operation("aircraft_registered", aircraft.call_sign, 
                          f"Registered {aircraft.aircraft_type.value} aircraft")
    
    def register_runway(self, runway: Runway) -> None:
        self.runways.append(runway)
        self.log_operation("runway_registered", runway.runway_id, 
                          f"Registered runway {runway.length}m x {runway.width}m")
    
    def register_controller(self, controller: AirTrafficController) -> None:
        controller.set_mediator(self)
        self.controllers.append(controller)
        self.log_operation("controller_registered", controller.controller_id, 
                          f"Registered controller {controller.name}")
    
    def request_landing(self, aircraft: Aircraft) -> str:
        self.operations_count += 1
        
        # Check weather conditions
        if not self._is_weather_suitable_for_landing():
            message = f"Landing denied for {aircraft.call_sign} due to poor weather conditions"
            self.log_operation("landing_denied", aircraft.call_sign, message)
            return message
        
        # Handle emergency aircraft with priority
        if aircraft.priority == Priority.EMERGENCY:
            return self._handle_emergency_landing(aircraft)
        
        # Find available runway
        available_runway = self._find_available_runway_for_landing()
        
        if not available_runway:
            # Add to landing queue
            if aircraft not in self.landing_queue:
                self.landing_queue.append(aircraft)
            aircraft.status = FlightStatus.IN_HOLDING
            message = f"{aircraft.call_sign} added to landing queue (position {len(self.landing_queue)})"
            self.log_operation("landing_queued", aircraft.call_sign, message)
            return message
        
        # Assign runway and clear for landing
        return self._clear_aircraft_for_landing(aircraft, available_runway)
    
    def request_takeoff(self, aircraft: Aircraft) -> str:
        self.operations_count += 1
        
        # Check weather conditions
        if not self._is_weather_suitable_for_takeoff():
            message = f"Takeoff denied for {aircraft.call_sign} due to poor weather conditions"
            self.log_operation("takeoff_denied", aircraft.call_sign, message)
            return message
        
        # Find available runway
        available_runway = self._find_available_runway_for_takeoff()
        
        if not available_runway:
            # Add to takeoff queue
            if aircraft not in self.takeoff_queue:
                self.takeoff_queue.append(aircraft)
            message = f"{aircraft.call_sign} added to takeoff queue (position {len(self.takeoff_queue)})"
            self.log_operation("takeoff_queued", aircraft.call_sign, message)
            return message
        
        # Clear for takeoff
        return self._clear_aircraft_for_takeoff(aircraft, available_runway)
    
    def report_emergency(self, aircraft: Aircraft, emergency_type: str) -> str:
        self.emergency_count += 1
        aircraft.priority = Priority.EMERGENCY
        
        # Alert all controllers
        available_controller = self._get_available_controller()
        if available_controller:
            controller_response = available_controller.handle_operation("emergency", aircraft)
        else:
            controller_response = "No controllers available for emergency"
        
        # Clear runway immediately if needed
        if emergency_type.lower() in ["engine failure", "medical emergency", "fuel emergency"]:
            emergency_runway = self._clear_runway_for_emergency(aircraft)
            if emergency_runway:
                message = f"EMERGENCY: {aircraft.call_sign} cleared for immediate landing on {emergency_runway.runway_id}"
                aircraft.status = FlightStatus.CLEARED_TO_LAND
                aircraft.assigned_runway = emergency_runway
                emergency_runway.occupy(aircraft)
            else:
                message = f"EMERGENCY: No runway immediately available for {aircraft.call_sign}"
        else:
            message = f"EMERGENCY ACKNOWLEDGED: {aircraft.call_sign} - {emergency_type}"
        
        # Request emergency ground services
        self.ground_services.request_service(aircraft, "emergency_response")
        
        self.log_operation("emergency", aircraft.call_sign, 
                          f"{emergency_type} - {controller_response}")
        
        print(f"🚨 EMERGENCY RESPONSE: {message}")
        return message
    
    def update_weather(self, condition: WeatherCondition, visibility: int) -> None:
        old_condition = self.weather_condition
        self.weather_condition = condition
        self.visibility = visibility
        
        message = f"Weather updated: {condition.value}, visibility {visibility}%"
        self.log_operation("weather_update", "SYSTEM", message)
        
        # If weather improved, process queues
        if (old_condition in [WeatherCondition.STORMY, WeatherCondition.FOGGY] and 
            condition in [WeatherCondition.CLEAR, WeatherCondition.CLOUDY]):
            self._process_queues_after_weather_improvement()
    
    def _handle_emergency_landing(self, aircraft: Aircraft) -> str:
        # Emergency aircraft get immediate priority
        emergency_runway = self._clear_runway_for_emergency(aircraft)
        
        if emergency_runway:
            aircraft.status = FlightStatus.CLEARED_TO_LAND
            aircraft.assigned_runway = emergency_runway
            emergency_runway.occupy(aircraft)
            
            message = f"EMERGENCY LANDING CLEARANCE: {aircraft.call_sign} cleared for immediate landing on {emergency_runway.runway_id}"
            self.log_operation("emergency_landing_cleared", aircraft.call_sign, message)
            
            # Automatically process landing
            aircraft.land(emergency_runway)
            emergency_runway.release()
            
            return message
        else:
            message = f"EMERGENCY: No runway available for immediate landing - {aircraft.call_sign} priority queued"
            if aircraft not in self.landing_queue:
                self.landing_queue.insert(0, aircraft)  # Add to front of queue
            return message
    
    def _clear_runway_for_emergency(self, aircraft: Aircraft) -> Optional[Runway]:
        # First try to find empty runway
        for runway in self.runways:
            if runway.is_available():
                return runway
        
        # If no empty runway, clear one with lowest priority aircraft
        for runway in self.runways:
            if (runway.current_aircraft and 
                runway.current_aircraft.priority.value > aircraft.priority.value):
                # Move current aircraft to queue
                displaced_aircraft = runway.current_aircraft
                displaced_aircraft.status = FlightStatus.IN_HOLDING
                self.landing_queue.insert(0, displaced_aircraft)
                runway.release()
                
                self.log_operation("runway_cleared", runway.runway_id, 
                                 f"Cleared for emergency - {displaced_aircraft.call_sign} moved to queue")
                return runway
        
        return None
    
    def _find_available_runway_for_landing(self) -> Optional[Runway]:
        # Prefer longer runways for landing
        sorted_runways = sorted([r for r in self.runways if r.is_available()], 
                               key=lambda x: x.length, reverse=True)
        return sorted_runways[0] if sorted_runways else None
    
    def _find_available_runway_for_takeoff(self) -> Optional[Runway]:
        # Any available runway can be used for takeoff
        available_runways = [r for r in self.runways if r.is_available()]
        return available_runways[0] if available_runways else None
    
    def _clear_aircraft_for_landing(self, aircraft: Aircraft, runway: Runway) -> str:
        aircraft.status = FlightStatus.CLEARED_TO_LAND
        aircraft.assigned_runway = runway
        runway.occupy(aircraft)
        
        # Assign controller
        controller = self._get_available_controller()
        if controller:
            controller.handle_operation("landing", aircraft)
        
        message = f"{aircraft.call_sign} cleared for landing on runway {runway.runway_id}"
        self.log_operation("landing_cleared", aircraft.call_sign, message)
        
        # Simulate landing process
        aircraft.land(runway)
        runway.release()
        
        # Request ground services
        if aircraft.aircraft_type == AircraftType.COMMERCIAL:
            self.ground_services.request_service(aircraft, "refueling")
            self.ground_services.request_service(aircraft, "catering")
            self.ground_services.request_service(aircraft, "cleaning")
        
        return message
    
    def _clear_aircraft_for_takeoff(self, aircraft: Aircraft, runway: Runway) -> str:
        aircraft.status = FlightStatus.CLEARED_TO_LAND  # Cleared for takeoff
        aircraft.assigned_runway = runway
        runway.occupy(aircraft)
        
        # Assign controller
        controller = self._get_available_controller()
        if controller:
            controller.handle_operation("takeoff", aircraft)
        
        message = f"{aircraft.call_sign} cleared for takeoff on runway {runway.runway_id}"
        self.log_operation("takeoff_cleared", aircraft.call_sign, message)
        
        # Simulate takeoff process
        aircraft.takeoff(runway)
        runway.release()
        
        return message
    
    def _get_available_controller(self) -> Optional[AirTrafficController]:
        available_controllers = [c for c in self.controllers if c.is_available()]
        return available_controllers[0] if available_controllers else None
    
    def _is_weather_suitable_for_landing(self) -> bool:
        if self.weather_condition == WeatherCondition.STORMY:
            return False
        if self.weather_condition == WeatherCondition.FOGGY and self.visibility < 30:
            return False
        return True
    
    def _is_weather_suitable_for_takeoff(self) -> bool:
        if self.weather_condition == WeatherCondition.STORMY:
            return False
        if self.weather_condition == WeatherCondition.FOGGY and self.visibility < 50:
            return False
        return True
    
    def _process_queues_after_weather_improvement(self) -> None:
        print("🌤️  Weather improved - processing queued aircraft")
        
        # Process landing queue
        for aircraft in self.landing_queue[:]:
            runway = self._find_available_runway_for_landing()
            if runway:
                self.landing_queue.remove(aircraft)
                self._clear_aircraft_for_landing(aircraft, runway)
            else:
                break  # No more runways available
        
        # Process takeoff queue
        for aircraft in self.takeoff_queue[:]:
            runway = self._find_available_runway_for_takeoff()
            if runway:
                self.takeoff_queue.remove(aircraft)
                self._clear_aircraft_for_takeoff(aircraft, runway)
            else:
                break  # No more runways available
    
    def log_operation(self, operation_type: str, subject: str, details: str) -> None:
        log_entry = {
            "timestamp": datetime.now(),
            "operation_type": operation_type,
            "subject": subject,
            "details": details
        }
        self.operation_log.append(log_entry)
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "airport": {
                "code": self.airport_code,
                "name": self.airport_name
            },
            "weather": {
                "condition": self.weather_condition.value,
                "visibility": self.visibility
            },
            "aircraft": {
                "total": len(self.aircraft),
                "by_status": self._count_aircraft_by_status()
            },
            "runways": {
                "total": len(self.runways),
                "available": len([r for r in self.runways if r.is_available()]),
                "occupied": len([r for r in self.runways if r.is_occupied])
            },
            "controllers": {
                "total": len(self.controllers),
                "available": len([c for c in self.controllers if c.is_available()])
            },
            "queues": {
                "landing": len(self.landing_queue),
                "takeoff": len(self.takeoff_queue)
            },
            "operations": {
                "total": self.operations_count,
                "emergencies": self.emergency_count
            },
            "ground_services": self.ground_services.get_status()
        }
    
    def _count_aircraft_by_status(self) -> Dict[str, int]:
        status_counts = {}
        for aircraft in self.aircraft:
            status = aircraft.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def get_operation_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent operations log."""
        recent_logs = self.operation_log[-limit:]
        return [
            {
                "timestamp": log["timestamp"].strftime("%H:%M:%S"),
                "operation": log["operation_type"],
                "subject": log["subject"],
                "details": log["details"]
            }
            for log in recent_logs
        ]


def main():
    """
    Demonstrate the Air Traffic Control Mediator System.
    """
    print("=== Air Traffic Control Mediator System Demo ===")
    
    # Create ATC system
    atc_system = AirportATCSystem("JFK", "John F. Kennedy International Airport")
    
    # Register runways
    runway_09L = Runway("09L", 4423, 60)  # Main runway
    runway_09R = Runway("09R", 3460, 46)  # Secondary runway
    runway_04L = Runway("04L", 2560, 46)  # Short runway
    
    atc_system.register_runway(runway_09L)
    atc_system.register_runway(runway_09R)
    atc_system.register_runway(runway_04L)
    
    # Register controllers
    controller1 = AirTrafficController("ATC001", "John Smith", (6, 14))
    controller2 = AirTrafficController("ATC002", "Sarah Johnson", (14, 22))
    controller3 = AirTrafficController("ATC003", "Mike Brown", (22, 6))
    
    atc_system.register_controller(controller1)
    atc_system.register_controller(controller2)
    atc_system.register_controller(controller3)
    
    print(f"\n🏢 {atc_system.airport_name} ({atc_system.airport_code}) initialized")
    print(f"   Runways: {len(atc_system.runways)}")
    print(f"   Controllers: {len(atc_system.controllers)}")
    
    # Create aircraft
    aircraft_fleet = [
        Aircraft("AA123", AircraftType.COMMERCIAL, "LAX", "JFK"),
        Aircraft("UA456", AircraftType.COMMERCIAL, "ORD", "JFK"),
        Aircraft("DL789", AircraftType.COMMERCIAL, "ATL", "JFK"),
        Aircraft("FX101", AircraftType.CARGO, "MEM", "JFK"),
        Aircraft("N12345", AircraftType.PRIVATE, "TEB", "JFK"),
        Aircraft("SW202", AircraftType.COMMERCIAL, "LAS", "JFK")
    ]
    
    # Register aircraft
    for aircraft in aircraft_fleet:
        atc_system.register_aircraft(aircraft)
    
    print(f"\n✈️  Registered {len(aircraft_fleet)} aircraft")
    
    # Test 1: Normal landing operations
    print("\n🛬 Test 1: Normal Landing Operations")
    
    # Multiple aircraft requesting landing
    landing_responses = []
    for aircraft in aircraft_fleet[:4]:  # First 4 aircraft
        response = aircraft.request_landing_clearance()
        landing_responses.append(response)
    
    print("\nLanding responses:")
    for response in landing_responses:
        print(f"  {response}")
    
    # Test 2: Weather impact
    print("\n🌧️  Test 2: Weather Impact on Operations")
    
    # Set bad weather
    atc_system.update_weather(WeatherCondition.STORMY, 20)
    
    # Try landing in bad weather
    storm_aircraft = Aircraft("WX999", AircraftType.COMMERCIAL, "MIA", "JFK")
    atc_system.register_aircraft(storm_aircraft)
    
    bad_weather_response = storm_aircraft.request_landing_clearance()
    print(f"Bad weather response: {bad_weather_response}")
    
    # Improve weather
    print("\nImproving weather conditions...")
    atc_system.update_weather(WeatherCondition.CLEAR, 100)
    
    # Test 3: Emergency handling
    print("\n🚨 Test 3: Emergency Handling")
    
    # Create emergency aircraft
    emergency_aircraft = Aircraft("EMG001", AircraftType.COMMERCIAL, "BOS", "JFK")
    atc_system.register_aircraft(emergency_aircraft)
    
    # Declare emergency
    emergency_response = emergency_aircraft.declare_emergency("Engine failure")
    print(f"Emergency response: {emergency_response}")
    
    # Test 4: Takeoff operations
    print("\n🛫 Test 4: Takeoff Operations")
    
    # Create departing aircraft
    departing_aircraft = [
        Aircraft("AA555", AircraftType.COMMERCIAL, "JFK", "LAX"),
        Aircraft("UA666", AircraftType.COMMERCIAL, "JFK", "SFO"),
        Aircraft("N67890", AircraftType.PRIVATE, "JFK", "MIA")
    ]
    
    for aircraft in departing_aircraft:
        atc_system.register_aircraft(aircraft)
        response = aircraft.request_takeoff_clearance()
        print(f"  Takeoff response: {response}")
    
    # Test 5: Queue management
    print("\n📋 Test 5: Queue Management")
    
    # Create multiple aircraft to test queuing
    queue_aircraft = []
    for i in range(5):
        aircraft = Aircraft(f"QL{100+i}", AircraftType.COMMERCIAL, "LAX", "JFK")
        queue_aircraft.append(aircraft)
        atc_system.register_aircraft(aircraft)
    
    # All request landing (should create queue)
    print("Multiple aircraft requesting landing:")
    for aircraft in queue_aircraft:
        response = aircraft.request_landing_clearance()
        print(f"  {response}")
    
    # Test 6: Ground services
    print("\n🔧 Test 6: Ground Services")
    
    # Process some ground services
    service_results = atc_system.ground_services.process_services()
    if service_results:
        print("Ground services activity:")
        for result in service_results:
            print(f"  {result}")
    else:
        print("No ground services to process at the moment")
    
    # Display system status
    print("\n📊 System Status Report:")
    status = atc_system.get_system_status()
    
    print(f"Airport: {status['airport']['name']} ({status['airport']['code']})")
    print(f"Weather: {status['weather']['condition']} (visibility: {status['weather']['visibility']}%)")
    print(f"Aircraft: {status['aircraft']['total']} total")
    print(f"  Status breakdown: {status['aircraft']['by_status']}")
    print(f"Runways: {status['runways']['available']}/{status['runways']['total']} available")
    print(f"Controllers: {status['controllers']['available']}/{status['controllers']['total']} available")
    print(f"Queues: Landing={status['queues']['landing']}, Takeoff={status['queues']['takeoff']}")
    print(f"Operations: {status['operations']['total']} total, {status['operations']['emergencies']} emergencies")
    
    # Ground services status
    ground_status = status['ground_services']
    print(f"Ground Services:")
    print(f"  Refueling: {ground_status['refueling_crew']['available']} available, {ground_status['refueling_crew']['busy']} busy")
    print(f"  Maintenance: {ground_status['maintenance_crew']['available']} available, {ground_status['maintenance_crew']['busy']} busy")
    print(f"  Pending services: {ground_status['pending_services']}")
    
    # Display recent operations log
    print("\n📜 Recent Operations Log:")
    recent_ops = atc_system.get_operation_log(8)
    for op in recent_ops:
        print(f"  {op['timestamp']} - {op['operation']}: {op['subject']} - {op['details']}")
    
    # Test 7: Controller performance
    print("\n👨‍💼 Test 7: Controller Performance")
    
    print("Controller performance stats:")
    for controller in atc_system.controllers:
        stats = controller.get_performance_stats()
        print(f"  {stats['name']} ({stats['controller_id']}):")
        print(f"    Available: {stats['is_available']}")
        print(f"    Operations handled: {stats['operations_handled']}")
        print(f"    Emergency responses: {stats['emergency_responses']}")
        print(f"    Shift: {stats['shift_hours']}")
    
    # Test 8: Runway status details
    print("\n🛤️  Test 8: Runway Status Details")
    
    print("Runway status:")
    for runway in atc_system.runways:
        runway_status = runway.get_status()
        print(f"  Runway {runway_status['runway_id']}:")
        print(f"    Available: {runway_status['is_available']}")
        print(f"    Current aircraft: {runway_status['current_aircraft'] or 'None'}")
        print(f"    Scheduled landings: {runway_status['scheduled_landings']}")
        print(f"    Scheduled takeoffs: {runway_status['scheduled_takeoffs']}")
    
    # Final statistics
    print("\n📈 Final Statistics:")
    final_status = atc_system.get_system_status()
    print(f"  Total aircraft managed: {len(atc_system.aircraft)}")
    print(f"  Total operations processed: {final_status['operations']['total']}")
    print(f"  Emergency situations handled: {final_status['operations']['emergencies']}")
    print(f"  System efficiency: {((final_status['operations']['total'] - final_status['operations']['emergencies']) / final_status['operations']['total'] * 100):.1f}%")
    print(f"  Average aircraft per runway: {len(atc_system.aircraft) / len(atc_system.runways):.1f}")


if __name__ == "__main__":
    main()