"""
Mediator Design Pattern - Gang of Four Implementation

Intent: Define an object that encapsulates how a set of objects interact.
Mediator promotes loose coupling by keeping objects from referring to each other
explicitly, and it lets you vary their interaction independently.

Structure:
- Mediator: defines the interface for communication between Component objects
- ConcreteMediator: implements the Mediator interface and coordinates communication
- Component: defines the interface for communication with the Mediator
- ConcreteComponent: implements the Component interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class Mediator(ABC):
    """
    The Mediator interface declares a method used by components to notify the
    mediator about various events. The Mediator may react to these events and
    pass the execution to other components.
    """
    
    @abstractmethod
    def notify(self, sender: 'Component', event: str, data: Any = None) -> None:
        pass


class Component(ABC):
    """
    The Base Component provides the basic functionality of storing a mediator's
    instance inside component objects.
    """
    
    def __init__(self, mediator: Mediator = None):
        self._mediator = mediator
    
    @property
    def mediator(self) -> Mediator:
        return self._mediator
    
    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator


class ConcreteMediator(Mediator):
    """
    Concrete Mediators implement cooperative behavior by coordinating several
    components.
    """
    
    def __init__(self, component1: 'ComponentA', component2: 'ComponentB'):
        self._component1 = component1
        self._component1.mediator = self
        self._component2 = component2
        self._component2.mediator = self
    
    def notify(self, sender: Component, event: str, data: Any = None) -> None:
        if event == "A":
            print("Mediator reacts on A and triggers following operations:")
            self._component2.do_c()
        elif event == "D":
            print("Mediator reacts on D and triggers following operations:")
            self._component1.do_b()
            self._component2.do_c()


class ComponentA(Component):
    """
    Concrete Components implement various functionality. They don't depend on
    other components. They also don't depend on any concrete mediator classes.
    """
    
    def do_a(self) -> None:
        print("Component A does A.")
        self.mediator.notify(self, "A")
    
    def do_b(self) -> None:
        print("Component A does B.")
        self.mediator.notify(self, "B")


class ComponentB(Component):
    """
    Concrete Components implement various functionality. They don't depend on
    other components. They also don't depend on any concrete mediator classes.
    """
    
    def do_c(self) -> None:
        print("Component B does C.")
        self.mediator.notify(self, "C")
    
    def do_d(self) -> None:
        print("Component B does D.")
        self.mediator.notify(self, "D")


# More realistic example: Chat Room
class ChatMediator(ABC):
    """
    Abstract mediator for chat room.
    """
    
    @abstractmethod
    def send_message(self, message: str, user: 'User') -> None:
        pass
    
    @abstractmethod
    def add_user(self, user: 'User') -> None:
        pass
    
    @abstractmethod
    def remove_user(self, user: 'User') -> None:
        pass


class ChatRoom(ChatMediator):
    """
    Concrete chat room mediator.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._users: List['User'] = []
    
    def send_message(self, message: str, sender: 'User') -> None:
        """
        Send message to all users except the sender.
        """
        print(f"[{self._name}] {sender.name}: {message}")
        for user in self._users:
            if user != sender:
                user.receive(message, sender)
    
    def send_private_message(self, message: str, sender: 'User', recipient: 'User') -> None:
        """
        Send private message to specific user.
        """
        if recipient in self._users:
            print(f"[{self._name}] {sender.name} -> {recipient.name}: {message}")
            recipient.receive(f"[Private] {message}", sender)
        else:
            sender.receive(f"User {recipient.name} not found in chat room", None)
    
    def add_user(self, user: 'User') -> None:
        """
        Add user to chat room.
        """
        if user not in self._users:
            self._users.append(user)
            user.chat_room = self
            print(f"[{self._name}] {user.name} joined the chat")
            self.send_message(f"{user.name} has joined the chat", user)
    
    def remove_user(self, user: 'User') -> None:
        """
        Remove user from chat room.
        """
        if user in self._users:
            self._users.remove(user)
            user.chat_room = None
            print(f"[{self._name}] {user.name} left the chat")
            self.send_message(f"{user.name} has left the chat", user)
    
    def get_users(self) -> List['User']:
        """
        Get list of users in the chat room.
        """
        return self._users.copy()
    
    @property
    def name(self) -> str:
        return self._name


class User:
    """
    User component that communicates through the mediator.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._chat_room: Optional[ChatRoom] = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def chat_room(self) -> Optional[ChatRoom]:
        return self._chat_room
    
    @chat_room.setter
    def chat_room(self, chat_room: Optional[ChatRoom]) -> None:
        self._chat_room = chat_room
    
    def send(self, message: str) -> None:
        """
        Send message to chat room.
        """
        if self._chat_room:
            self._chat_room.send_message(message, self)
        else:
            print(f"{self._name}: Not connected to any chat room")
    
    def send_private(self, message: str, recipient: 'User') -> None:
        """
        Send private message to specific user.
        """
        if self._chat_room:
            self._chat_room.send_private_message(message, self, recipient)
        else:
            print(f"{self._name}: Not connected to any chat room")
    
    def receive(self, message: str, sender: Optional['User']) -> None:
        """
        Receive message from another user.
        """
        sender_name = sender.name if sender else "System"
        print(f"  {self._name} received: {message} (from {sender_name})")
    
    def join_chat(self, chat_room: ChatRoom) -> None:
        """
        Join a chat room.
        """
        chat_room.add_user(self)
    
    def leave_chat(self) -> None:
        """
        Leave current chat room.
        """
        if self._chat_room:
            self._chat_room.remove_user(self)


# Air Traffic Control example
class AirTrafficControl(ABC):
    """
    Abstract mediator for air traffic control.
    """
    
    @abstractmethod
    def request_landing(self, aircraft: 'Aircraft') -> None:
        pass
    
    @abstractmethod
    def request_takeoff(self, aircraft: 'Aircraft') -> None:
        pass
    
    @abstractmethod
    def register_aircraft(self, aircraft: 'Aircraft') -> None:
        pass


class Airport(AirTrafficControl):
    """
    Concrete air traffic control mediator.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._runway_busy = False
        self._aircraft_queue: List['Aircraft'] = []
        self._registered_aircraft: List['Aircraft'] = []
    
    def register_aircraft(self, aircraft: 'Aircraft') -> None:
        """
        Register aircraft with the control tower.
        """
        if aircraft not in self._registered_aircraft:
            self._registered_aircraft.append(aircraft)
            aircraft.control_tower = self
            print(f"[{self._name} ATC] {aircraft.call_sign} registered")
    
    def request_landing(self, aircraft: 'Aircraft') -> None:
        """
        Handle landing request.
        """
        print(f"[{self._name} ATC] Landing request from {aircraft.call_sign}")
        
        if not self._runway_busy:
            self._runway_busy = True
            aircraft.land()
            self._runway_busy = False
            self._process_queue()
        else:
            print(f"[{self._name} ATC] Runway busy, {aircraft.call_sign} added to queue")
            self._aircraft_queue.append(aircraft)
    
    def request_takeoff(self, aircraft: 'Aircraft') -> None:
        """
        Handle takeoff request.
        """
        print(f"[{self._name} ATC] Takeoff request from {aircraft.call_sign}")
        
        if not self._runway_busy:
            self._runway_busy = True
            aircraft.takeoff()
            self._runway_busy = False
            self._process_queue()
        else:
            print(f"[{self._name} ATC] Runway busy, {aircraft.call_sign} added to queue")
            self._aircraft_queue.append(aircraft)
    
    def _process_queue(self) -> None:
        """
        Process aircraft queue when runway becomes available.
        """
        if self._aircraft_queue and not self._runway_busy:
            next_aircraft = self._aircraft_queue.pop(0)
            print(f"[{self._name} ATC] Processing next aircraft: {next_aircraft.call_sign}")
            
            if next_aircraft.status == "approaching":
                self.request_landing(next_aircraft)
            elif next_aircraft.status == "ready_for_takeoff":
                self.request_takeoff(next_aircraft)
    
    @property
    def name(self) -> str:
        return self._name


class Aircraft:
    """
    Aircraft component that communicates through the mediator.
    """
    
    def __init__(self, call_sign: str):
        self._call_sign = call_sign
        self._status = "idle"
        self._control_tower: Optional[Airport] = None
    
    @property
    def call_sign(self) -> str:
        return self._call_sign
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def control_tower(self) -> Optional[Airport]:
        return self._control_tower
    
    @control_tower.setter
    def control_tower(self, tower: Optional[Airport]) -> None:
        self._control_tower = tower
    
    def approach_airport(self) -> None:
        """
        Approach airport for landing.
        """
        self._status = "approaching"
        print(f"{self._call_sign}: Approaching for landing")
        if self._control_tower:
            self._control_tower.request_landing(self)
    
    def prepare_takeoff(self) -> None:
        """
        Prepare for takeoff.
        """
        self._status = "ready_for_takeoff"
        print(f"{self._call_sign}: Ready for takeoff")
        if self._control_tower:
            self._control_tower.request_takeoff(self)
    
    def land(self) -> None:
        """
        Land the aircraft.
        """
        self._status = "landed"
        print(f"{self._call_sign}: Landing completed")
    
    def takeoff(self) -> None:
        """
        Takeoff the aircraft.
        """
        self._status = "airborne"
        print(f"{self._call_sign}: Takeoff completed")


# Smart Home example
class SmartHomeMediator:
    """
    Smart home mediator that coordinates various devices.
    """
    
    def __init__(self):
        self._devices: List['SmartDevice'] = []
        self._scenarios: dict = {
            "morning": self._morning_scenario,
            "night": self._night_scenario,
            "away": self._away_scenario,
            "home": self._home_scenario
        }
    
    def register_device(self, device: 'SmartDevice') -> None:
        """
        Register a smart device.
        """
        if device not in self._devices:
            self._devices.append(device)
            device.mediator = self
            print(f"SmartHome: {device.name} registered")
    
    def notify(self, sender: 'SmartDevice', event: str, data: Any = None) -> None:
        """
        Handle device notifications.
        """
        print(f"SmartHome: Received {event} from {sender.name}")
        
        if event == "motion_detected":
            self._handle_motion_detection(data)
        elif event == "door_opened":
            self._handle_door_opened()
        elif event == "temperature_change":
            self._handle_temperature_change(data)
        elif event == "light_on":
            self._handle_light_on(sender)
    
    def execute_scenario(self, scenario: str) -> None:
        """
        Execute a predefined scenario.
        """
        if scenario in self._scenarios:
            print(f"SmartHome: Executing {scenario} scenario")
            self._scenarios[scenario]()
        else:
            print(f"SmartHome: Unknown scenario: {scenario}")
    
    def _morning_scenario(self) -> None:
        """
        Morning scenario.
        """
        for device in self._devices:
            if device.device_type == "light":
                device.turn_on()
            elif device.device_type == "thermostat":
                device.set_temperature(22)
            elif device.device_type == "coffee_maker":
                device.start_brewing()
    
    def _night_scenario(self) -> None:
        """
        Night scenario.
        """
        for device in self._devices:
            if device.device_type == "light":
                device.turn_off()
            elif device.device_type == "thermostat":
                device.set_temperature(18)
            elif device.device_type == "security":
                device.arm()
    
    def _away_scenario(self) -> None:
        """
        Away scenario.
        """
        for device in self._devices:
            if device.device_type == "light":
                device.turn_off()
            elif device.device_type == "thermostat":
                device.set_temperature(16)
            elif device.device_type == "security":
                device.arm()
    
    def _home_scenario(self) -> None:
        """
        Home scenario.
        """
        for device in self._devices:
            if device.device_type == "security":
                device.disarm()
            elif device.device_type == "thermostat":
                device.set_temperature(21)
    
    def _handle_motion_detection(self, room: str) -> None:
        """
        Handle motion detection.
        """
        for device in self._devices:
            if device.device_type == "light" and hasattr(device, 'room') and device.room == room:
                device.turn_on()
    
    def _handle_door_opened(self) -> None:
        """
        Handle door opening.
        """
        for device in self._devices:
            if device.device_type == "security":
                device.disarm()
    
    def _handle_temperature_change(self, temperature: float) -> None:
        """
        Handle temperature changes.
        """
        if temperature > 25:
            for device in self._devices:
                if device.device_type == "air_conditioning":
                    device.turn_on()
        elif temperature < 18:
            for device in self._devices:
                if device.device_type == "heater":
                    device.turn_on()
    
    def _handle_light_on(self, sender: 'SmartDevice') -> None:
        """
        Handle light being turned on.
        """
        # If it's late at night, dim other lights
        import datetime
        current_hour = datetime.datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            for device in self._devices:
                if device.device_type == "light" and device != sender:
                    device.dim(30)  # Dim to 30%


class SmartDevice:
    """
    Base class for smart home devices.
    """
    
    def __init__(self, name: str, device_type: str):
        self._name = name
        self._device_type = device_type
        self._mediator: Optional[SmartHomeMediator] = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def device_type(self) -> str:
        return self._device_type
    
    @property
    def mediator(self) -> Optional[SmartHomeMediator]:
        return self._mediator
    
    @mediator.setter
    def mediator(self, mediator: Optional[SmartHomeMediator]) -> None:
        self._mediator = mediator


class SmartLight(SmartDevice):
    """
    Smart light device.
    """
    
    def __init__(self, name: str, room: str):
        super().__init__(name, "light")
        self.room = room
        self._is_on = False
        self._brightness = 100
    
    def turn_on(self) -> None:
        self._is_on = True
        print(f"{self.name}: Light turned on")
        if self._mediator:
            self._mediator.notify(self, "light_on")
    
    def turn_off(self) -> None:
        self._is_on = False
        print(f"{self.name}: Light turned off")
    
    def dim(self, brightness: int) -> None:
        self._brightness = max(0, min(100, brightness))
        print(f"{self.name}: Dimmed to {self._brightness}%")


class SmartThermostat(SmartDevice):
    """
    Smart thermostat device.
    """
    
    def __init__(self, name: str):
        super().__init__(name, "thermostat")
        self._temperature = 20
    
    def set_temperature(self, temperature: int) -> None:
        self._temperature = temperature
        print(f"{self.name}: Temperature set to {self._temperature}°C")
        if self._mediator:
            self._mediator.notify(self, "temperature_change", self._temperature)


def main():
    """
    The client code demonstrates the Mediator pattern.
    """
    print("=== Mediator Pattern Demo ===")
    
    # Basic mediator pattern
    print("\n1. Basic Mediator Pattern:")
    
    c1 = ComponentA()
    c2 = ComponentB()
    mediator = ConcreteMediator(c1, c2)
    
    print("Client triggers operation A.")
    c1.do_a()
    
    print("\nClient triggers operation D.")
    c2.do_d()
    
    # Chat room example
    print("\n2. Chat Room Mediator:")
    
    chat_room = ChatRoom("General")
    
    alice = User("Alice")
    bob = User("Bob")
    charlie = User("Charlie")
    
    # Users join chat
    alice.join_chat(chat_room)
    bob.join_chat(chat_room)
    charlie.join_chat(chat_room)
    
    print(f"\nUsers in chat: {[user.name for user in chat_room.get_users()]}")
    
    # Send messages
    print("\nChat conversation:")
    alice.send("Hello everyone!")
    bob.send("Hi Alice!")
    charlie.send("Hey there!")
    
    # Private message
    print("\nPrivate message:")
    alice.send_private("How are you doing?", bob)
    
    # User leaves
    print("\nUser leaving:")
    bob.leave_chat()
    
    charlie.send("Where did Bob go?")
    
    # Air traffic control example
    print("\n3. Air Traffic Control Mediator:")
    
    airport = Airport("JFK")
    
    flight1 = Aircraft("AA123")
    flight2 = Aircraft("BA456")
    flight3 = Aircraft("LH789")
    
    # Register aircraft
    airport.register_aircraft(flight1)
    airport.register_aircraft(flight2)
    airport.register_aircraft(flight3)
    
    # Multiple aircraft requesting runway access
    print("\nAircraft operations:")
    flight1.approach_airport()
    flight2.prepare_takeoff()  # Should be queued
    flight3.approach_airport()  # Should be queued
    
    # Smart home example
    print("\n4. Smart Home Mediator:")
    
    smart_home = SmartHomeMediator()
    
    # Create devices
    living_room_light = SmartLight("Living Room Light", "living_room")
    bedroom_light = SmartLight("Bedroom Light", "bedroom")
    thermostat = SmartThermostat("Main Thermostat")
    
    # Register devices
    smart_home.register_device(living_room_light)
    smart_home.register_device(bedroom_light)
    smart_home.register_device(thermostat)
    
    # Execute scenarios
    print("\nExecuting scenarios:")
    smart_home.execute_scenario("morning")
    
    print("\nExecuting night scenario:")
    smart_home.execute_scenario("night")
    
    # Individual device actions
    print("\nIndividual device actions:")
    living_room_light.turn_on()  # This will trigger mediator logic
    thermostat.set_temperature(26)  # This might trigger AC


if __name__ == "__main__":
    main()