"""
Iterator Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Generic iterators with full typing support
- Async iteration with __aiter__ and __anext__
- Memory-efficient generators and yield patterns
- Parallel iteration with asyncio and threading
- Lazy evaluation with deferred computation
- Iterator composition and chaining
- Performance monitoring and profiling
- Caching and memoization for expensive iterators
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Iterator, AsyncIterator, Iterable, AsyncIterable,
    Type, runtime_checkable, Tuple
)
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio
import threading
import functools
import weakref
import time
import heapq
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools

# Type variables
T = TypeVar('T')
U = TypeVar('U')
K = TypeVar('K')
V = TypeVar('V')


class IteratorState(Enum):
    """Iterator state enumeration."""
    CREATED = auto()
    ACTIVE = auto()
    EXHAUSTED = auto()
    ERROR = auto()


@dataclass
class IteratorMetrics:
    """Performance metrics for iterators."""
    items_yielded: int = 0
    total_time: float = 0.0
    average_time_per_item: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage: int = 0  # Approximate bytes
    
    def update_timing(self, item_time: float) -> None:
        """Update timing metrics."""
        self.total_time += item_time
        self.items_yielded += 1
        self.average_time_per_item = self.total_time / self.items_yielded


@runtime_checkable
class AdvancedIterator(Protocol[T]):
    """Protocol for advanced iterator features."""
    
    def __iter__(self) -> Iterator[T]:
        """Return iterator."""
        ...
    
    def __next__(self) -> T:
        """Get next item."""
        ...
    
    def peek(self) -> Optional[T]:
        """Peek at next item without consuming."""
        ...
    
    def reset(self) -> None:
        """Reset iterator to beginning."""
        ...
    
    def get_metrics(self) -> IteratorMetrics:
        """Get performance metrics."""
        ...


class OptimizedIterator(Generic[T], ABC):
    """
    Base class for optimized iterators with advanced features.
    """
    
    def __init__(self, cache_size: int = 100):
        self._state = IteratorState.CREATED
        self._metrics = IteratorMetrics()
        self._cache: deque = deque(maxlen=cache_size)
        self._peek_buffer: Optional[T] = None
        self._position = 0
        self._lock = threading.RLock()
        self._start_time = time.time()
    
    @abstractmethod
    def _next_item(self) -> T:
        """Get the next item (to be implemented by subclasses)."""
        pass
    
    @abstractmethod
    def _reset_source(self) -> None:
        """Reset the data source (to be implemented by subclasses)."""
        pass
    
    def __iter__(self) -> Iterator[T]:
        """Return iterator."""
        return self
    
    def __next__(self) -> T:
        """Get next item with monitoring."""
        with self._lock:
            if self._state == IteratorState.EXHAUSTED:
                raise StopIteration
            
            if self._state == IteratorState.ERROR:
                raise RuntimeError("Iterator is in error state")
            
            if self._peek_buffer is not None:
                # Return peeked item
                item = self._peek_buffer
                self._peek_buffer = None
                self._position += 1
                return item
            
            item_start_time = time.time()
            
            try:
                self._state = IteratorState.ACTIVE
                item = self._next_item()
                
                # Update metrics
                item_time = time.time() - item_start_time
                self._metrics.update_timing(item_time)
                
                # Cache item
                self._cache.append(item)
                
                self._position += 1
                return item
                
            except StopIteration:
                self._state = IteratorState.EXHAUSTED
                raise
            except Exception as e:
                self._state = IteratorState.ERROR
                raise RuntimeError(f"Iterator error: {e}")
    
    def peek(self) -> Optional[T]:
        """Peek at next item without consuming."""
        with self._lock:
            if self._peek_buffer is not None:
                return self._peek_buffer
            
            try:
                self._peek_buffer = self._next_item()
                return self._peek_buffer
            except StopIteration:
                return None
    
    def reset(self) -> None:
        """Reset iterator to beginning."""
        with self._lock:
            self._state = IteratorState.CREATED
            self._position = 0
            self._peek_buffer = None
            self._cache.clear()
            self._reset_source()
    
    def get_metrics(self) -> IteratorMetrics:
        """Get performance metrics."""
        return self._metrics
    
    def get_state(self) -> IteratorState:
        """Get current iterator state."""
        return self._state
    
    def get_position(self) -> int:
        """Get current position."""
        return self._position


class AsyncOptimizedIterator(Generic[T], ABC):
    """
    Async iterator with advanced features.
    """
    
    def __init__(self, cache_size: int = 100):
        self._state = IteratorState.CREATED
        self._metrics = IteratorMetrics()
        self._cache: deque = deque(maxlen=cache_size)
        self._peek_buffer: Optional[T] = None
        self._position = 0
        self._lock = asyncio.Lock()
    
    @abstractmethod
    async def _next_item(self) -> T:
        """Get the next item asynchronously."""
        pass
    
    @abstractmethod
    async def _reset_source(self) -> None:
        """Reset the data source asynchronously."""
        pass
    
    def __aiter__(self) -> AsyncIterator[T]:
        """Return async iterator."""
        return self
    
    async def __anext__(self) -> T:
        """Get next item asynchronously."""
        async with self._lock:
            if self._state == IteratorState.EXHAUSTED:
                raise StopAsyncIteration
            
            if self._peek_buffer is not None:
                item = self._peek_buffer
                self._peek_buffer = None
                self._position += 1
                return item
            
            item_start_time = time.time()
            
            try:
                self._state = IteratorState.ACTIVE
                item = await self._next_item()
                
                # Update metrics
                item_time = time.time() - item_start_time
                self._metrics.update_timing(item_time)
                
                self._position += 1
                return item
                
            except StopAsyncIteration:
                self._state = IteratorState.EXHAUSTED
                raise
    
    async def peek(self) -> Optional[T]:
        """Peek at next item without consuming."""
        async with self._lock:
            if self._peek_buffer is not None:
                return self._peek_buffer
            
            try:
                self._peek_buffer = await self._next_item()
                return self._peek_buffer
            except StopAsyncIteration:
                return None
    
    async def reset(self) -> None:
        """Reset iterator to beginning."""
        async with self._lock:
            self._state = IteratorState.CREATED
            self._position = 0
            self._peek_buffer = None
            await self._reset_source()


class LazyIterator(OptimizedIterator[T]):
    """
    Lazy iterator that defers computation until needed.
    """
    
    def __init__(self, generator_func: Callable[[], Iterator[T]], cache_size: int = 100):
        super().__init__(cache_size)
        self._generator_func = generator_func
        self._generator: Optional[Iterator[T]] = None
    
    def _next_item(self) -> T:
        """Get next item from lazy generator."""
        if self._generator is None:
            self._generator = self._generator_func()
        
        return next(self._generator)
    
    def _reset_source(self) -> None:
        """Reset lazy generator."""
        self._generator = None


class MemoizedIterator(OptimizedIterator[T]):
    """
    Iterator that memoizes expensive computations.
    """
    
    def __init__(self, source: Iterable[T], 
                 transform_func: Callable[[T], T] = None,
                 cache_size: int = 1000):
        super().__init__(cache_size)
        self._source = source
        self._source_iter: Optional[Iterator[T]] = None
        self._transform_func = transform_func or (lambda x: x)
        self._memoization_cache: Dict[Any, T] = {}
        self._cache_lock = threading.RLock()
    
    def _next_item(self) -> T:
        """Get next item with memoization."""
        if self._source_iter is None:
            self._source_iter = iter(self._source)
        
        source_item = next(self._source_iter)
        
        # Check memoization cache
        cache_key = hash(str(source_item))
        
        with self._cache_lock:
            if cache_key in self._memoization_cache:
                self._metrics.cache_hits += 1
                return self._memoization_cache[cache_key]
            
            # Compute and cache
            result = self._transform_func(source_item)
            self._memoization_cache[cache_key] = result
            self._metrics.cache_misses += 1
            
            # Limit cache size
            if len(self._memoization_cache) > 10000:
                # Remove oldest entries (simplified LRU)
                keys_to_remove = list(self._memoization_cache.keys())[:1000]
                for key in keys_to_remove:
                    del self._memoization_cache[key]
            
            return result
    
    def _reset_source(self) -> None:
        """Reset source iterator."""
        self._source_iter = None


class ParallelIterator(OptimizedIterator[T]):
    """
    Iterator that processes items in parallel.
    """
    
    def __init__(self, source: Iterable[T],
                 transform_func: Callable[[T], T],
                 max_workers: int = 4,
                 buffer_size: int = 100):
        super().__init__(buffer_size)
        self._source = source
        self._transform_func = transform_func
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._buffer: deque = deque()
        self._futures: List = []
        self._source_iter: Optional[Iterator[T]] = None
        self._buffer_lock = threading.RLock()
    
    def _next_item(self) -> T:
        """Get next item from parallel processing buffer."""
        if self._source_iter is None:
            self._source_iter = iter(self._source)
            self._fill_buffer()
        
        with self._buffer_lock:
            if not self._buffer and not self._futures:
                raise StopIteration
            
            # Wait for at least one result
            if not self._buffer and self._futures:
                self._wait_for_results()
            
            if self._buffer:
                return self._buffer.popleft()
            else:
                raise StopIteration
    
    def _fill_buffer(self) -> None:
        """Fill buffer with parallel processing tasks."""
        try:
            while len(self._futures) < self._cache.maxlen:
                item = next(self._source_iter)
                future = self._executor.submit(self._transform_func, item)
                self._futures.append(future)
        except StopIteration:
            pass
    
    def _wait_for_results(self) -> None:
        """Wait for parallel processing results."""
        if not self._futures:
            return
        
        # Wait for completed futures
        completed_futures = []
        for future in as_completed(self._futures[:10], timeout=1.0):  # Wait for up to 10 futures
            try:
                result = future.result()
                with self._buffer_lock:
                    self._buffer.append(result)
                completed_futures.append(future)
            except Exception as e:
                # Skip failed items
                completed_futures.append(future)
        
        # Remove completed futures
        for future in completed_futures:
            if future in self._futures:
                self._futures.remove(future)
        
        # Refill buffer
        self._fill_buffer()
    
    def _reset_source(self) -> None:
        """Reset parallel iterator."""
        self._source_iter = None
        with self._buffer_lock:
            self._buffer.clear()
        
        # Cancel pending futures
        for future in self._futures:
            future.cancel()
        self._futures.clear()


class ChainedIterator(OptimizedIterator[T]):
    """
    Iterator that chains multiple iterators together.
    """
    
    def __init__(self, *iterators: Iterator[T]):
        super().__init__()
        self._iterators = list(iterators)
        self._current_index = 0
        self._current_iterator: Optional[Iterator[T]] = None
    
    def _next_item(self) -> T:
        """Get next item from chained iterators."""
        while self._current_index < len(self._iterators):
            if self._current_iterator is None:
                self._current_iterator = iter(self._iterators[self._current_index])
            
            try:
                return next(self._current_iterator)
            except StopIteration:
                # Move to next iterator
                self._current_index += 1
                self._current_iterator = None
        
        raise StopIteration
    
    def _reset_source(self) -> None:
        """Reset chained iterator."""
        self._current_index = 0
        self._current_iterator = None


class FilteredIterator(OptimizedIterator[T]):
    """
    Iterator that filters items based on a predicate.
    """
    
    def __init__(self, source: Iterable[T], predicate: Callable[[T], bool]):
        super().__init__()
        self._source = source
        self._predicate = predicate
        self._source_iter: Optional[Iterator[T]] = None
    
    def _next_item(self) -> T:
        """Get next item that matches the predicate."""
        if self._source_iter is None:
            self._source_iter = iter(self._source)
        
        while True:
            item = next(self._source_iter)
            if self._predicate(item):
                return item
    
    def _reset_source(self) -> None:
        """Reset filtered iterator."""
        self._source_iter = None


class WindowedIterator(OptimizedIterator[Tuple[T, ...]]):
    """
    Iterator that yields sliding windows of items.
    """
    
    def __init__(self, source: Iterable[T], window_size: int, step: int = 1):
        super().__init__()
        self._source = source
        self._window_size = window_size
        self._step = step
        self._buffer: deque = deque(maxlen=window_size)
        self._source_iter: Optional[Iterator[T]] = None
        self._first_window = True
    
    def _next_item(self) -> Tuple[T, ...]:
        """Get next windowed items."""
        if self._source_iter is None:
            self._source_iter = iter(self._source)
        
        # Fill initial buffer
        if self._first_window:
            for _ in range(self._window_size):
                try:
                    item = next(self._source_iter)
                    self._buffer.append(item)
                except StopIteration:
                    if len(self._buffer) == 0:
                        raise StopIteration
                    break
            self._first_window = False
        else:
            # Slide window
            for _ in range(self._step):
                try:
                    item = next(self._source_iter)
                    self._buffer.append(item)
                except StopIteration:
                    raise StopIteration
        
        if len(self._buffer) < self._window_size:
            raise StopIteration
        
        return tuple(self._buffer)
    
    def _reset_source(self) -> None:
        """Reset windowed iterator."""
        self._source_iter = None
        self._buffer.clear()
        self._first_window = True


class AsyncBatchIterator(AsyncOptimizedIterator[List[T]]):
    """
    Async iterator that yields batches of items.
    """
    
    def __init__(self, source: AsyncIterable[T], batch_size: int):
        super().__init__()
        self._source = source
        self._batch_size = batch_size
        self._source_iter: Optional[AsyncIterator[T]] = None
    
    async def _next_item(self) -> List[T]:
        """Get next batch of items."""
        if self._source_iter is None:
            self._source_iter = aiter(self._source)
        
        batch = []
        try:
            for _ in range(self._batch_size):
                item = await anext(self._source_iter)
                batch.append(item)
        except StopAsyncIteration:
            if not batch:
                raise StopAsyncIteration
        
        return batch
    
    async def _reset_source(self) -> None:
        """Reset batch iterator."""
        self._source_iter = None


class IteratorComposer:
    """
    Utility class for composing complex iterators.
    """
    
    @staticmethod
    def chain(*iterators: Iterator[T]) -> ChainedIterator[T]:
        """Chain multiple iterators together."""
        return ChainedIterator(*iterators)
    
    @staticmethod
    def filter(source: Iterable[T], predicate: Callable[[T], bool]) -> FilteredIterator[T]:
        """Create filtered iterator."""
        return FilteredIterator(source, predicate)
    
    @staticmethod
    def map(source: Iterable[T], transform: Callable[[T], U]) -> MemoizedIterator[U]:
        """Create mapping iterator with memoization."""
        return MemoizedIterator(source, transform)
    
    @staticmethod
    def parallel_map(source: Iterable[T], transform: Callable[[T], U], 
                    max_workers: int = 4) -> ParallelIterator[U]:
        """Create parallel mapping iterator."""
        return ParallelIterator(source, transform, max_workers)
    
    @staticmethod
    def window(source: Iterable[T], size: int, step: int = 1) -> WindowedIterator[T]:
        """Create windowed iterator."""
        return WindowedIterator(source, size, step)
    
    @staticmethod
    def lazy(generator_func: Callable[[], Iterator[T]]) -> LazyIterator[T]:
        """Create lazy iterator."""
        return LazyIterator(generator_func)
    
    @staticmethod
    def pipeline(*operations: Callable[[Iterator], Iterator]) -> Callable[[Iterator[T]], Iterator]:
        """Create iterator pipeline."""
        def apply_pipeline(source: Iterator[T]) -> Iterator:
            result = source
            for operation in operations:
                result = operation(result)
            return result
        return apply_pipeline


class PerformanceMonitor:
    """
    Monitor for tracking iterator performance across the application.
    """
    
    def __init__(self):
        self._iterator_stats: Dict[str, List[IteratorMetrics]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def register_iterator(self, name: str, iterator: OptimizedIterator) -> None:
        """Register an iterator for monitoring."""
        with self._lock:
            metrics = iterator.get_metrics()
            self._iterator_stats[name].append(metrics)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        with self._lock:
            report = {}
            
            for name, metrics_list in self._iterator_stats.items():
                if not metrics_list:
                    continue
                
                total_items = sum(m.items_yielded for m in metrics_list)
                total_time = sum(m.total_time for m in metrics_list)
                total_cache_hits = sum(m.cache_hits for m in metrics_list)
                total_cache_misses = sum(m.cache_misses for m in metrics_list)
                
                report[name] = {
                    "total_items_yielded": total_items,
                    "total_time": total_time,
                    "average_throughput": total_items / max(total_time, 0.001),
                    "cache_hit_ratio": total_cache_hits / max(total_cache_hits + total_cache_misses, 1),
                    "instance_count": len(metrics_list)
                }
            
            return report
    
    def clear_stats(self) -> None:
        """Clear all statistics."""
        with self._lock:
            self._iterator_stats.clear()


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitored_iterator(name: str):
    """Decorator for automatic iterator performance monitoring."""
    
    def decorator(iterator_class):
        class MonitoredIterator(iterator_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                performance_monitor.register_iterator(name, self)
        
        return MonitoredIterator
    
    return decorator


def main():
    """Demonstrate the optimized iterator pattern."""
    print("=== Optimized Iterator Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Generic iterators with full typing support")
    print("✓ Async iteration with __aiter__ and __anext__")
    print("✓ Memory-efficient generators and lazy evaluation")
    print("✓ Parallel iteration with threading and asyncio")
    print("✓ Iterator composition and chaining utilities")
    print("✓ Performance monitoring and profiling")
    print("✓ Caching and memoization for expensive operations")
    print("✓ Advanced features: peek, reset, windowing, filtering")
    print("✓ Thread-safe concurrent iteration")
    print("✓ Comprehensive performance analytics")
    print("✓ Pipeline composition for complex transformations")
    print("✓ Global performance monitoring system")


if __name__ == "__main__":
    main()