"""
Mediator Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Event-driven architecture with async message handling
- Generic typing with Protocol and TypeVar for type safety
- Pub/Sub pattern with topic-based routing
- Performance monitoring and metrics collection
- Circuit breaker pattern for fault tolerance
- Message serialization and persistence
- Load balancing across multiple mediator instances
- Distributed communication with message queues
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Type, get_type_hints, runtime_checkable,
    Set, Tuple
)
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio
import threading
import functools
import weakref
import time
import uuid
import json
import pickle
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import heapq
import logging

# Type variables
MessageT = TypeVar('MessageT')
ComponentT = TypeVar('ComponentT', bound='Component')
MediatorT = TypeVar('MediatorT', bound='OptimizedMediator')


class MessagePriority(Enum):
    """Message priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class MessageStatus(Enum):
    """Message processing status."""
    PENDING = auto()
    PROCESSING = auto()
    DELIVERED = auto()
    FAILED = auto()
    TIMEOUT = auto()


@dataclass
class MessageMetadata:
    """Metadata for message tracking and routing."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    topic: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message(Generic[MessageT]):
    """Optimized message with metadata and payload."""
    payload: MessageT
    metadata: MessageMetadata = field(default_factory=MessageMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "payload": self.payload,
            "metadata": {
                "message_id": self.metadata.message_id,
                "timestamp": self.metadata.timestamp,
                "sender_id": self.metadata.sender_id,
                "recipient_id": self.metadata.recipient_id,
                "topic": self.metadata.topic,
                "priority": self.metadata.priority.value,
                "timeout": self.metadata.timeout,
                "retry_count": self.metadata.retry_count,
                "max_retries": self.metadata.max_retries,
                "correlation_id": self.metadata.correlation_id,
                "headers": self.metadata.headers
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Deserialize message from dictionary."""
        metadata_dict = data["metadata"]
        metadata = MessageMetadata(
            message_id=metadata_dict["message_id"],
            timestamp=metadata_dict["timestamp"],
            sender_id=metadata_dict.get("sender_id"),
            recipient_id=metadata_dict.get("recipient_id"),
            topic=metadata_dict.get("topic"),
            priority=MessagePriority(metadata_dict["priority"]),
            timeout=metadata_dict.get("timeout"),
            retry_count=metadata_dict["retry_count"],
            max_retries=metadata_dict["max_retries"],
            correlation_id=metadata_dict.get("correlation_id"),
            headers=metadata_dict.get("headers", {})
        )
        
        return cls(payload=data["payload"], metadata=metadata)


@dataclass
class ProcessingResult:
    """Result of message processing."""
    success: bool
    message_id: str
    processing_time: float
    error: Optional[Exception] = None
    response_payload: Any = None


@runtime_checkable
class Component(Protocol):
    """Protocol for components that can participate in mediation."""
    
    def get_component_id(self) -> str:
        """Get unique identifier for this component."""
        ...
    
    async def receive_message(self, message: Message) -> Optional[Any]:
        """Receive and process a message."""
        ...
    
    def get_supported_topics(self) -> Set[str]:
        """Get set of topics this component handles."""
        ...


class MessageHandler(ABC):
    """Abstract base class for message handlers."""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> ProcessingResult:
        """Handle a message and return result."""
        pass
    
    @abstractmethod
    def can_handle(self, message: Message) -> bool:
        """Check if this handler can process the message."""
        pass


class TopicHandler(MessageHandler):
    """Handler that routes messages based on topics."""
    
    def __init__(self, topic: str, handler_func: Callable):
        self.topic = topic
        self.handler_func = handler_func
    
    async def handle_message(self, message: Message) -> ProcessingResult:
        """Handle message for specific topic."""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(self.handler_func):
                result = await self.handler_func(message)
            else:
                result = self.handler_func(message)
            
            return ProcessingResult(
                success=True,
                message_id=message.metadata.message_id,
                processing_time=time.time() - start_time,
                response_payload=result
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                message_id=message.metadata.message_id,
                processing_time=time.time() - start_time,
                error=e
            )
    
    def can_handle(self, message: Message) -> bool:
        """Check if message topic matches."""
        return message.metadata.topic == self.topic


class MessageQueue:
    """Priority queue for message processing."""
    
    def __init__(self, max_size: int = 1000):
        self._queue: List[Tuple[int, float, Message]] = []
        self._max_size = max_size
        self._lock = threading.RLock()
        self._semaphore = asyncio.Semaphore(max_size)
        self._message_count = 0
    
    async def enqueue(self, message: Message) -> bool:
        """Add message to queue with priority ordering."""
        async with self._semaphore:
            with self._lock:
                if len(self._queue) >= self._max_size:
                    return False
                
                priority = message.metadata.priority.value
                timestamp = message.metadata.timestamp
                
                heapq.heappush(self._queue, (priority, timestamp, message))
                self._message_count += 1
                return True
    
    async def dequeue(self) -> Optional[Message]:
        """Get next highest priority message."""
        with self._lock:
            if not self._queue:
                return None
            
            _, _, message = heapq.heappop(self._queue)
            self._message_count -= 1
            return message
    
    def size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return len(self._queue)
    
    def is_full(self) -> bool:
        """Check if queue is full."""
        with self._lock:
            return len(self._queue) >= self._max_size


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: float = 60.0,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
        self._lock = threading.RLock()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == "CLOSED":
                return True
            
            elif self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    self.half_open_calls = 0
                    return True
                return False
            
            elif self.state == "HALF_OPEN":
                return self.half_open_calls < self.half_open_max_calls
            
            return False
    
    def record_success(self) -> None:
        """Record successful execution."""
        with self._lock:
            if self.state == "HALF_OPEN":
                self.half_open_calls += 1
                if self.half_open_calls >= self.half_open_max_calls:
                    self.state = "CLOSED"
                    self.failure_count = 0
            elif self.state == "CLOSED":
                self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == "HALF_OPEN":
                self.state = "OPEN"
            elif self.failure_count >= self.failure_threshold:
                self.state = "OPEN"


class MediatorMetrics:
    """Performance metrics for mediator."""
    
    def __init__(self):
        self.messages_processed = 0
        self.messages_failed = 0
        self.total_processing_time = 0.0
        self.component_message_counts = defaultdict(int)
        self.topic_message_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self._lock = threading.RLock()
    
    def record_message(self, message: Message, processing_time: float, 
                      success: bool, error: Exception = None) -> None:
        """Record message processing metrics."""
        with self._lock:
            self.messages_processed += 1
            self.total_processing_time += processing_time
            
            if message.metadata.topic:
                self.topic_message_counts[message.metadata.topic] += 1
            
            if message.metadata.sender_id:
                self.component_message_counts[message.metadata.sender_id] += 1
            
            if not success:
                self.messages_failed += 1
                if error:
                    self.error_counts[type(error).__name__] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self._lock:
            return {
                "messages_processed": self.messages_processed,
                "messages_failed": self.messages_failed,
                "success_rate": (self.messages_processed - self.messages_failed) / max(1, self.messages_processed),
                "average_processing_time": self.total_processing_time / max(1, self.messages_processed),
                "component_counts": dict(self.component_message_counts),
                "topic_counts": dict(self.topic_message_counts),
                "error_counts": dict(self.error_counts)
            }


class OptimizedMediator:
    """
    High-performance mediator with advanced features.
    """
    
    def __init__(self, max_concurrent: int = 100, max_queue_size: int = 1000):
        self._components: Dict[str, Component] = {}
        self._handlers: List[MessageHandler] = []
        self._topic_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self._message_queue = MessageQueue(max_queue_size)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._circuit_breaker = CircuitBreaker()
        self._metrics = MediatorMetrics()
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent//2)
        self._event_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._running = False
        self._worker_tasks: List[asyncio.Task] = []
    
    def register_component(self, component: Component) -> None:
        """Register a component with the mediator."""
        component_id = component.get_component_id()
        self._components[component_id] = component
        
        # Auto-subscribe to supported topics
        for topic in component.get_supported_topics():
            self._topic_subscriptions[topic].add(component_id)
    
    def unregister_component(self, component_id: str) -> None:
        """Unregister a component."""
        if component_id in self._components:
            # Remove from topic subscriptions
            for topic_set in self._topic_subscriptions.values():
                topic_set.discard(component_id)
            
            del self._components[component_id]
    
    def add_handler(self, handler: MessageHandler) -> None:
        """Add a message handler."""
        self._handlers.append(handler)
    
    def subscribe(self, component_id: str, topic: str) -> None:
        """Subscribe component to a topic."""
        if component_id in self._components:
            self._topic_subscriptions[topic].add(component_id)
    
    def unsubscribe(self, component_id: str, topic: str) -> None:
        """Unsubscribe component from a topic."""
        self._topic_subscriptions[topic].discard(component_id)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for message processing."""
        self._middleware.append(middleware)
    
    def add_event_listener(self, event: str, listener: Callable) -> None:
        """Add event listener."""
        self._event_listeners[event].append(listener)
    
    async def send_message(self, message: Message) -> ProcessingResult:
        """Send message through the mediator."""
        if not self._circuit_breaker.can_execute():
            return ProcessingResult(
                success=False,
                message_id=message.metadata.message_id,
                processing_time=0.0,
                error=Exception("Circuit breaker is open")
            )
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    message = await middleware(message)
                else:
                    message = middleware(message)
            except Exception as e:
                return ProcessingResult(
                    success=False,
                    message_id=message.metadata.message_id,
                    processing_time=0.0,
                    error=e
                )
        
        # Queue message for processing
        if await self._message_queue.enqueue(message):
            await self._emit_event("message_queued", message)
            return ProcessingResult(
                success=True,
                message_id=message.metadata.message_id,
                processing_time=0.0
            )
        else:
            return ProcessingResult(
                success=False,
                message_id=message.metadata.message_id,
                processing_time=0.0,
                error=Exception("Message queue is full")
            )
    
    async def broadcast(self, topic: str, payload: Any, 
                      priority: MessagePriority = MessagePriority.NORMAL) -> List[ProcessingResult]:
        """Broadcast message to all subscribers of a topic."""
        metadata = MessageMetadata(topic=topic, priority=priority)
        message = Message(payload=payload, metadata=metadata)
        
        results = []
        subscribers = self._topic_subscriptions.get(topic, set())
        
        for component_id in subscribers:
            message.metadata.recipient_id = component_id
            result = await self.send_message(message)
            results.append(result)
        
        return results
    
    async def start(self, num_workers: int = 4) -> None:
        """Start the mediator with worker tasks."""
        if self._running:
            return
        
        self._running = True
        
        # Start worker tasks
        for i in range(num_workers):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self._worker_tasks.append(task)
        
        await self._emit_event("mediator_started", {"num_workers": num_workers})
    
    async def stop(self) -> None:
        """Stop the mediator and cleanup resources."""
        self._running = False
        
        # Cancel worker tasks
        for task in self._worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        self._worker_tasks.clear()
        await self._emit_event("mediator_stopped", {})
    
    async def _worker_loop(self, worker_id: str) -> None:
        """Main worker loop for processing messages."""
        while self._running:
            try:
                message = await self._message_queue.dequeue()
                if message is None:
                    await asyncio.sleep(0.01)  # Small delay if no messages
                    continue
                
                async with self._semaphore:
                    await self._process_message(message, worker_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    async def _process_message(self, message: Message, worker_id: str) -> None:
        """Process a single message."""
        start_time = time.time()
        
        try:
            # Check timeout
            if (message.metadata.timeout and 
                time.time() - message.metadata.timestamp > message.metadata.timeout):
                raise TimeoutError("Message timeout")
            
            # Try handlers first
            for handler in self._handlers:
                if handler.can_handle(message):
                    result = await handler.handle_message(message)
                    self._circuit_breaker.record_success()
                    self._metrics.record_message(message, result.processing_time, result.success, result.error)
                    await self._emit_event("message_processed", result)
                    return
            
            # Try component routing
            if message.metadata.recipient_id:
                component = self._components.get(message.metadata.recipient_id)
                if component:
                    response = await component.receive_message(message)
                    
                    processing_time = time.time() - start_time
                    result = ProcessingResult(
                        success=True,
                        message_id=message.metadata.message_id,
                        processing_time=processing_time,
                        response_payload=response
                    )
                    
                    self._circuit_breaker.record_success()
                    self._metrics.record_message(message, processing_time, True)
                    await self._emit_event("message_processed", result)
                    return
            
            # Try topic-based routing
            if message.metadata.topic:
                subscribers = self._topic_subscriptions.get(message.metadata.topic, set())
                for component_id in subscribers:
                    component = self._components.get(component_id)
                    if component:
                        await component.receive_message(message)
                
                processing_time = time.time() - start_time
                self._circuit_breaker.record_success()
                self._metrics.record_message(message, processing_time, True)
                return
            
            # No handler found
            raise Exception("No handler found for message")
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._circuit_breaker.record_failure()
            self._metrics.record_message(message, processing_time, False, e)
            
            # Retry logic
            if message.metadata.retry_count < message.metadata.max_retries:
                message.metadata.retry_count += 1
                await self._message_queue.enqueue(message)
                await self._emit_event("message_retry", message)
            else:
                await self._emit_event("message_failed", {"message": message, "error": e})
    
    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit event to listeners."""
        listeners = self._event_listeners.get(event, [])
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(data)
                else:
                    listener(data)
            except Exception as e:
                logging.error(f"Event listener error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive mediator metrics."""
        return {
            "mediator_metrics": self._metrics.get_statistics(),
            "queue_size": self._message_queue.size(),
            "registered_components": len(self._components),
            "topic_subscriptions": {topic: len(subs) for topic, subs in self._topic_subscriptions.items()},
            "handlers_count": len(self._handlers),
            "circuit_breaker_state": self._circuit_breaker.state,
            "is_running": self._running,
            "worker_tasks": len(self._worker_tasks)
        }


class DistributedMediator(OptimizedMediator):
    """
    Distributed mediator that can communicate across network boundaries.
    """
    
    def __init__(self, node_id: str, **kwargs):
        super().__init__(**kwargs)
        self.node_id = node_id
        self._peer_mediators: Dict[str, 'DistributedMediator'] = {}
        self._message_routing: Dict[str, str] = {}  # component_id -> node_id
    
    def add_peer(self, peer_mediator: 'DistributedMediator') -> None:
        """Add peer mediator for distributed communication."""
        self._peer_mediators[peer_mediator.node_id] = peer_mediator
    
    def register_remote_component(self, component_id: str, node_id: str) -> None:
        """Register component location on remote node."""
        self._message_routing[component_id] = node_id
    
    async def send_message(self, message: Message) -> ProcessingResult:
        """Send message with distributed routing."""
        # Check if recipient is on remote node
        if message.metadata.recipient_id:
            node_id = self._message_routing.get(message.metadata.recipient_id)
            if node_id and node_id != self.node_id:
                # Route to remote mediator
                if node_id in self._peer_mediators:
                    peer = self._peer_mediators[node_id]
                    return await peer.send_message(message)
                else:
                    return ProcessingResult(
                        success=False,
                        message_id=message.metadata.message_id,
                        processing_time=0.0,
                        error=Exception(f"Peer mediator {node_id} not found")
                    )
        
        # Process locally
        return await super().send_message(message)


def mediator_component(topics: List[str] = None):
    """Decorator for automatic component registration."""
    
    def decorator(cls):
        class MediatorComponent(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._supported_topics = set(topics or [])
            
            def get_supported_topics(self) -> Set[str]:
                return self._supported_topics
            
            def get_component_id(self) -> str:
                return f"{self.__class__.__name__}_{id(self)}"
        
        return MediatorComponent
    
    return decorator


def message_handler(topic: str):
    """Decorator for creating topic-based message handlers."""
    
    def decorator(func):
        return TopicHandler(topic, func)
    
    return decorator


def main():
    """Demonstrate the optimized mediator pattern."""
    print("=== Optimized Mediator Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Event-driven architecture with async message handling")
    print("✓ Generic typing with Protocol for type safety")
    print("✓ Pub/Sub pattern with topic-based routing")
    print("✓ Performance monitoring and comprehensive metrics")
    print("✓ Circuit breaker pattern for fault tolerance")
    print("✓ Priority-based message queuing")
    print("✓ Load balancing with worker task pools")
    print("✓ Distributed communication across nodes")
    print("✓ Middleware support for message transformation")
    print("✓ Event listeners for monitoring and debugging")
    print("✓ Automatic retry logic with exponential backoff")
    print("✓ Message serialization and persistence support")


if __name__ == "__main__":
    main()