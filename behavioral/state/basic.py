"""
State Design Pattern - Gang of Four Implementation

Intent: Allow an object to alter its behavior when its internal state changes.
The object will appear to change its class.

Structure:
- Context: maintains an instance of a ConcreteState subclass that defines the current state
- State: defines an interface for encapsulating the behavior associated with a particular state
- ConcreteState: implements a behavior associated with a state of the Context
"""

from abc import ABC, abstractmethod
from typing import Optional


class Context:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """
    
    def __init__(self, state: 'State'):
        self._state: Optional[State] = None
        self.transition_to(state)
    
    def transition_to(self, state: 'State') -> None:
        """
        The Context allows changing the State object at runtime.
        """
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self
    
    def request1(self) -> str:
        """
        The Context delegates part of its behavior to the current State object.
        """
        return self._state.handle1()
    
    def request2(self) -> str:
        """
        The Context delegates part of its behavior to the current State object.
        """
        return self._state.handle2()


class State(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a back reference to the Context object,
    associated with the State. This back reference can be used by States to
    transition the Context to another State.
    """
    
    def __init__(self):
        self._context: Optional[Context] = None
    
    @property
    def context(self) -> Context:
        return self._context
    
    @context.setter
    def context(self, context: Context) -> None:
        self._context = context
    
    @abstractmethod
    def handle1(self) -> str:
        pass
    
    @abstractmethod
    def handle2(self) -> str:
        pass


class ConcreteStateA(State):
    """
    Concrete States implement various behaviors, associated with a state of the
    Context.
    """
    
    def handle1(self) -> str:
        result = "ConcreteStateA handles request1."
        result += " ConcreteStateA wants to change the state of the context."
        self.context.transition_to(ConcreteStateB())
        return result
    
    def handle2(self) -> str:
        return "ConcreteStateA handles request2."


class ConcreteStateB(State):
    """
    Concrete States implement various behaviors, associated with a state of the
    Context.
    """
    
    def handle1(self) -> str:
        return "ConcreteStateB handles request1."
    
    def handle2(self) -> str:
        result = "ConcreteStateB handles request2."
        result += " ConcreteStateB wants to change the state of the context."
        self.context.transition_to(ConcreteStateA())
        return result


# More realistic example: Media Player
class MediaPlayer:
    """
    Media player context that changes behavior based on its state.
    """
    
    def __init__(self):
        self._state: Optional['MediaState'] = None
        self._volume = 50
        self._track = "No track loaded"
        self.change_state(StoppedState())
    
    def change_state(self, state: 'MediaState') -> None:
        """
        Change the current state of the media player.
        """
        print(f"MediaPlayer: Changing state to {type(state).__name__}")
        self._state = state
        self._state.player = self
    
    def play(self) -> str:
        """
        Play action delegates to current state.
        """
        return self._state.play()
    
    def pause(self) -> str:
        """
        Pause action delegates to current state.
        """
        return self._state.pause()
    
    def stop(self) -> str:
        """
        Stop action delegates to current state.
        """
        return self._state.stop()
    
    def next_track(self) -> str:
        """
        Next track action delegates to current state.
        """
        return self._state.next_track()
    
    @property
    def volume(self) -> int:
        return self._volume
    
    @volume.setter
    def volume(self, value: int) -> None:
        self._volume = max(0, min(100, value))
    
    @property
    def track(self) -> str:
        return self._track
    
    @track.setter
    def track(self, value: str) -> None:
        self._track = value
    
    def get_state_name(self) -> str:
        """
        Get the name of the current state.
        """
        return type(self._state).__name__


class MediaState(ABC):
    """
    Base state class for media player states.
    """
    
    def __init__(self):
        self._player: Optional[MediaPlayer] = None
    
    @property
    def player(self) -> MediaPlayer:
        return self._player
    
    @player.setter
    def player(self, player: MediaPlayer) -> None:
        self._player = player
    
    @abstractmethod
    def play(self) -> str:
        pass
    
    @abstractmethod
    def pause(self) -> str:
        pass
    
    @abstractmethod
    def stop(self) -> str:
        pass
    
    @abstractmethod
    def next_track(self) -> str:
        pass


class StoppedState(MediaState):
    """
    State when the media player is stopped.
    """
    
    def play(self) -> str:
        self.player.change_state(PlayingState())
        return f"Playing: {self.player.track}"
    
    def pause(self) -> str:
        return "Cannot pause - player is stopped"
    
    def stop(self) -> str:
        return "Player is already stopped"
    
    def next_track(self) -> str:
        # Simulate loading next track
        self.player.track = "Next Track"
        return f"Loaded next track: {self.player.track}"


class PlayingState(MediaState):
    """
    State when the media player is playing.
    """
    
    def play(self) -> str:
        return f"Already playing: {self.player.track}"
    
    def pause(self) -> str:
        self.player.change_state(PausedState())
        return f"Paused: {self.player.track}"
    
    def stop(self) -> str:
        self.player.change_state(StoppedState())
        return f"Stopped: {self.player.track}"
    
    def next_track(self) -> str:
        old_track = self.player.track
        self.player.track = "Next Track"
        return f"Switched from '{old_track}' to '{self.player.track}'"


class PausedState(MediaState):
    """
    State when the media player is paused.
    """
    
    def play(self) -> str:
        self.player.change_state(PlayingState())
        return f"Resumed playing: {self.player.track}"
    
    def pause(self) -> str:
        return f"Already paused: {self.player.track}"
    
    def stop(self) -> str:
        self.player.change_state(StoppedState())
        return f"Stopped: {self.player.track}"
    
    def next_track(self) -> str:
        old_track = self.player.track
        self.player.track = "Next Track"
        # Stay in paused state but with new track
        return f"Switched to '{self.player.track}' (still paused)"


# Traffic light example
class TrafficLight:
    """
    Traffic light context.
    """
    
    def __init__(self):
        self._state: Optional['TrafficState'] = None
        self.change_state(RedLightState())
    
    def change_state(self, state: 'TrafficState') -> None:
        print(f"TrafficLight: State changed to {type(state).__name__}")
        self._state = state
        self._state.traffic_light = self
    
    def next_state(self) -> str:
        return self._state.next_state()
    
    def get_color(self) -> str:
        return self._state.get_color()


class TrafficState(ABC):
    """
    Base state for traffic light states.
    """
    
    def __init__(self):
        self._traffic_light: Optional[TrafficLight] = None
    
    @property
    def traffic_light(self) -> TrafficLight:
        return self._traffic_light
    
    @traffic_light.setter
    def traffic_light(self, traffic_light: TrafficLight) -> None:
        self._traffic_light = traffic_light
    
    @abstractmethod
    def next_state(self) -> str:
        pass
    
    @abstractmethod
    def get_color(self) -> str:
        pass


class RedLightState(TrafficState):
    """
    Red light state.
    """
    
    def next_state(self) -> str:
        self.traffic_light.change_state(GreenLightState())
        return "Red -> Green: Go!"
    
    def get_color(self) -> str:
        return "Red"


class GreenLightState(TrafficState):
    """
    Green light state.
    """
    
    def next_state(self) -> str:
        self.traffic_light.change_state(YellowLightState())
        return "Green -> Yellow: Caution!"
    
    def get_color(self) -> str:
        return "Green"


class YellowLightState(TrafficState):
    """
    Yellow light state.
    """
    
    def next_state(self) -> str:
        self.traffic_light.change_state(RedLightState())
        return "Yellow -> Red: Stop!"
    
    def get_color(self) -> str:
        return "Yellow"


def main():
    """
    The client code demonstrates the State pattern.
    """
    print("=== State Pattern Demo ===")
    
    # Basic state pattern
    print("\n1. Basic State Pattern:")
    context = Context(ConcreteStateA())
    
    print(context.request1())
    print(context.request2())
    print(context.request1())
    print(context.request2())
    
    # Media player example
    print("\n2. Media Player State Machine:")
    player = MediaPlayer()
    player.track = "Song 1"
    
    print(f"Initial state: {player.get_state_name()}")
    print(f"Current track: {player.track}")
    
    # Test state transitions
    actions = [
        ("play", lambda: player.play()),
        ("pause", lambda: player.pause()),
        ("play", lambda: player.play()),
        ("stop", lambda: player.stop()),
        ("pause", lambda: player.pause()),
        ("next_track", lambda: player.next_track()),
        ("play", lambda: player.play()),
        ("next_track", lambda: player.next_track()),
        ("stop", lambda: player.stop())
    ]
    
    for action_name, action in actions:
        print(f"\nAction: {action_name}")
        result = action()
        print(f"Result: {result}")
        print(f"State: {player.get_state_name()}")
    
    # Traffic light example
    print("\n3. Traffic Light State Machine:")
    traffic_light = TrafficLight()
    
    print(f"Initial color: {traffic_light.get_color()}")
    
    # Cycle through several state changes
    for i in range(6):
        result = traffic_light.next_state()
        print(f"Change {i+1}: {result}")
        print(f"Current color: {traffic_light.get_color()}")
    
    # Demonstrate invalid operations in media player
    print("\n4. Invalid Operations Handling:")
    player2 = MediaPlayer()
    player2.track = "Test Song"
    
    print(f"State: {player2.get_state_name()}")
    print(f"Try to pause when stopped: {player2.pause()}")
    print(f"Try to stop when stopped: {player2.stop()}")
    
    player2.play()
    print(f"State: {player2.get_state_name()}")
    print(f"Try to play when playing: {player2.play()}")
    
    player2.pause()
    print(f"State: {player2.get_state_name()}")
    print(f"Try to pause when paused: {player2.pause()}")


if __name__ == "__main__":
    main()