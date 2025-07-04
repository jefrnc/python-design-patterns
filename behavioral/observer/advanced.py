"""
Observer Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Event-driven architecture with async observers
- Generic typing with TypeVar and Protocol for type safety
- High-performance event dispatching with priority queues
- Memory-efficient weak references to prevent memory leaks
- Thread-safe concurrent notifications with locks
- Event filtering and transformation pipelines
- Performance monitoring and comprehensive metrics
- Advanced subscription management with wildcards
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Awaitable, Type, runtime_checkable,
    Set, Pattern, Match
)
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import asyncio
import threading
import functools
import weakref
import time
import uuid
import re
import heapq
import logging
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import inspect

# Type variables
EventT = TypeVar('EventT')
ObserverT = TypeVar('ObserverT', bound='Observer')
SubjectT = TypeVar('SubjectT', bound='Subject')


class EventPriority(Enum):
    """Event priority levels for ordered processing."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class NotificationStrategy(Enum):
    """Strategies for notification delivery."""
    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"
    PRIORITY = "priority"


@dataclass
class EventMetadata:
    """Metadata for event tracking and processing."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    source: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    correlation_id: Optional[str] = None
    ttl: Optional[timedelta] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Event(Generic[EventT]):
    """Optimized event with metadata and payload."""
    data: EventT
    type: str
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    def is_expired(self) -> bool:
        """Check if event has expired."""
        if not self.metadata.ttl:
            return False
        age = datetime.now() - self.metadata.timestamp
        return age > self.metadata.ttl
    
    def matches_pattern(self, pattern: str) -> bool:
        """Check if event type matches pattern (supports wildcards)."""
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(f"^{regex_pattern}$", self.type))


@dataclass
class ObserverMetrics:
    """Performance metrics for observers."""
    notifications_received: int = 0
    notifications_processed: int = 0
    notifications_failed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    last_notification: Optional[datetime] = None
    
    def update(self, processing_time: float, success: bool):
        """Update metrics with processing result."""
        self.notifications_received += 1
        if success:
            self.notifications_processed += 1
        else:
            self.notifications_failed += 1
        
        self.total_processing_time += processing_time
        self.average_processing_time = self.total_processing_time / self.notifications_received
        self.last_notification = datetime.now()


@runtime_checkable
class Observer(Protocol[EventT]):
    """Protocol for observers with advanced features."""
    
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        ...
    
    async def notify(self, event: Event[EventT]) -> bool:
        """Receive notification of an event."""
        ...
    
    def get_subscription_patterns(self) -> List[str]:
        """Get event patterns this observer subscribes to."""
        ...
    
    def should_receive_event(self, event: Event[EventT]) -> bool:
        """Check if observer should receive this event."""
        ...


class AsyncObserver(Generic[EventT]):
    """
    High-performance async observer with filtering and metrics.
    """
    
    def __init__(self, observer_id: str = None, 
                 patterns: List[str] = None,
                 filters: List[Callable[[Event[EventT]], bool]] = None):
        self.observer_id = observer_id or f"observer_{uuid.uuid4()}"
        self.subscription_patterns = patterns or ["*"]
        self.filters = filters or []
        self.metrics = ObserverMetrics()
        self._enabled = True
        self._lock = asyncio.Lock()
    
    def get_observer_id(self) -> str:
        return self.observer_id
    
    async def notify(self, event: Event[EventT]) -> bool:
        """Process event notification with metrics."""
        if not self._enabled or not self.should_receive_event(event):
            return False
        
        start_time = time.time()
        success = False
        
        async with self._lock:
            try:
                success = await self.handle_event(event)
            except Exception as e:
                logging.error(f"Observer {self.observer_id} failed to handle event: {e}")
            finally:
                processing_time = time.time() - start_time
                self.metrics.update(processing_time, success)
        
        return success
    
    async def handle_event(self, event: Event[EventT]) -> bool:
        """Handle event (to be overridden by subclasses)."""
        return True
    
    def get_subscription_patterns(self) -> List[str]:
        return self.subscription_patterns
    
    def should_receive_event(self, event: Event[EventT]) -> bool:
        """Check if observer should receive this event."""
        # Check patterns
        pattern_match = any(
            event.matches_pattern(pattern) 
            for pattern in self.subscription_patterns
        )
        
        if not pattern_match:
            return False
        
        # Apply filters
        return all(filter_func(event) for filter_func in self.filters)
    
    def add_filter(self, filter_func: Callable[[Event[EventT]], bool]) -> None:
        """Add event filter."""
        self.filters.append(filter_func)
    
    def enable(self) -> None:
        """Enable observer."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable observer."""
        self._enabled = False
    
    def get_metrics(self) -> ObserverMetrics:
        return self.metrics


class FunctionalObserver(AsyncObserver[EventT]):
    """Observer that wraps a function for event handling."""
    
    def __init__(self, handler_func: Callable[[Event[EventT]], Awaitable[bool]], 
                 **kwargs):
        super().__init__(**kwargs)
        self.handler_func = handler_func
    
    async def handle_event(self, event: Event[EventT]) -> bool:
        """Handle event using the provided function."""
        if asyncio.iscoroutinefunction(self.handler_func):
            return await self.handler_func(event)
        else:
            return self.handler_func(event)


@runtime_checkable
class Subject(Protocol[EventT]):
    """Protocol for subjects that can be observed."""
    
    def attach(self, observer: Observer[EventT], patterns: List[str] = None) -> None:
        """Attach observer with optional patterns."""
        ...
    
    def detach(self, observer: Observer[EventT]) -> None:
        """Detach observer."""
        ...
    
    async def notify_observers(self, event: Event[EventT]) -> List[bool]:
        """Notify all relevant observers."""
        ...


class EventDispatcher:
    """High-performance event dispatcher with priority queuing."""
    
    def __init__(self, max_workers: int = 10, 
                 batch_size: int = 50,
                 batch_timeout: float = 0.1):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        self._priority_queue: List[tuple] = []  # (priority, timestamp, event, observers)
        self._batch_queue: List[tuple] = []  # For batch processing
        self._queue_lock = threading.RLock()
        self._worker_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._running = False
        self._metrics = defaultdict(int)
    
    async def dispatch_event(self, event: Event, observers: List[Observer], 
                           strategy: NotificationStrategy = NotificationStrategy.ASYNC) -> List[bool]:
        """Dispatch event to observers using specified strategy."""
        
        if strategy == NotificationStrategy.SYNC:
            return await self._dispatch_sync(event, observers)
        elif strategy == NotificationStrategy.ASYNC:
            return await self._dispatch_async(event, observers)
        elif strategy == NotificationStrategy.BATCH:
            await self._dispatch_batch(event, observers)
            return []  # Batch processing doesn't return immediate results
        elif strategy == NotificationStrategy.PRIORITY:
            await self._dispatch_priority(event, observers)
            return []
        else:
            raise ValueError(f"Unknown notification strategy: {strategy}")
    
    async def _dispatch_sync(self, event: Event, observers: List[Observer]) -> List[bool]:
        """Synchronous event dispatch."""
        results = []
        for observer in observers:
            try:
                result = await observer.notify(event)
                results.append(result)
                self._metrics['sync_notifications'] += 1
            except Exception as e:
                logging.error(f"Sync notification failed: {e}")
                results.append(False)
                self._metrics['sync_failures'] += 1
        return results
    
    async def _dispatch_async(self, event: Event, observers: List[Observer]) -> List[bool]:
        """Asynchronous event dispatch."""
        tasks = []
        for observer in observers:
            task = asyncio.create_task(observer.notify(event))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Async notification failed: {result}")
                processed_results.append(False)
                self._metrics['async_failures'] += 1
            else:
                processed_results.append(result)
                self._metrics['async_notifications'] += 1
        
        return processed_results
    
    async def _dispatch_batch(self, event: Event, observers: List[Observer]) -> None:
        """Add to batch queue for later processing."""
        with self._queue_lock:
            self._batch_queue.append((event, observers))
            
            if len(self._batch_queue) >= self.batch_size:
                await self._process_batch()
    
    async def _dispatch_priority(self, event: Event, observers: List[Observer]) -> None:
        """Add to priority queue for ordered processing."""
        priority = event.metadata.priority.value
        timestamp = time.time()
        
        with self._queue_lock:
            heapq.heappush(self._priority_queue, (priority, timestamp, event, observers))
    
    async def _process_batch(self) -> None:
        """Process accumulated batch events."""
        if not self._batch_queue:
            return
        
        with self._queue_lock:
            batch = self._batch_queue.copy()
            self._batch_queue.clear()
        
        # Group events by observer to optimize notifications
        observer_events = defaultdict(list)
        
        for event, observers in batch:
            for observer in observers:
                observer_events[observer.get_observer_id()].append(event)
        
        # Process each observer's events
        tasks = []
        for observer_id, events in observer_events.items():
            # Find observer instance (simplified - in practice you'd maintain a registry)
            observer = next((obs for _, obs_list in batch for obs in obs_list 
                           if obs.get_observer_id() == observer_id), None)
            if observer:
                task = asyncio.create_task(self._notify_observer_batch(observer, events))
                tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        self._metrics['batch_processed'] += len(batch)
    
    async def _notify_observer_batch(self, observer: Observer, events: List[Event]) -> None:
        """Notify observer with batch of events."""
        for event in events:
            try:
                await observer.notify(event)
            except Exception as e:
                logging.error(f"Batch notification failed: {e}")
    
    async def start_background_processing(self) -> None:
        """Start background processing of queued events."""
        if self._running:
            return
        
        self._running = True
        self._batch_processor_task = asyncio.create_task(self._background_processor())
    
    async def stop_background_processing(self) -> None:
        """Stop background processing."""
        self._running = False
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass
    
    async def _background_processor(self) -> None:
        """Background task for processing queued events."""
        while self._running:
            try:
                # Process priority queue
                await self._process_priority_queue()
                
                # Process batch queue if timeout reached
                await self._process_batch()
                
                await asyncio.sleep(self.batch_timeout)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Background processor error: {e}")
    
    async def _process_priority_queue(self) -> None:
        """Process events from priority queue."""
        events_to_process = []
        
        with self._queue_lock:
            while self._priority_queue:
                priority, timestamp, event, observers = heapq.heappop(self._priority_queue)
                events_to_process.append((event, observers))
                
                # Process in batches to avoid blocking
                if len(events_to_process) >= 10:
                    break
        
        # Process events
        for event, observers in events_to_process:
            await self._dispatch_async(event, observers)
            self._metrics['priority_processed'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get dispatcher metrics."""
        with self._queue_lock:
            return {
                "queue_sizes": {
                    "priority": len(self._priority_queue),
                    "batch": len(self._batch_queue)
                },
                "metrics": dict(self._metrics),
                "worker_pool_active": self._worker_pool._threads,
                "background_running": self._running
            }


class OptimizedSubject(Generic[EventT]):
    """
    High-performance subject with advanced observer management.
    """
    
    def __init__(self, subject_id: str = None,
                 max_observers: int = 1000,
                 notification_strategy: NotificationStrategy = NotificationStrategy.ASYNC):
        self.subject_id = subject_id or f"subject_{uuid.uuid4()}"
        self.max_observers = max_observers
        self.notification_strategy = notification_strategy
        
        # Use weak references to prevent memory leaks
        self._observers: weakref.WeakSet = weakref.WeakSet()
        self._pattern_observers: Dict[str, weakref.WeakSet] = defaultdict(lambda: weakref.WeakSet())
        self._observer_registry: Dict[str, Observer] = weakref.WeakValueDictionary()
        
        self._dispatcher = EventDispatcher()
        self._event_history: deque = deque(maxlen=100)
        self._subscription_lock = threading.RLock()
        self._metrics = defaultdict(int)
        
        # Event middleware
        self._event_middleware: List[Callable[[Event[EventT]], Event[EventT]]] = []
        
    def attach(self, observer: Observer[EventT], patterns: List[str] = None) -> bool:
        """Attach observer with optional subscription patterns."""
        if len(self._observers) >= self.max_observers:
            return False
        
        with self._subscription_lock:
            self._observers.add(observer)
            self._observer_registry[observer.get_observer_id()] = observer
            
            # Register patterns
            subscription_patterns = patterns or observer.get_subscription_patterns()
            for pattern in subscription_patterns:
                self._pattern_observers[pattern].add(observer)
            
            self._metrics['observers_attached'] += 1
            return True
    
    def detach(self, observer: Observer[EventT]) -> bool:
        """Detach observer from all subscriptions."""
        with self._subscription_lock:
            if observer in self._observers:
                self._observers.discard(observer)
                
                # Remove from pattern subscriptions
                for pattern_set in self._pattern_observers.values():
                    pattern_set.discard(observer)
                
                # Remove from registry
                self._observer_registry.pop(observer.get_observer_id(), None)
                
                self._metrics['observers_detached'] += 1
                return True
            
            return False
    
    def detach_by_id(self, observer_id: str) -> bool:
        """Detach observer by ID."""
        observer = self._observer_registry.get(observer_id)
        if observer:
            return self.detach(observer)
        return False
    
    async def notify_observers(self, event: Event[EventT]) -> List[bool]:
        """Notify all relevant observers with optimized filtering."""
        
        # Apply event middleware
        for middleware in self._event_middleware:
            event = middleware(event)
        
        # Check if event has expired
        if event.is_expired():
            return []
        
        # Add to history
        self._event_history.append(event)
        
        # Find matching observers
        matching_observers = self._find_matching_observers(event)
        
        if not matching_observers:
            return []
        
        # Dispatch event
        results = await self._dispatcher.dispatch_event(
            event, 
            matching_observers, 
            self.notification_strategy
        )
        
        self._metrics['events_dispatched'] += 1
        self._metrics['total_notifications'] += len(matching_observers)
        
        return results
    
    async def broadcast(self, event_type: str, data: EventT, 
                       priority: EventPriority = EventPriority.NORMAL,
                       tags: Set[str] = None,
                       correlation_id: str = None) -> List[bool]:
        """Broadcast event to all relevant observers."""
        metadata = EventMetadata(
            priority=priority,
            source=self.subject_id,
            tags=tags or set(),
            correlation_id=correlation_id
        )
        
        event = Event(data=data, type=event_type, metadata=metadata)
        return await self.notify_observers(event)
    
    def _find_matching_observers(self, event: Event[EventT]) -> List[Observer[EventT]]:
        """Find observers that should receive this event."""
        matching_observers = []
        
        with self._subscription_lock:
            # Check pattern-based subscriptions
            for pattern, observers in self._pattern_observers.items():
                if event.matches_pattern(pattern):
                    for observer in list(observers):  # Convert to list to avoid modification during iteration
                        if observer.should_receive_event(event):
                            matching_observers.append(observer)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_observers = []
        for observer in matching_observers:
            observer_id = observer.get_observer_id()
            if observer_id not in seen:
                seen.add(observer_id)
                unique_observers.append(observer)
        
        return unique_observers
    
    def add_event_middleware(self, middleware: Callable[[Event[EventT]], Event[EventT]]) -> None:
        """Add middleware for event processing."""
        self._event_middleware.append(middleware)
    
    def get_observer_count(self) -> int:
        """Get current number of observers."""
        return len(self._observers)
    
    def get_observers_by_pattern(self, pattern: str) -> List[Observer[EventT]]:
        """Get all observers subscribed to a pattern."""
        with self._subscription_lock:
            return list(self._pattern_observers.get(pattern, []))
    
    def get_event_history(self, limit: int = 10) -> List[Event[EventT]]:
        """Get recent event history."""
        return list(self._event_history)[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive subject metrics."""
        observer_metrics = {}
        for observer_id, observer in self._observer_registry.items():
            if hasattr(observer, 'get_metrics'):
                observer_metrics[observer_id] = observer.get_metrics()
        
        return {
            "subject_metrics": dict(self._metrics),
            "observer_count": len(self._observers),
            "pattern_subscriptions": {k: len(v) for k, v in self._pattern_observers.items()},
            "dispatcher_metrics": self._dispatcher.get_metrics(),
            "observer_metrics": observer_metrics,
            "event_history_size": len(self._event_history)
        }
    
    async def start_background_processing(self) -> None:
        """Start background event processing."""
        await self._dispatcher.start_background_processing()
    
    async def stop_background_processing(self) -> None:
        """Stop background event processing."""
        await self._dispatcher.stop_background_processing()


# Utility decorators and functions
def observer(patterns: List[str] = None, 
            filters: List[Callable] = None,
            priority: EventPriority = EventPriority.NORMAL):
    """Decorator for creating functional observers."""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler_patterns = patterns or ["*"]
            handler_filters = filters or []
            
            return FunctionalObserver(
                handler_func=func,
                patterns=handler_patterns,
                filters=handler_filters
            )
        
        return wrapper
    return decorator


def event_filter(condition: Callable[[Event], bool]):
    """Decorator for creating event filters."""
    return condition


def throttle_observer(rate_limit: int, time_window: timedelta = timedelta(seconds=1)):
    """Decorator for rate-limiting observer notifications."""
    
    def decorator(observer_class):
        class ThrottledObserver(observer_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._rate_limiter = RateLimiter(rate_limit, time_window)
            
            async def notify(self, event: Event) -> bool:
                if self._rate_limiter.should_allow():
                    return await super().notify(event)
                return False
        
        return ThrottledObserver
    return decorator


class RateLimiter:
    """Rate limiter for controlling notification frequency."""
    
    def __init__(self, rate_limit: int, time_window: timedelta):
        self.rate_limit = rate_limit
        self.time_window = time_window
        self._request_times: deque = deque()
        self._lock = threading.RLock()
    
    def should_allow(self) -> bool:
        """Check if request should be allowed."""
        now = datetime.now()
        
        with self._lock:
            # Remove old requests outside time window
            while (self._request_times and 
                   now - self._request_times[0] > self.time_window):
                self._request_times.popleft()
            
            # Check if under rate limit
            if len(self._request_times) < self.rate_limit:
                self._request_times.append(now)
                return True
            
            return False


def main():
    """Demonstrate the optimized observer pattern."""
    print("=== Optimized Observer Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Event-driven architecture with async observers")
    print("✓ Generic typing with Protocol for type safety")
    print("✓ High-performance event dispatching with priority queues")
    print("✓ Memory-efficient weak references to prevent leaks")
    print("✓ Thread-safe concurrent notifications")
    print("✓ Event filtering and transformation pipelines")
    print("✓ Performance monitoring and comprehensive metrics")
    print("✓ Advanced subscription management with wildcards")
    print("✓ Multiple notification strategies (sync/async/batch/priority)")
    print("✓ Rate limiting and throttling capabilities")
    print("✓ Background event processing with queues")
    print("✓ Event middleware for transformation and validation")


if __name__ == "__main__":
    main()