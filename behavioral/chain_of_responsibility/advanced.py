"""
Chain of Responsibility Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Generic type hints with TypeVar and Protocol
- Async/await support for non-blocking processing
- Decorator-based handler registration
- Metaclass for automatic handler discovery
- Performance monitoring and metrics
- Caching and memoization
- Handler priority and routing optimization
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Type, get_type_hints, runtime_checkable
)
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import asyncio
import functools
import weakref
import time
import logging
from collections import defaultdict, deque
import heapq
import threading
from concurrent.futures import ThreadPoolExecutor

# Type variables for generic request/response
RequestT = TypeVar('RequestT')
ResponseT = TypeVar('ResponseT')
HandlerT = TypeVar('HandlerT', bound='AsyncHandler')


class Priority(Enum):
    """Handler priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class HandlerStatus(Enum):
    """Handler execution status."""
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
    TIMEOUT = auto()


@dataclass
class ProcessingResult(Generic[ResponseT]):
    """Result of chain processing with detailed metrics."""
    response: Optional[ResponseT] = None
    handler_name: Optional[str] = None
    status: HandlerStatus = HandlerStatus.FAILED
    processing_time: float = 0.0
    execution_path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None


@dataclass
class ChainMetrics:
    """Performance metrics for the chain."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_processing_time: float = 0.0
    handler_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cache_hits: int = 0
    cache_misses: int = 0


@runtime_checkable
class Request(Protocol):
    """Protocol for requests that can be processed by the chain."""
    
    def get_request_id(self) -> str:
        """Get unique identifier for this request."""
        ...
    
    def get_priority(self) -> Priority:
        """Get request priority."""
        ...
    
    def get_cache_key(self) -> Optional[str]:
        """Get cache key for this request (None if not cacheable)."""
        ...


class CacheableMixin:
    """Mixin for adding caching capabilities to requests."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache_key: Optional[str] = None
        self._cache_ttl: Optional[timedelta] = None
    
    def set_cache_key(self, key: str, ttl: timedelta = None) -> None:
        """Set cache key and TTL for this request."""
        self._cache_key = key
        self._cache_ttl = ttl or timedelta(minutes=5)
    
    def get_cache_key(self) -> Optional[str]:
        return self._cache_key


class HandlerRegistry:
    """Registry for automatic handler discovery and management."""
    
    def __init__(self):
        self._handlers: Dict[str, Type['AsyncHandler']] = {}
        self._priority_queue: List[tuple] = []  # (priority, name, handler_class)
        self._type_mappings: Dict[Type, List[str]] = defaultdict(list)
    
    def register(self, handler_class: Type['AsyncHandler'], 
                request_type: Type[RequestT] = None,
                priority: Priority = Priority.NORMAL) -> None:
        """Register a handler class."""
        name = handler_class.__name__
        self._handlers[name] = handler_class
        
        # Add to priority queue
        heapq.heappush(self._priority_queue, (priority.value, name, handler_class))
        
        # Map request types
        if request_type:
            self._type_mappings[request_type].append(name)
        else:
            # Try to infer from type hints
            type_hints = get_type_hints(handler_class.can_handle)
            if 'request' in type_hints:
                req_type = type_hints['request']
                self._type_mappings[req_type].append(name)
    
    def get_handlers_for_type(self, request_type: Type) -> List[Type['AsyncHandler']]:
        """Get all handlers that can process this request type."""
        handler_names = self._type_mappings.get(request_type, [])
        return [self._handlers[name] for name in handler_names]
    
    def get_all_handlers(self) -> List[Type['AsyncHandler']]:
        """Get all handlers sorted by priority."""
        return [handler_class for _, _, handler_class in sorted(self._priority_queue)]


# Global registry instance
handler_registry = HandlerRegistry()


def handler(request_type: Type[RequestT] = None, 
           priority: Priority = Priority.NORMAL,
           cache_results: bool = False,
           timeout: float = 30.0):
    """Decorator for registering handlers with automatic discovery."""
    
    def decorator(handler_class: Type[HandlerT]) -> Type[HandlerT]:
        # Add metadata to the class
        handler_class._request_type = request_type
        handler_class._priority = priority
        handler_class._cache_results = cache_results
        handler_class._timeout = timeout
        
        # Register in global registry
        handler_registry.register(handler_class, request_type, priority)
        
        return handler_class
    
    return decorator


class HandlerMetaMixin(type):
    """Metaclass for automatic handler configuration."""
    
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Auto-configure based on attributes
        if hasattr(cls, '_request_type') and hasattr(cls, '_priority'):
            handler_registry.register(cls, cls._request_type, cls._priority)
        
        return cls


class AsyncHandler(ABC, Generic[RequestT, ResponseT], metaclass=HandlerMetaMixin):
    """
    Optimized async handler with advanced features.
    """
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.next_handler: Optional['AsyncHandler'] = None
        self._metrics = ChainMetrics()
        self._cache: Dict[str, tuple] = {}  # key -> (response, timestamp)
        self._cache_lock = threading.RLock()
        self._processing_times = deque(maxlen=100)  # Rolling window
    
    def set_next(self, handler: 'AsyncHandler') -> 'AsyncHandler':
        """Set the next handler in the chain."""
        self.next_handler = handler
        return handler
    
    @abstractmethod
    async def can_handle(self, request: RequestT) -> bool:
        """Check if this handler can process the request."""
        pass
    
    @abstractmethod
    async def handle_request(self, request: RequestT) -> ResponseT:
        """Process the request and return response."""
        pass
    
    async def process(self, request: RequestT) -> ProcessingResult[ResponseT]:
        """
        Process request with full optimization features.
        """
        start_time = time.time()
        result = ProcessingResult[ResponseT]()
        result.execution_path.append(self.name)
        
        try:
            # Check cache first
            cache_key = None
            if hasattr(request, 'get_cache_key'):
                cache_key = request.get_cache_key()
                if cache_key:
                    cached_response = self._get_cached_response(cache_key)
                    if cached_response is not None:
                        self._metrics.cache_hits += 1
                        result.response = cached_response
                        result.status = HandlerStatus.SUCCESS
                        result.handler_name = self.name
                        result.metadata['cache_hit'] = True
                        return result
                    self._metrics.cache_misses += 1
            
            # Check if we can handle this request
            if await self.can_handle(request):
                # Apply timeout
                timeout = getattr(self.__class__, '_timeout', 30.0)
                
                try:
                    response = await asyncio.wait_for(
                        self.handle_request(request), 
                        timeout=timeout
                    )
                    
                    result.response = response
                    result.status = HandlerStatus.SUCCESS
                    result.handler_name = self.name
                    
                    # Cache result if configured
                    if cache_key and getattr(self.__class__, '_cache_results', False):
                        self._cache_response(cache_key, response)
                    
                    # Update metrics
                    self._metrics.successful_requests += 1
                    self._metrics.handler_usage[self.name] += 1
                    
                except asyncio.TimeoutError:
                    result.status = HandlerStatus.TIMEOUT
                    result.error = asyncio.TimeoutError(f"Handler {self.name} timed out")
                    self._metrics.failed_requests += 1
                
            else:
                # Pass to next handler
                if self.next_handler:
                    next_result = await self.next_handler.process(request)
                    result.response = next_result.response
                    result.status = next_result.status
                    result.handler_name = next_result.handler_name
                    result.execution_path.extend(next_result.execution_path)
                    result.metadata.update(next_result.metadata)
                    result.error = next_result.error
                else:
                    result.status = HandlerStatus.SKIPPED
        
        except Exception as e:
            result.error = e
            result.status = HandlerStatus.FAILED
            self._metrics.failed_requests += 1
        
        finally:
            # Update timing metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self._processing_times.append(processing_time)
            self._update_average_time()
            self._metrics.total_requests += 1
        
        return result
    
    def _get_cached_response(self, cache_key: str) -> Optional[ResponseT]:
        """Get cached response if valid."""
        with self._cache_lock:
            if cache_key in self._cache:
                response, timestamp = self._cache[cache_key]
                # Check TTL (default 5 minutes)
                if datetime.now() - timestamp < timedelta(minutes=5):
                    return response
                else:
                    del self._cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: ResponseT) -> None:
        """Cache response with timestamp."""
        with self._cache_lock:
            self._cache[cache_key] = (response, datetime.now())
            
            # Cleanup old entries (keep max 100)
            if len(self._cache) > 100:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
    
    def _update_average_time(self) -> None:
        """Update average processing time."""
        if self._processing_times:
            self._metrics.average_processing_time = sum(self._processing_times) / len(self._processing_times)
    
    def get_metrics(self) -> ChainMetrics:
        """Get handler metrics."""
        return self._metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics = ChainMetrics()
        self._processing_times.clear()


class OptimizedChain(Generic[RequestT, ResponseT]):
    """
    Highly optimized chain implementation with advanced features.
    """
    
    def __init__(self, max_concurrent: int = 10):
        self._handlers: List[AsyncHandler] = []
        self._handler_map: Dict[str, AsyncHandler] = {}
        self._global_metrics = ChainMetrics()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._request_queue = asyncio.Queue()
        self._circuit_breaker = CircuitBreaker()
        self._middleware: List[Callable] = []
        self._logger = logging.getLogger(__name__)
    
    def add_handler(self, handler: AsyncHandler) -> 'OptimizedChain':
        """Add handler to the chain."""
        if self._handlers:
            self._handlers[-1].set_next(handler)
        
        self._handlers.append(handler)
        self._handler_map[handler.name] = handler
        return self
    
    def add_middleware(self, middleware: Callable) -> 'OptimizedChain':
        """Add middleware for request preprocessing."""
        self._middleware.append(middleware)
        return self
    
    async def process_request(self, request: RequestT) -> ProcessingResult[ResponseT]:
        """
        Process request with full optimization and monitoring.
        """
        async with self._semaphore:  # Limit concurrency
            
            # Apply middleware
            for middleware in self._middleware:
                request = await middleware(request) if asyncio.iscoroutinefunction(middleware) else middleware(request)
            
            # Check circuit breaker
            if self._circuit_breaker.is_open():
                result = ProcessingResult[ResponseT]()
                result.status = HandlerStatus.FAILED
                result.error = Exception("Circuit breaker is open")
                return result
            
            start_time = time.time()
            
            try:
                if not self._handlers:
                    raise ValueError("No handlers configured in chain")
                
                # Start processing from first handler
                result = await self._handlers[0].process(request)
                
                # Update circuit breaker
                if result.status == HandlerStatus.SUCCESS:
                    self._circuit_breaker.record_success()
                else:
                    self._circuit_breaker.record_failure()
                
                # Update global metrics
                self._update_global_metrics(result)
                
                return result
                
            except Exception as e:
                self._circuit_breaker.record_failure()
                self._logger.error(f"Chain processing failed: {e}")
                
                result = ProcessingResult[ResponseT]()
                result.status = HandlerStatus.FAILED
                result.error = e
                result.processing_time = time.time() - start_time
                
                self._update_global_metrics(result)
                return result
    
    async def process_batch(self, requests: List[RequestT]) -> List[ProcessingResult[ResponseT]]:
        """Process multiple requests concurrently."""
        tasks = [self.process_request(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def _update_global_metrics(self, result: ProcessingResult) -> None:
        """Update global chain metrics."""
        self._global_metrics.total_requests += 1
        
        if result.status == HandlerStatus.SUCCESS:
            self._global_metrics.successful_requests += 1
        else:
            self._global_metrics.failed_requests += 1
        
        if result.handler_name:
            self._global_metrics.handler_usage[result.handler_name] += 1
    
    def get_chain_metrics(self) -> Dict[str, Any]:
        """Get comprehensive chain metrics."""
        handler_metrics = {
            handler.name: handler.get_metrics() 
            for handler in self._handlers
        }
        
        return {
            "global_metrics": self._global_metrics,
            "handler_metrics": handler_metrics,
            "circuit_breaker_status": self._circuit_breaker.get_status(),
            "active_handlers": len(self._handlers),
            "middleware_count": len(self._middleware)
        }
    
    def optimize_chain(self) -> None:
        """Optimize chain based on usage patterns."""
        # Sort handlers by success rate and performance
        handler_stats = []
        
        for handler in self._handlers:
            metrics = handler.get_metrics()
            if metrics.total_requests > 0:
                success_rate = metrics.successful_requests / metrics.total_requests
                avg_time = metrics.average_processing_time
                usage_count = metrics.handler_usage.get(handler.name, 0)
                
                handler_stats.append((handler, success_rate, avg_time, usage_count))
        
        # Sort by success rate (desc) and then by average time (asc)
        handler_stats.sort(key=lambda x: (-x[1], x[2]))
        
        # Rebuild chain in optimized order
        optimized_handlers = [stat[0] for stat in handler_stats]
        
        # Re-link handlers
        for i, handler in enumerate(optimized_handlers):
            if i < len(optimized_handlers) - 1:
                handler.set_next(optimized_handlers[i + 1])
            else:
                handler.set_next(None)
        
        self._handlers = optimized_handlers
        self._logger.info("Chain optimized based on performance metrics")


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, 
                 timeout: timedelta = timedelta(minutes=1)):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self.state == 'OPEN':
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > self.timeout):
                self.state = 'HALF_OPEN'
                return False
            return True
        return False
    
    def record_success(self) -> None:
        """Record successful execution."""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


# Utility decorators for additional optimizations
def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for automatic retry with exponential backoff."""
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator


def memoize_async(ttl: timedelta = timedelta(minutes=5)):
    """Decorator for async function memoization."""
    
    def decorator(func):
        cache = {}
        cache_lock = asyncio.Lock()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            async with cache_lock:
                if key in cache:
                    result, timestamp = cache[key]
                    if datetime.now() - timestamp < ttl:
                        return result
                    else:
                        del cache[key]
                
                result = await func(*args, **kwargs)
                cache[key] = (result, datetime.now())
                
                # Cleanup old entries
                if len(cache) > 100:
                    oldest_key = min(cache.keys(), 
                                   key=lambda k: cache[k][1])
                    del cache[oldest_key]
                
                return result
        
        return wrapper
    return decorator


def main():
    """Demonstrate the optimized chain of responsibility pattern."""
    
    # Example implementations will be provided in the demo
    print("=== Optimized Chain of Responsibility Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Async/await support with concurrency control")
    print("✓ Generic type hints for type safety")
    print("✓ Automatic handler registration with decorators")
    print("✓ Caching and memoization")
    print("✓ Performance monitoring and metrics")
    print("✓ Circuit breaker pattern for fault tolerance")
    print("✓ Automatic chain optimization")
    print("✓ Middleware support")
    print("✓ Batch processing capabilities")
    print("✓ Retry mechanisms with exponential backoff")


if __name__ == "__main__":
    main()