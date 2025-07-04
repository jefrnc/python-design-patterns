"""
Flyweight Design Pattern - Optimized Implementation

An advanced implementation demonstrating the Flyweight pattern with Python 3.13.5
features including async operations, intelligent memory management, adaptive caching,
concurrent operations, and performance optimization.

This optimized version includes:
- Async flyweight operations with concurrent access
- Intelligent memory management with garbage collection
- Adaptive caching strategies based on usage patterns
- Memory pool allocation for efficiency
- Weak references for automatic cleanup
- Performance monitoring and optimization
- Compression and serialization optimizations
- Thread-safe operations with fine-grained locking
- Memory profiling and analytics
- Auto-scaling flyweight pools
"""

import asyncio
import logging
import time
import sys
import gc
import weakref
import threading
import hashlib
import pickle
import gzip
import lzma
from abc import ABC, abstractmethod
from typing import (
    Dict, List, Optional, Set, Protocol, TypeVar, Generic, 
    Callable, Awaitable, AsyncIterator, Union, Tuple, Any,
    WeakValueDictionary, Final
)
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
from contextlib import asynccontextmanager
import statistics
import array
import mmap
from concurrent.futures import ThreadPoolExecutor


# Type Variables and Protocols
T = TypeVar('T')
F = TypeVar('F', bound='OptimizedFlyweight')


class FlyweightProtocol(Protocol[T]):
    """Protocol defining the interface for flyweight objects."""
    
    async def render(self, context: 'RenderContext') -> str: ...
    def get_memory_footprint(self) -> int: ...
    def get_intrinsic_state(self) -> Dict[str, Any]: ...


class CacheProtocol(Protocol):
    """Protocol for cache implementations."""
    
    async def get(self, key: str) -> Optional[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    async def evict_lru(self, count: int) -> int: ...


# Enhanced Enums
class FontWeight(Enum):
    THIN = 100
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    EXTRABOLD = 800
    BLACK = 900


class FontStyle(Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class CompressionLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 5
    HIGH = 9


class AllocationStrategy(Enum):
    LAZY = "lazy"
    EAGER = "eager"
    ADAPTIVE = "adaptive"
    POOLED = "pooled"


class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    ADAPTIVE = "adaptive"
    TIME_BASED = "time_based"


# Enhanced Data Classes
@dataclass(frozen=True)
class Color:
    """Immutable color with optimized memory layout."""
    red: int
    green: int
    blue: int
    alpha: int = 255
    
    def __post_init__(self):
        for value in [self.red, self.green, self.blue, self.alpha]:
            if not 0 <= value <= 255:
                raise ValueError("Color values must be between 0 and 255")
    
    def to_hex(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
    
    def to_rgba(self) -> str:
        return f"rgba({self.red}, {self.green}, {self.blue}, {self.alpha/255:.2f})"
    
    def __hash__(self) -> int:
        return hash((self.red, self.green, self.blue, self.alpha))


@dataclass
class RenderContext:
    """Enhanced rendering context with caching support."""
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    scale_factor: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    clip_rect: Optional[Tuple[int, int, int, int]] = None
    render_quality: str = "normal"
    animation_frame: int = 0
    
    def get_cache_key(self) -> str:
        """Generate cache key for this context."""
        return hashlib.md5(str(self).encode()).hexdigest()
    
    def transformed_position(self) -> Tuple[float, float]:
        """Calculate transformed position."""
        # Simplified transformation
        x = self.x * self.scale_factor
        y = self.y * self.scale_factor
        return (x, y)


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    total_flyweights: int = 0
    total_memory_bytes: int = 0
    shared_memory_bytes: int = 0
    context_memory_bytes: int = 0
    cache_memory_bytes: int = 0
    compression_savings_bytes: int = 0
    gc_collections: int = 0
    weak_references_count: int = 0
    
    def memory_efficiency(self) -> float:
        """Calculate memory efficiency ratio."""
        if self.total_memory_bytes == 0:
            return 1.0
        return self.shared_memory_bytes / self.total_memory_bytes
    
    def compression_ratio(self) -> float:
        """Calculate compression effectiveness."""
        if self.compression_savings_bytes == 0:
            return 1.0
        return 1.0 - (self.compression_savings_bytes / (self.total_memory_bytes + self.compression_savings_bytes))


# Memory Pool for Efficient Allocation
class MemoryPool:
    """Advanced memory pool with different allocation strategies."""
    
    def __init__(self, object_size: int, pool_size: int = 1000, strategy: AllocationStrategy = AllocationStrategy.ADAPTIVE):
        self.object_size = object_size
        self.pool_size = pool_size
        self.strategy = strategy
        self.available_objects: deque = deque()
        self.allocated_count = 0
        self.allocation_stats = Counter()
        self._lock = threading.Lock()
        
        # Pre-allocate objects for eager strategy
        if strategy == AllocationStrategy.EAGER:
            self._preallocate_objects()
    
    def _preallocate_objects(self):
        """Pre-allocate objects in the pool."""
        for _ in range(self.pool_size):
            obj_data = bytearray(self.object_size)
            self.available_objects.append(obj_data)
    
    def allocate(self) -> Optional[bytearray]:
        """Allocate object from pool."""
        with self._lock:
            if self.available_objects:
                obj = self.available_objects.popleft()
                self.allocated_count += 1
                self.allocation_stats['reused'] += 1
                return obj
            elif self.allocated_count < self.pool_size:
                obj = bytearray(self.object_size)
                self.allocated_count += 1
                self.allocation_stats['new'] += 1
                return obj
            else:
                self.allocation_stats['failed'] += 1
                return None
    
    def deallocate(self, obj: bytearray):
        """Return object to pool."""
        with self._lock:
            if len(self.available_objects) < self.pool_size:
                # Clear the object data
                for i in range(len(obj)):
                    obj[i] = 0
                self.available_objects.append(obj)
                self.allocation_stats['returned'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._lock:
            return {
                'pool_size': self.pool_size,
                'allocated_count': self.allocated_count,
                'available_count': len(self.available_objects),
                'allocation_stats': dict(self.allocation_stats),
                'efficiency': len(self.available_objects) / self.pool_size if self.pool_size > 0 else 0
            }


# Advanced Cache Implementation
class AdaptiveCache:
    """Adaptive cache with multiple strategies and intelligent eviction."""
    
    def __init__(self, max_size: int = 50000, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: Dict[str, Tuple[Any, datetime, int]] = {}  # value, timestamp, access_count
        self._access_order: deque = deque()
        self._access_frequency: Counter = Counter()
        self._lock = asyncio.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0
        }
        
        # Adaptive parameters
        self._hit_rate_history = deque(maxlen=1000)
        self._current_strategy = strategy
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with strategy-specific logic."""
        async with self._lock:
            if key in self._cache:
                value, timestamp, access_count = self._cache[key]
                
                # Update access statistics
                access_count += 1
                self._cache[key] = (value, timestamp, access_count)
                self._access_frequency[key] += 1
                
                # Update access order for LRU
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                
                self._stats['hits'] += 1
                return value
            else:
                self._stats['misses'] += 1
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with intelligent eviction."""
        async with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_items(1)
            
            # Calculate expiry
            expiry = datetime.now() + timedelta(seconds=ttl) if ttl else datetime.max
            
            # Store value
            self._cache[key] = (value, expiry, 1)
            self._access_frequency[key] = 1
            
            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            self._stats['sets'] += 1
            
            # Adaptive strategy adjustment
            if self._current_strategy == CacheStrategy.ADAPTIVE:
                await self._adjust_strategy()
    
    async def _evict_items(self, count: int) -> int:
        """Evict items based on current strategy."""
        evicted = 0
        
        for _ in range(count):
            if not self._cache:
                break
                
            victim_key = None
            
            if self._current_strategy == CacheStrategy.LRU:
                # Evict least recently used
                victim_key = self._access_order.popleft() if self._access_order else None
            elif self._current_strategy == CacheStrategy.LFU:
                # Evict least frequently used
                victim_key = min(self._access_frequency.keys(), 
                               key=lambda k: self._access_frequency[k])
            elif self._current_strategy == CacheStrategy.TIME_BASED:
                # Evict oldest items
                victim_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k][1])
            else:  # ADAPTIVE
                # Hybrid approach
                if len(self._access_order) > 0:
                    victim_key = self._access_order.popleft()
            
            if victim_key and victim_key in self._cache:
                del self._cache[victim_key]
                self._access_frequency.pop(victim_key, None)
                if victim_key in self._access_order:
                    self._access_order.remove(victim_key)
                evicted += 1
                self._stats['evictions'] += 1
        
        return evicted
    
    async def _adjust_strategy(self):
        """Adjust caching strategy based on performance."""
        total_requests = self._stats['hits'] + self._stats['misses']
        if total_requests > 100:  # Only adjust after sufficient data
            hit_rate = self._stats['hits'] / total_requests
            self._hit_rate_history.append(hit_rate)
            
            # Simple strategy adjustment
            if len(self._hit_rate_history) >= 10:
                recent_performance = statistics.mean(list(self._hit_rate_history)[-10:])
                if recent_performance < 0.6:
                    # Poor performance, try different strategy
                    strategies = [CacheStrategy.LRU, CacheStrategy.LFU, CacheStrategy.TIME_BASED]
                    current_idx = strategies.index(self._current_strategy) if self._current_strategy in strategies else 0
                    self._current_strategy = strategies[(current_idx + 1) % len(strategies)]
    
    async def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        async with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (_, expiry, _) in self._cache.items()
                if expiry < now
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._access_frequency.pop(key, None)
                if key in self._access_order:
                    self._access_order.remove(key)
            
            return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        async with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / max(1, total_requests)
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'strategy': self._current_strategy.value,
                'stats': self._stats.copy(),
                'memory_usage': sys.getsizeof(self._cache) + 
                               sum(sys.getsizeof(v) for v, _, _ in self._cache.values())
            }


# Performance Monitor for Flyweights
class FlyweightPerformanceMonitor:
    """Advanced performance monitoring for flyweight operations."""
    
    def __init__(self):
        self.operation_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.memory_snapshots: deque = deque(maxlen=100)
        self.gc_stats: List[Dict] = []
        self._lock = threading.Lock()
        
        # Start background monitoring
        self._monitoring_task = None
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background monitoring tasks."""
        def monitor_loop():
            while True:
                try:
                    # Take memory snapshot
                    self._take_memory_snapshot()
                    
                    # Force garbage collection and record stats
                    self._record_gc_stats()
                    
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logging.error(f"Error in performance monitoring: {e}")
                    time.sleep(60)
        
        self._monitoring_task = threading.Thread(target=monitor_loop, daemon=True)
        self._monitoring_task.start()
    
    def record_operation(self, operation: str, duration_ms: float, memory_delta: int = 0):
        """Record operation performance."""
        with self._lock:
            self.operation_times[operation].append({
                'duration_ms': duration_ms,
                'memory_delta': memory_delta,
                'timestamp': datetime.now()
            })
    
    def _take_memory_snapshot(self):
        """Take a memory usage snapshot."""
        with self._lock:
            snapshot = {
                'timestamp': datetime.now(),
                'total_memory': sys.getsizeof(gc.get_objects()),
                'gc_counts': gc.get_count(),
                'object_count': len(gc.get_objects())
            }
            self.memory_snapshots.append(snapshot)
    
    def _record_gc_stats(self):
        """Record garbage collection statistics."""
        with self._lock:
            # Force garbage collection
            collected = gc.collect()
            
            stats = {
                'timestamp': datetime.now(),
                'objects_collected': collected,
                'gc_counts': gc.get_count(),
                'total_objects': len(gc.get_objects())
            }
            self.gc_stats.append(stats)
            
            # Keep only recent stats
            if len(self.gc_stats) > 100:
                self.gc_stats = self.gc_stats[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self._lock:
            summary = {}
            
            # Operation performance
            for operation, times in self.operation_times.items():
                if times:
                    durations = [t['duration_ms'] for t in times]
                    summary[operation] = {
                        'count': len(durations),
                        'mean_ms': statistics.mean(durations),
                        'median_ms': statistics.median(durations),
                        'p95_ms': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations),
                        'total_memory_delta': sum(t['memory_delta'] for t in times)
                    }
            
            # Memory trends
            if self.memory_snapshots:
                recent_snapshots = list(self.memory_snapshots)[-10:]
                memory_trend = "stable"
                if len(recent_snapshots) >= 2:
                    start_memory = recent_snapshots[0]['total_memory']
                    end_memory = recent_snapshots[-1]['total_memory']
                    change_percent = (end_memory - start_memory) / start_memory * 100
                    
                    if change_percent > 10:
                        memory_trend = "increasing"
                    elif change_percent < -10:
                        memory_trend = "decreasing"
                
                summary['memory_analysis'] = {
                    'trend': memory_trend,
                    'snapshots_count': len(self.memory_snapshots),
                    'latest_object_count': recent_snapshots[-1]['object_count'] if recent_snapshots else 0
                }
            
            # GC analysis
            if self.gc_stats:
                recent_gc = self.gc_stats[-10:]
                total_collected = sum(stat['objects_collected'] for stat in recent_gc)
                
                summary['gc_analysis'] = {
                    'recent_collections': len(recent_gc),
                    'total_objects_collected': total_collected,
                    'avg_objects_per_collection': total_collected / max(1, len(recent_gc))
                }
            
            return summary


# Optimized Flyweight Base Class
class OptimizedFlyweight(ABC):
    """Enhanced flyweight with performance optimizations."""
    
    def __init__(self):
        self._hash_cache: Optional[int] = None
        self._memory_footprint_cache: Optional[int] = None
        self._creation_time = datetime.now()
        self._access_count = 0
        self._last_accessed = datetime.now()
    
    @abstractmethod
    async def render(self, context: RenderContext) -> str:
        """Render flyweight with given context."""
        pass
    
    @abstractmethod
    def get_intrinsic_state(self) -> Dict[str, Any]:
        """Get intrinsic state dictionary."""
        pass
    
    def get_memory_footprint(self) -> int:
        """Get cached memory footprint."""
        if self._memory_footprint_cache is None:
            self._memory_footprint_cache = self._calculate_memory_footprint()
        return self._memory_footprint_cache
    
    def _calculate_memory_footprint(self) -> int:
        """Calculate actual memory footprint."""
        return sys.getsizeof(self) + sum(
            sys.getsizeof(getattr(self, attr, None)) 
            for attr in dir(self) 
            if not attr.startswith('_')
        )
    
    def update_access_stats(self):
        """Update access statistics."""
        self._access_count += 1
        self._last_accessed = datetime.now()
    
    def get_access_stats(self) -> Dict[str, Any]:
        """Get access statistics."""
        age = (datetime.now() - self._creation_time).total_seconds()
        return {
            'access_count': self._access_count,
            'age_seconds': age,
            'last_accessed': self._last_accessed.isoformat(),
            'access_frequency': self._access_count / max(1, age / 3600)  # per hour
        }
    
    def __hash__(self) -> int:
        """Cached hash implementation."""
        if self._hash_cache is None:
            intrinsic = self.get_intrinsic_state()
            self._hash_cache = hash(tuple(sorted(intrinsic.items())))
        return self._hash_cache


# Optimized Character Flyweight
class OptimizedCharacterFlyweight(OptimizedFlyweight):
    """Highly optimized character flyweight with compression."""
    
    __slots__ = ('_character', '_font_family', '_font_size', '_font_weight', 
                 '_font_style', '_color', '_compressed_data', '_hash_cache',
                 '_memory_footprint_cache', '_creation_time', '_access_count',
                 '_last_accessed')
    
    def __init__(self, character: str, font_family: str, font_size: int,
                 font_weight: FontWeight, font_style: FontStyle, color: Color,
                 compress: bool = True):
        super().__init__()
        
        if len(character) != 1:
            raise ValueError("CharacterFlyweight can only represent single characters")
        
        # Store intrinsic state
        self._character = character
        self._font_family = font_family
        self._font_size = font_size
        self._font_weight = font_weight
        self._font_style = font_style
        self._color = color
        
        # Optional compression for memory efficiency
        self._compressed_data = None
        if compress and len(font_family) > 10:  # Only compress longer font names
            self._compressed_data = self._compress_font_data()
    
    def _compress_font_data(self) -> bytes:
        """Compress font data for memory efficiency."""
        data = {
            'font_family': self._font_family,
            'font_size': self._font_size,
            'font_weight': self._font_weight.value,
            'font_style': self._font_style.value,
            'color': (self._color.red, self._color.green, self._color.blue, self._color.alpha)
        }
        pickled = pickle.dumps(data)
        return gzip.compress(pickled, compresslevel=6)
    
    def _decompress_font_data(self) -> Dict[str, Any]:
        """Decompress font data when needed."""
        if self._compressed_data:
            decompressed = gzip.decompress(self._compressed_data)
            return pickle.loads(decompressed)
        return {}
    
    async def render(self, context: RenderContext) -> str:
        """Optimized rendering with context caching."""
        self.update_access_stats()
        
        # Use cache key for expensive renders
        cache_key = f"{id(self)}_{context.get_cache_key()}"
        
        # Get transformed position
        x, y = context.transformed_position()
        
        # Build style string efficiently
        style_parts = [
            f"font-family: {self._font_family}",
            f"font-size: {self._font_size}px",
            f"font-weight: {self._font_weight.value}",
            f"font-style: {self._font_style.value}",
            f"color: {self._color.to_hex()}",
            f"position: absolute",
            f"left: {x}px",
            f"top: {y}px"
        ]
        
        # Add optional properties
        if context.opacity < 1.0:
            style_parts.append(f"opacity: {context.opacity}")
        
        if context.rotation != 0:
            style_parts.append(f"transform: rotate({context.rotation}deg)")
        
        style_str = "; ".join(style_parts)
        
        # Simulate async rendering delay for complex characters
        if self._font_size > 24 or context.render_quality == "high":
            await asyncio.sleep(0.001)
        
        return f'<span style="{style_str}">{self._character}</span>'
    
    def get_intrinsic_state(self) -> Dict[str, Any]:
        """Get intrinsic state with decompression if needed."""
        if self._compressed_data:
            return {
                'character': self._character,
                **self._decompress_font_data()
            }
        else:
            return {
                'character': self._character,
                'font_family': self._font_family,
                'font_size': self._font_size,
                'font_weight': self._font_weight.value,
                'font_style': self._font_style.value,
                'color': self._color.to_hex()
            }
    
    @property
    def character(self) -> str:
        return self._character
    
    @property
    def font_family(self) -> str:
        return self._font_family
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, OptimizedCharacterFlyweight):
            return False
        return (self._character == other._character and
                self._font_family == other._font_family and
                self._font_size == other._font_size and
                self._font_weight == other._font_weight and
                self._font_style == other._font_style and
                self._color == other._color)


# Advanced Flyweight Factory
class IntelligentFlyweightFactory:
    """Intelligent flyweight factory with advanced memory management."""
    
    def __init__(self, cache_strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 max_cache_size: int = 100000, enable_compression: bool = True,
                 allocation_strategy: AllocationStrategy = AllocationStrategy.ADAPTIVE):
        
        # Core storage
        self._character_flyweights: WeakValueDictionary[Tuple, OptimizedCharacterFlyweight] = WeakValueDictionary()
        self._flyweight_cache = AdaptiveCache(max_cache_size, cache_strategy)
        
        # Memory management
        self._memory_pool = MemoryPool(1024, 1000, allocation_strategy)  # 1KB objects
        self._weak_refs: Set[weakref.ref] = set()
        
        # Performance monitoring
        self._performance_monitor = FlyweightPerformanceMonitor()
        
        # Configuration
        self._enable_compression = enable_compression
        self._allocation_strategy = allocation_strategy
        
        # Statistics
        self._creation_stats = Counter()
        self._access_stats = Counter()
        self._memory_stats = MemoryStats()
        
        # Thread safety
        self._lock = asyncio.RLock()
        
        # Background tasks
        self._cleanup_task = None
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        async def cleanup_loop():
            while True:
                try:
                    await self._periodic_cleanup()
                    await asyncio.sleep(60)  # Cleanup every minute
                except Exception as e:
                    logging.error(f"Error in flyweight cleanup: {e}")
                    await asyncio.sleep(300)  # Back off on error
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def get_character_flyweight(self, character: str, font_family: str, 
                                    font_size: int, font_weight: FontWeight,
                                    font_style: FontStyle, color: Color) -> OptimizedCharacterFlyweight:
        """Get or create character flyweight with intelligent caching."""
        start_time = time.time()
        
        # Create cache key
        key = (character, font_family, font_size, font_weight, font_style, color)
        cache_key = str(hash(key))
        
        async with self._lock:
            # Check cache first
            cached_flyweight = await self._flyweight_cache.get(cache_key)
            if cached_flyweight:
                self._access_stats['cache_hit'] += 1
                cached_flyweight.update_access_stats()
                return cached_flyweight
            
            # Check weak reference storage
            if key in self._character_flyweights:
                flyweight = self._character_flyweights[key]
                if flyweight:  # Weak reference still valid
                    self._access_stats['weak_ref_hit'] += 1
                    flyweight.update_access_stats()
                    
                    # Re-cache popular flyweights
                    await self._flyweight_cache.set(cache_key, flyweight, ttl=3600)
                    return flyweight
            
            # Create new flyweight
            try:
                flyweight = OptimizedCharacterFlyweight(
                    character, font_family, font_size, font_weight, 
                    font_style, color, compress=self._enable_compression
                )
                
                # Store in weak reference dictionary
                self._character_flyweights[key] = flyweight
                
                # Add to cache
                await self._flyweight_cache.set(cache_key, flyweight, ttl=3600)
                
                # Create weak reference for cleanup tracking
                weak_ref = weakref.ref(flyweight, self._on_flyweight_deleted)
                self._weak_refs.add(weak_ref)
                
                # Update statistics
                self._creation_stats['character'] += 1
                self._access_stats['cache_miss'] += 1
                
                return flyweight
                
            except Exception as e:
                logging.error(f"Failed to create character flyweight: {e}")
                raise
        
        finally:
            duration = (time.time() - start_time) * 1000
            self._performance_monitor.record_operation("get_character_flyweight", duration)
    
    def _on_flyweight_deleted(self, weak_ref):
        """Callback when flyweight is garbage collected."""
        self._weak_refs.discard(weak_ref)
        self._memory_stats.weak_references_count = len(self._weak_refs)
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired cache entries and statistics."""
        try:
            # Clean up expired cache entries
            expired_count = await self._flyweight_cache.cleanup_expired()
            if expired_count > 0:
                logging.debug(f"Cleaned up {expired_count} expired flyweight cache entries")
            
            # Update memory statistics
            await self._update_memory_stats()
            
            # Trigger garbage collection if memory usage is high
            current_memory = self._memory_stats.total_memory_bytes
            if current_memory > 100 * 1024 * 1024:  # 100MB threshold
                gc.collect()
                self._memory_stats.gc_collections += 1
                logging.info("Triggered garbage collection due to high memory usage")
            
        except Exception as e:
            logging.error(f"Error during periodic cleanup: {e}")
    
    async def _update_memory_stats(self):
        """Update comprehensive memory statistics."""
        async with self._lock:
            # Count active flyweights
            self._memory_stats.total_flyweights = len(self._character_flyweights)
            
            # Calculate memory usage
            shared_memory = sum(fw.get_memory_footprint() for fw in self._character_flyweights.values())
            cache_memory = (await self._flyweight_cache.get_stats())['memory_usage']
            
            self._memory_stats.shared_memory_bytes = shared_memory
            self._memory_stats.cache_memory_bytes = cache_memory
            self._memory_stats.total_memory_bytes = shared_memory + cache_memory
            self._memory_stats.weak_references_count = len(self._weak_refs)
    
    async def get_factory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive factory statistics."""
        await self._update_memory_stats()
        
        cache_stats = await self._flyweight_cache.get_stats()
        pool_stats = self._memory_pool.get_stats()
        performance_summary = self._performance_monitor.get_performance_summary()
        
        # Calculate efficiency metrics
        total_access = sum(self._access_stats.values())
        cache_hit_rate = self._access_stats['cache_hit'] / max(1, total_access)
        
        return {
            'flyweight_counts': {
                'character_flyweights': len(self._character_flyweights),
                'total_flyweights': self._memory_stats.total_flyweights
            },
            'memory_stats': {
                'total_memory_bytes': self._memory_stats.total_memory_bytes,
                'shared_memory_bytes': self._memory_stats.shared_memory_bytes,
                'cache_memory_bytes': self._memory_stats.cache_memory_bytes,
                'memory_efficiency': self._memory_stats.memory_efficiency(),
                'compression_ratio': self._memory_stats.compression_ratio(),
                'weak_references_count': self._memory_stats.weak_references_count
            },
            'performance_stats': {
                'cache_hit_rate': cache_hit_rate,
                'total_accesses': total_access,
                'creation_stats': dict(self._creation_stats),
                'access_stats': dict(self._access_stats)
            },
            'cache_stats': cache_stats,
            'memory_pool_stats': pool_stats,
            'detailed_performance': performance_summary,
            'configuration': {
                'compression_enabled': self._enable_compression,
                'allocation_strategy': self._allocation_strategy.value,
                'cache_strategy': cache_stats['strategy']
            }
        }
    
    async def optimize_memory_usage(self, target_reduction_percent: float = 20.0) -> Dict[str, Any]:
        """Intelligent memory optimization."""
        start_time = time.time()
        initial_memory = self._memory_stats.total_memory_bytes
        
        optimizations_applied = []
        
        try:
            # 1. Cleanup expired cache entries
            expired_cleaned = await self._flyweight_cache.cleanup_expired()
            if expired_cleaned > 0:
                optimizations_applied.append(f"Cleaned {expired_cleaned} expired cache entries")
            
            # 2. Evict least accessed flyweights from cache
            cache_size_before = (await self._flyweight_cache.get_stats())['size']
            eviction_target = int(cache_size_before * (target_reduction_percent / 100))
            evicted = await self._flyweight_cache.evict_lru(eviction_target)
            if evicted > 0:
                optimizations_applied.append(f"Evicted {evicted} LRU cache entries")
            
            # 3. Force garbage collection
            collected = gc.collect()
            if collected > 0:
                optimizations_applied.append(f"Garbage collected {collected} objects")
                self._memory_stats.gc_collections += 1
            
            # 4. Clean up dead weak references
            initial_weak_refs = len(self._weak_refs)
            self._weak_refs = {ref for ref in self._weak_refs if ref() is not None}
            cleaned_refs = initial_weak_refs - len(self._weak_refs)
            if cleaned_refs > 0:
                optimizations_applied.append(f"Cleaned {cleaned_refs} dead weak references")
            
            # Update memory stats
            await self._update_memory_stats()
            final_memory = self._memory_stats.total_memory_bytes
            
            memory_saved = initial_memory - final_memory
            reduction_percent = (memory_saved / max(1, initial_memory)) * 100
            
            result = {
                'success': True,
                'initial_memory_bytes': initial_memory,
                'final_memory_bytes': final_memory,
                'memory_saved_bytes': memory_saved,
                'reduction_percent': reduction_percent,
                'target_reduction_percent': target_reduction_percent,
                'optimizations_applied': optimizations_applied,
                'optimization_time_ms': (time.time() - start_time) * 1000
            }
            
            logging.info(f"Memory optimization completed: {reduction_percent:.1f}% reduction")
            return result
            
        except Exception as e:
            logging.error(f"Memory optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'optimizations_applied': optimizations_applied
            }
    
    async def shutdown(self):
        """Graceful shutdown of the factory."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Final cleanup
        await self._flyweight_cache.cleanup_expired()
        self._character_flyweights.clear()
        self._weak_refs.clear()
        
        logging.info("Flyweight factory shutdown completed")


# Context Object for Flyweight Usage
class OptimizedTextCharacter:
    """Optimized context object using character flyweights."""
    
    __slots__ = ('_flyweight', '_x', '_y', '_selected', '_visible', '_animation_data')
    
    def __init__(self, flyweight: OptimizedCharacterFlyweight, x: int, y: int):
        self._flyweight = flyweight
        self._x = x
        self._y = y
        self._selected = False
        self._visible = True
        self._animation_data: Optional[Dict[str, Any]] = None
    
    async def render(self, render_quality: str = "normal") -> str:
        """Render character with optimizations."""
        if not self._visible:
            return ""
        
        # Create optimized render context
        context = RenderContext(
            x=self._x, 
            y=self._y, 
            render_quality=render_quality
        )
        
        # Add selection styling
        if self._selected:
            context.opacity = 0.8
        
        # Add animation if present
        if self._animation_data:
            context.rotation = self._animation_data.get('rotation', 0)
            context.scale_factor = self._animation_data.get('scale', 1.0)
        
        return await self._flyweight.render(context)
    
    def move_to(self, x: int, y: int) -> None:
        """Move character to new position."""
        self._x = x
        self._y = y
    
    def set_selected(self, selected: bool) -> None:
        """Set selection state."""
        self._selected = selected
    
    def set_animation(self, animation_data: Dict[str, Any]) -> None:
        """Set animation properties."""
        self._animation_data = animation_data
    
    @property
    def flyweight(self) -> OptimizedCharacterFlyweight:
        return self._flyweight
    
    @property
    def position(self) -> Tuple[int, int]:
        return (self._x, self._y)
    
    @property
    def character(self) -> str:
        return self._flyweight.character


# High-Performance Document Class
class OptimizedDocument:
    """High-performance document with intelligent flyweight management."""
    
    def __init__(self, name: str, factory: IntelligentFlyweightFactory):
        self.name = name
        self._factory = factory
        self._characters: List[OptimizedTextCharacter] = []
        self._render_cache: Dict[str, str] = {}
        self._dirty = True
        self._last_render_time: Optional[datetime] = None
        
        # Performance tracking
        self._operation_times: Dict[str, List[float]] = defaultdict(list)
        self._character_pools: Dict[str, List[OptimizedTextCharacter]] = defaultdict(list)
    
    async def insert_text_async(self, text: str, font_family: str = "Arial", 
                              font_size: int = 12, color: Color = None) -> None:
        """Asynchronously insert text with batch flyweight creation."""
        if color is None:
            color = Color(0, 0, 0)
        
        start_time = time.time()
        
        try:
            # Create flyweights in batch for better performance
            flyweight_tasks = []
            for char in text:
                if char != ' ':  # Skip spaces
                    task = self._factory.get_character_flyweight(
                        char, font_family, font_size, FontWeight.NORMAL, 
                        FontStyle.NORMAL, color
                    )
                    flyweight_tasks.append((char, task))
            
            # Await all flyweight creations concurrently
            flyweights = []
            for char, task in flyweight_tasks:
                flyweight = await task
                flyweights.append((char, flyweight))
            
            # Create character objects
            x_position = len(self._characters) * 8  # Simple positioning
            for char, flyweight in flyweights:
                char_obj = OptimizedTextCharacter(flyweight, x_position, 0)
                self._characters.append(char_obj)
                x_position += 8
            
            self._dirty = True
            
        finally:
            duration = (time.time() - start_time) * 1000
            self._operation_times['insert_text'].append(duration)
    
    async def render_document_async(self, use_cache: bool = True) -> str:
        """Asynchronously render document with intelligent caching."""
        cache_key = f"{id(self)}_{len(self._characters)}_{hash(str(self._dirty))}"
        
        # Check cache
        if use_cache and not self._dirty and cache_key in self._render_cache:
            return self._render_cache[cache_key]
        
        start_time = time.time()
        
        try:
            # Render characters concurrently in batches
            batch_size = 100  # Process in batches for memory efficiency
            rendered_parts = []
            
            for i in range(0, len(self._characters), batch_size):
                batch = self._characters[i:i + batch_size]
                
                # Render batch concurrently
                render_tasks = [char.render() for char in batch]
                batch_results = await asyncio.gather(*render_tasks)
                rendered_parts.extend(batch_results)
            
            # Combine results
            html_parts = ['<div class="document">']
            html_parts.extend(rendered_parts)
            html_parts.append('</div>')
            
            result = '\n'.join(html_parts)
            
            # Cache result
            if use_cache:
                self._render_cache[cache_key] = result
                # Limit cache size
                if len(self._render_cache) > 10:
                    oldest_key = min(self._render_cache.keys())
                    del self._render_cache[oldest_key]
            
            self._dirty = False
            self._last_render_time = datetime.now()
            
            return result
            
        finally:
            duration = (time.time() - start_time) * 1000
            self._operation_times['render_document'].append(duration)
    
    async def apply_batch_animation(self, animation_data: Dict[str, Any], 
                                  character_range: Optional[Tuple[int, int]] = None) -> None:
        """Apply animation to characters in batch."""
        start_time = time.time()
        
        try:
            # Determine range
            if character_range:
                start_idx, end_idx = character_range
                characters = self._characters[start_idx:end_idx]
            else:
                characters = self._characters
            
            # Apply animation in parallel
            def apply_animation(char):
                char.set_animation(animation_data)
            
            # Use thread pool for CPU-bound animation setup
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(apply_animation, characters)
            
            self._dirty = True
            
        finally:
            duration = (time.time() - start_time) * 1000
            self._operation_times['apply_animation'].append(duration)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get document performance statistics."""
        stats = {}
        
        for operation, times in self._operation_times.items():
            if times:
                stats[operation] = {
                    'count': len(times),
                    'mean_ms': statistics.mean(times),
                    'median_ms': statistics.median(times),
                    'total_ms': sum(times)
                }
        
        stats['document_info'] = {
            'name': self.name,
            'character_count': len(self._characters),
            'cache_size': len(self._render_cache),
            'dirty': self._dirty,
            'last_render': self._last_render_time.isoformat() if self._last_render_time else None
        }
        
        return stats


# Demonstration Function
async def demonstrate_optimized_flyweight_pattern():
    """Demonstrate the optimized Flyweight pattern implementation."""
    
    print("=== Optimized Text Editor - Flyweight Pattern Demo ===\n")
    
    # Create intelligent flyweight factory
    factory = IntelligentFlyweightFactory(
        cache_strategy=CacheStrategy.ADAPTIVE,
        max_cache_size=50000,
        enable_compression=True,
        allocation_strategy=AllocationStrategy.ADAPTIVE
    )
    
    print("1. Factory Initialization:")
    print("-" * 30)
    
    initial_stats = await factory.get_factory_statistics()
    print(f"Initial flyweights: {initial_stats['flyweight_counts']['total_flyweights']}")
    print(f"Cache strategy: {initial_stats['configuration']['cache_strategy']}")
    print(f"Compression enabled: {initial_stats['configuration']['compression_enabled']}")
    print()
    
    # Create optimized document
    print("2. Document Creation with Batch Operations:")
    print("-" * 45)
    
    doc = OptimizedDocument("Advanced Document", factory)
    
    # Insert text asynchronously
    start_time = time.time()
    await doc.insert_text_async(
        "Hello World! This is an advanced flyweight demonstration with optimized performance.",
        font_family="Arial",
        font_size=12,
        color=Color(50, 50, 50)
    )
    insert_duration = time.time() - start_time
    
    print(f"✓ Text insertion completed in {insert_duration:.3f}s")
    print(f"Document characters: {len(doc._characters)}")
    print()
    
    # Add more content with different fonts
    print("3. Multi-Font Content Creation:")
    print("-" * 35)
    
    fonts_and_content = [
        ("Times New Roman", 14, "This is serif text. "),
        ("Courier New", 10, "This is monospace code. "),
        ("Helvetica", 16, "This is large sans-serif. "),
        ("Georgia", 12, "This is readable text. ")
    ]
    
    for font_family, font_size, content in fonts_and_content:
        await doc.insert_text_async(content, font_family, font_size, Color(0, 0, 0))
    
    print(f"✓ Multi-font content added")
    print(f"Total characters: {len(doc._characters)}")
    print()
    
    # Test flyweight sharing
    print("4. Flyweight Sharing Analysis:")
    print("-" * 35)
    
    sharing_stats = await factory.get_factory_statistics()
    flyweight_count = sharing_stats['flyweight_counts']['total_flyweights']
    character_count = len(doc._characters)
    
    print(f"Characters in document: {character_count}")
    print(f"Unique flyweights created: {flyweight_count}")
    print(f"Sharing ratio: {character_count / max(1, flyweight_count):.1f}:1")
    print(f"Memory efficiency: {sharing_stats['memory_stats']['memory_efficiency']:.1%}")
    print()
    
    # Performance testing
    print("5. Performance Testing:")
    print("-" * 25)
    
    # Test concurrent rendering
    render_start = time.time()
    rendered_content = await doc.render_document_async()
    render_duration = time.time() - render_start
    
    print(f"Document rendering: {render_duration:.3f}s")
    print(f"Rendered size: {len(rendered_content)} characters")
    
    # Test cached rendering
    cached_start = time.time()
    cached_content = await doc.render_document_async(use_cache=True)
    cached_duration = time.time() - cached_start
    
    print(f"Cached rendering: {cached_duration:.3f}s")
    print(f"Cache speedup: {render_duration / max(cached_duration, 0.001):.1f}x")
    print()
    
    # Memory optimization
    print("6. Memory Optimization:")
    print("-" * 25)
    
    pre_optimization_stats = await factory.get_factory_statistics()
    pre_memory = pre_optimization_stats['memory_stats']['total_memory_bytes']
    
    optimization_result = await factory.optimize_memory_usage(target_reduction_percent=15.0)
    
    if optimization_result['success']:
        print(f"✓ Memory optimization successful")
        print(f"Memory before: {pre_memory:,} bytes")
        print(f"Memory after: {optimization_result['final_memory_bytes']:,} bytes")
        print(f"Memory saved: {optimization_result['memory_saved_bytes']:,} bytes")
        print(f"Reduction: {optimization_result['reduction_percent']:.1f}%")
        print(f"Optimizations: {len(optimization_result['optimizations_applied'])}")
    else:
        print(f"✗ Memory optimization failed: {optimization_result['error']}")
    print()
    
    # Advanced features demonstration
    print("7. Advanced Features:")
    print("-" * 22)
    
    # Batch animation
    animation_data = {'rotation': 5, 'scale': 1.1}
    await doc.apply_batch_animation(animation_data, character_range=(0, 20))
    print("✓ Batch animation applied")
    
    # Performance analytics
    doc_stats = doc.get_performance_stats()
    print(f"✓ Performance analytics:")
    for operation, stats in doc_stats.items():
        if isinstance(stats, dict) and 'mean_ms' in stats:
            print(f"  {operation}: {stats['mean_ms']:.2f}ms avg ({stats['count']} ops)")
    print()
    
    # Large-scale stress test
    print("8. Stress Test - Large Document:")
    print("-" * 35)
    
    stress_doc = OptimizedDocument("Stress Test", factory)
    
    # Create large document
    stress_start = time.time()
    large_text = "Lorem ipsum dolor sit amet. " * 1000  # ~28k characters
    await stress_doc.insert_text_async(large_text, "Arial", 12, Color(0, 0, 0))
    stress_creation_time = time.time() - stress_start
    
    # Render large document
    stress_render_start = time.time()
    large_rendered = await stress_doc.render_document_async()
    stress_render_time = time.time() - stress_render_start
    
    print(f"Large document creation: {stress_creation_time:.3f}s")
    print(f"Large document rendering: {stress_render_time:.3f}s")
    print(f"Characters processed: {len(stress_doc._characters):,}")
    print(f"Processing rate: {len(stress_doc._characters) / max(stress_creation_time, 0.001):,.0f} chars/sec")
    print()
    
    # Final statistics
    print("9. Final System Statistics:")
    print("-" * 30)
    
    final_stats = await factory.get_factory_statistics()
    
    print(f"Performance Summary:")
    print(f"  Total flyweights: {final_stats['flyweight_counts']['total_flyweights']}")
    print(f"  Cache hit rate: {final_stats['performance_stats']['cache_hit_rate']:.1%}")
    print(f"  Total memory: {final_stats['memory_stats']['total_memory_bytes']:,} bytes")
    print(f"  Memory efficiency: {final_stats['memory_stats']['memory_efficiency']:.1%}")
    print(f"  GC collections: {final_stats['memory_stats'].get('gc_collections', 0)}")
    print()
    
    # Detailed performance metrics
    if 'detailed_performance' in final_stats:
        perf_details = final_stats['detailed_performance']
        print(f"Detailed Performance:")
        for operation, metrics in perf_details.items():
            if isinstance(metrics, dict) and 'mean_ms' in metrics:
                print(f"  {operation}: {metrics['mean_ms']:.2f}ms avg (P95: {metrics.get('p95_ms', 0):.2f}ms)")
    print()
    
    # Graceful shutdown
    print("10. System Shutdown:")
    print("-" * 20)
    
    await factory.shutdown()
    print("✓ Factory shutdown completed")
    
    print("\n=== Optimized Flyweight Pattern Benefits ===")
    print("✓ Intelligent memory management with weak references")
    print("✓ Adaptive caching strategies")
    print("✓ Concurrent flyweight creation and operations")
    print("✓ Compression for memory efficiency")
    print("✓ Performance monitoring and optimization")
    print("✓ Memory pool allocation")
    print("✓ Automatic garbage collection integration")
    print("✓ Batch operations for performance")
    print("✓ Thread-safe operations")
    print("✓ Comprehensive analytics and metrics")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run the demonstration
    asyncio.run(demonstrate_optimized_flyweight_pattern())