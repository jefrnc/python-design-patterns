"""
Composite Design Pattern - Optimized Implementation

An advanced implementation demonstrating the Composite pattern with Python 3.13.5
features including async operations, generic typing, performance optimization,
concurrent operations, caching, and advanced monitoring.

This optimized version includes:
- Async file system operations
- Generic type safety with protocols
- Concurrent tree traversal and operations
- LRU caching for frequently accessed items
- Performance monitoring and metrics
- Batch operations for efficiency
- Transaction support with rollback
- Memory-efficient lazy loading
- Thread-safe operations
- Advanced search with indexing
"""

import asyncio
import logging
import time
import hashlib
import weakref
import mimetypes
from abc import ABC, abstractmethod
from typing import (
    Dict, List, Optional, Set, Protocol, TypeVar, Generic, 
    Callable, Awaitable, AsyncIterator, Union, Tuple, Any
)
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
import statistics


# Type Variables and Protocols
T = TypeVar('T')
F = TypeVar('F', bound='FileSystemObject')


class FileSystemProtocol(Protocol[T]):
    """Protocol defining the interface for file system objects."""
    
    async def get_size(self) -> int: ...
    async def get_file_count(self) -> int: ...
    async def search(self, criteria: 'SearchCriteria') -> List[T]: ...
    async def copy_to(self, destination_path: str) -> bool: ...
    async def move_to(self, destination_path: str) -> bool: ...
    async def delete(self) -> bool: ...


class CacheProtocol(Protocol):
    """Protocol for cache implementations."""
    
    async def get(self, key: str) -> Optional[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...


# Enhanced Enums
class FileType(Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"


class Permission(Enum):
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"
    ADMIN = "a"


class OperationType(Enum):
    CREATE = auto()
    READ = auto()
    UPDATE = auto()
    DELETE = auto()
    COPY = auto()
    MOVE = auto()
    COMPRESS = auto()
    SEARCH = auto()


class CompressionAlgorithm(Enum):
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    ZSTD = "zstd"
    LZ4 = "lz4"


# Enhanced Data Classes
@dataclass
class FileMetadata:
    """Enhanced metadata with validation and serialization."""
    name: str
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    owner: str = "system"
    group: str = "users"
    permissions: Dict[str, Set[Permission]] = field(default_factory=lambda: {
        "owner": {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        "group": {Permission.READ, Permission.EXECUTE},
        "others": {Permission.READ}
    })
    file_type: FileType = FileType.UNKNOWN
    mime_type: str = "application/octet-stream"
    checksum: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    compression: CompressionAlgorithm = CompressionAlgorithm.NONE
    encrypted: bool = False
    version: int = 1
    
    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if self.size_bytes < 0:
            raise ValueError("Size cannot be negative")
        if self.version < 1:
            raise ValueError("Version must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "owner": self.owner,
            "group": self.group,
            "permissions": {k: [p.value for p in v] for k, v in self.permissions.items()},
            "file_type": self.file_type.value,
            "mime_type": self.mime_type,
            "checksum": self.checksum,
            "tags": list(self.tags),
            "custom_attributes": self.custom_attributes,
            "compression": self.compression.value,
            "encrypted": self.encrypted,
            "version": self.version
        }


@dataclass
class SearchCriteria:
    """Enhanced search criteria with indexing support."""
    name_pattern: Optional[str] = None
    file_type: Optional[FileType] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    owner: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    has_permission: Optional[Permission] = None
    content_pattern: Optional[str] = None
    mime_type_pattern: Optional[str] = None
    checksum: Optional[str] = None
    encrypted_only: bool = False
    compressed_only: bool = False
    max_depth: Optional[int] = None
    
    def matches_metadata(self, metadata: FileMetadata) -> bool:
        """Check if metadata matches criteria efficiently."""
        # Name pattern check
        if self.name_pattern and self.name_pattern not in metadata.name:
            return False
        
        # File type check
        if self.file_type and self.file_type != metadata.file_type:
            return False
        
        # Size checks
        if self.min_size and metadata.size_bytes < self.min_size:
            return False
        if self.max_size and metadata.size_bytes > self.max_size:
            return False
        
        # Date checks
        if self.created_after and metadata.created_at < self.created_after:
            return False
        if self.created_before and metadata.created_at > self.created_before:
            return False
        if self.modified_after and metadata.modified_at < self.modified_after:
            return False
        if self.modified_before and metadata.modified_at > self.modified_before:
            return False
        
        # Owner check
        if self.owner and self.owner != metadata.owner:
            return False
        
        # Tags check
        if self.tags and not self.tags.issubset(metadata.tags):
            return False
        
        # MIME type pattern
        if self.mime_type_pattern and self.mime_type_pattern not in metadata.mime_type:
            return False
        
        # Checksum check
        if self.checksum and self.checksum != metadata.checksum:
            return False
        
        # Encryption check
        if self.encrypted_only and not metadata.encrypted:
            return False
        
        # Compression check
        if self.compressed_only and metadata.compression == CompressionAlgorithm.NONE:
            return False
        
        return True


@dataclass
class OperationResult:
    """Result of file system operations."""
    operation: OperationType
    success: bool
    object_path: str
    duration_ms: float
    bytes_processed: int = 0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BatchOperationResult:
    """Result of batch operations."""
    total_operations: int
    successful_operations: int
    failed_operations: int
    total_duration_ms: float
    total_bytes_processed: int
    results: List[OperationResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successful_operations / max(1, self.total_operations)


# Advanced Cache Implementation
class AsyncLRUCache:
    """Thread-safe async LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._access_order: deque = deque()
        self._lock = asyncio.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.now() < expiry:
                    # Move to end (most recently used)
                    try:
                        self._access_order.remove(key)
                    except ValueError:
                        pass
                    self._access_order.append(key)
                    self._stats['hits'] += 1
                    return value
                else:
                    # Expired
                    del self._cache[key]
                    try:
                        self._access_order.remove(key)
                    except ValueError:
                        pass
            
            self._stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        async with self._lock:
            if key in self._cache:
                try:
                    self._access_order.remove(key)
                except ValueError:
                    pass
            elif len(self._cache) >= self.max_size:
                # Remove least recently used
                while self._access_order and len(self._cache) >= self.max_size:
                    lru_key = self._access_order.popleft()
                    if lru_key in self._cache:
                        del self._cache[lru_key]
                        self._stats['evictions'] += 1
            
            self._cache[key] = (value, expiry)
            self._access_order.append(key)
            self._stats['sets'] += 1
    
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                try:
                    self._access_order.remove(key)
                except ValueError:
                    pass
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / max(1, total_requests)
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                **self._stats
            }


# Performance Monitor
class PerformanceMonitor:
    """Advanced performance monitoring with statistical analysis."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self._lock = threading.Lock()
    
    def record_operation(self, operation: OperationType, duration_ms: float, 
                        bytes_processed: int = 0, success: bool = True) -> None:
        """Record an operation's performance metrics."""
        with self._lock:
            metric_base = f"{operation.name.lower()}"
            self.metrics[f"{metric_base}_duration"].append(duration_ms)
            self.metrics[f"{metric_base}_bytes"].append(bytes_processed)
            self.metrics[f"{metric_base}_success"].append(1 if success else 0)
    
    def get_statistics(self, operation: OperationType) -> Dict[str, Any]:
        """Get statistical summary for an operation type."""
        with self._lock:
            metric_base = f"{operation.name.lower()}"
            durations = list(self.metrics[f"{metric_base}_duration"])
            bytes_processed = list(self.metrics[f"{metric_base}_bytes"])
            successes = list(self.metrics[f"{metric_base}_success"])
        
        if not durations:
            return {}
        
        stats = {
            'operation': operation.name,
            'count': len(durations),
            'duration_stats': self._calculate_stats(durations),
            'bytes_stats': self._calculate_stats(bytes_processed),
            'success_rate': sum(successes) / len(successes) if successes else 0
        }
        
        # Calculate throughput
        if bytes_processed and durations:
            throughputs = [b / max(d, 0.001) for b, d in zip(bytes_processed, durations)]
            stats['throughput_stats'] = self._calculate_stats(throughputs)
        
        return stats
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical measures for a list of values."""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(values)
        
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if n > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'p50': sorted_values[n // 2],
            'p95': sorted_values[int(n * 0.95)] if n > 20 else max(values),
            'p99': sorted_values[int(n * 0.99)] if n > 100 else max(values)
        }


# Search Index for Performance
class SearchIndex:
    """In-memory search index for fast lookups."""
    
    def __init__(self):
        self.name_index: Dict[str, Set[str]] = defaultdict(set)  # name -> object_ids
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)   # tag -> object_ids
        self.type_index: Dict[FileType, Set[str]] = defaultdict(set)  # type -> object_ids
        self.size_index: List[Tuple[int, str]] = []  # (size, object_id) sorted by size
        self.owner_index: Dict[str, Set[str]] = defaultdict(set)  # owner -> object_ids
        self._lock = threading.RLock()
    
    def add_object(self, object_id: str, metadata: FileMetadata) -> None:
        """Add object to search index."""
        with self._lock:
            # Name index (substring matching)
            for i in range(len(metadata.name)):
                for j in range(i + 1, len(metadata.name) + 1):
                    substring = metadata.name[i:j].lower()
                    if len(substring) >= 2:  # Only index substrings of length 2+
                        self.name_index[substring].add(object_id)
            
            # Tag index
            for tag in metadata.tags:
                self.tag_index[tag.lower()].add(object_id)
            
            # Type index
            self.type_index[metadata.file_type].add(object_id)
            
            # Size index (keep sorted)
            self.size_index.append((metadata.size_bytes, object_id))
            self.size_index.sort(key=lambda x: x[0])
            
            # Owner index
            self.owner_index[metadata.owner.lower()].add(object_id)
    
    def remove_object(self, object_id: str, metadata: FileMetadata) -> None:
        """Remove object from search index."""
        with self._lock:
            # Name index
            for i in range(len(metadata.name)):
                for j in range(i + 1, len(metadata.name) + 1):
                    substring = metadata.name[i:j].lower()
                    if len(substring) >= 2:
                        self.name_index[substring].discard(object_id)
                        if not self.name_index[substring]:
                            del self.name_index[substring]
            
            # Tag index
            for tag in metadata.tags:
                self.tag_index[tag.lower()].discard(object_id)
                if not self.tag_index[tag.lower()]:
                    del self.tag_index[tag.lower()]
            
            # Type index
            self.type_index[metadata.file_type].discard(object_id)
            
            # Size index
            self.size_index = [(size, oid) for size, oid in self.size_index if oid != object_id]
            
            # Owner index
            self.owner_index[metadata.owner.lower()].discard(object_id)
            if not self.owner_index[metadata.owner.lower()]:
                del self.owner_index[metadata.owner.lower()]
    
    def search(self, criteria: SearchCriteria) -> Set[str]:
        """Search for object IDs matching criteria."""
        with self._lock:
            result_sets = []
            
            # Name pattern search
            if criteria.name_pattern:
                pattern = criteria.name_pattern.lower()
                matching_ids = set()
                for substring, ids in self.name_index.items():
                    if pattern in substring:
                        matching_ids.update(ids)
                result_sets.append(matching_ids)
            
            # Tag search
            if criteria.tags:
                tag_ids = set()
                for tag in criteria.tags:
                    tag_ids.intersection_update(self.tag_index.get(tag.lower(), set()))
                result_sets.append(tag_ids)
            
            # Type search
            if criteria.file_type:
                result_sets.append(self.type_index[criteria.file_type])
            
            # Owner search
            if criteria.owner:
                result_sets.append(self.owner_index.get(criteria.owner.lower(), set()))
            
            # Size range search
            if criteria.min_size is not None or criteria.max_size is not None:
                min_size = criteria.min_size or 0
                max_size = criteria.max_size or float('inf')
                size_ids = {oid for size, oid in self.size_index if min_size <= size <= max_size}
                result_sets.append(size_ids)
            
            # Intersect all result sets
            if result_sets:
                return set.intersection(*result_sets)
            else:
                return set()


# Transaction Support
class Transaction:
    """Transaction support with rollback capability."""
    
    def __init__(self):
        self.operations: List[Callable[[], Awaitable[None]]] = []
        self.rollback_operations: List[Callable[[], Awaitable[None]]] = []
        self.completed = False
    
    def add_operation(self, operation: Callable[[], Awaitable[None]], 
                     rollback: Callable[[], Awaitable[None]]) -> None:
        """Add an operation with its rollback."""
        if self.completed:
            raise RuntimeError("Cannot add operations to completed transaction")
        self.operations.append(operation)
        self.rollback_operations.append(rollback)
    
    async def commit(self) -> bool:
        """Execute all operations."""
        try:
            for operation in self.operations:
                await operation()
            self.completed = True
            return True
        except Exception as e:
            await self.rollback()
            raise e
    
    async def rollback(self) -> None:
        """Rollback all completed operations."""
        for rollback in reversed(self.rollback_operations):
            try:
                await rollback()
            except Exception as e:
                logging.error(f"Rollback operation failed: {e}")


# Enhanced Component Interface
class FileSystemObject(ABC):
    """Enhanced file system object with async operations and caching."""
    
    def __init__(self, metadata: FileMetadata):
        self.metadata = metadata
        self.parent: Optional['OptimizedDirectory'] = None
        self._object_id = f"{id(self)}_{hash(metadata.name)}"
        self._cache = AsyncLRUCache(max_size=100, default_ttl=300)
        self._lock = asyncio.RLock()
        self._access_count = 0
        self._last_accessed = datetime.now()
    
    @abstractmethod
    async def get_size(self) -> int:
        """Get total size in bytes."""
        pass
    
    @abstractmethod
    async def get_file_count(self) -> int:
        """Get total number of files."""
        pass
    
    @abstractmethod
    async def search(self, criteria: SearchCriteria, current_depth: int = 0) -> List['FileSystemObject']:
        """Search for objects matching criteria."""
        pass
    
    @abstractmethod
    async def copy_to(self, destination_path: str) -> bool:
        """Copy this object to destination."""
        pass
    
    @abstractmethod
    async def move_to(self, destination_path: str) -> bool:
        """Move this object to destination."""
        pass
    
    @abstractmethod
    async def delete(self) -> bool:
        """Delete this object."""
        pass
    
    @abstractmethod
    async def compress(self, algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP) -> bool:
        """Compress this object."""
        pass
    
    async def get_path(self) -> str:
        """Get full path of this object."""
        if self.parent is None:
            return self.metadata.name
        parent_path = await self.parent.get_path()
        return f"{parent_path}/{self.metadata.name}"
    
    def update_access_time(self) -> None:
        """Update access statistics."""
        self._access_count += 1
        self._last_accessed = datetime.now()
        self.metadata.accessed_at = datetime.now()
    
    async def get_metadata_dict(self) -> Dict[str, Any]:
        """Get metadata as dictionary with caching."""
        cache_key = f"metadata_{self._object_id}"
        cached = await self._cache.get(cache_key)
        
        if cached is None:
            metadata_dict = self.metadata.to_dict()
            metadata_dict.update({
                'object_id': self._object_id,
                'access_count': self._access_count,
                'last_accessed': self._last_accessed.isoformat(),
                'path': await self.get_path()
            })
            await self._cache.set(cache_key, metadata_dict, ttl=60)
            return metadata_dict
        
        return cached
    
    async def calculate_checksum(self) -> str:
        """Calculate and cache object checksum."""
        cache_key = f"checksum_{self._object_id}"
        cached = await self._cache.get(cache_key)
        
        if cached is None:
            # Simulate checksum calculation
            content = f"{self.metadata.name}_{self.metadata.size_bytes}_{self.metadata.modified_at}"
            checksum = hashlib.sha256(content.encode()).hexdigest()
            self.metadata.checksum = checksum
            await self._cache.set(cache_key, checksum, ttl=3600)
            return checksum
        
        return cached


# Enhanced File Implementation
class OptimizedFile(FileSystemObject):
    """Optimized file implementation with async operations."""
    
    def __init__(self, metadata: FileMetadata, content: bytes = b""):
        super().__init__(metadata)
        self._content = content
        self.metadata.size_bytes = len(content)
        self._content_cache_key = f"content_{self._object_id}"
        
        # Determine file type and MIME type
        self._determine_file_properties()
    
    def _determine_file_properties(self) -> None:
        """Determine file type and MIME type."""
        mime_type, _ = mimetypes.guess_type(self.metadata.name)
        
        if mime_type:
            self.metadata.mime_type = mime_type
            
            if mime_type.startswith('text/') or mime_type in ['application/pdf', 'application/msword']:
                self.metadata.file_type = FileType.DOCUMENT
            elif mime_type.startswith('image/'):
                self.metadata.file_type = FileType.IMAGE
            elif mime_type.startswith('video/'):
                self.metadata.file_type = FileType.VIDEO
            elif mime_type.startswith('audio/'):
                self.metadata.file_type = FileType.AUDIO
            elif mime_type in ['application/zip', 'application/x-rar']:
                self.metadata.file_type = FileType.ARCHIVE
            elif mime_type in ['application/x-executable']:
                self.metadata.file_type = FileType.EXECUTABLE
    
    async def get_size(self) -> int:
        """Get file size."""
        return self.metadata.size_bytes
    
    async def get_file_count(self) -> int:
        """Files count as 1."""
        return 1
    
    async def search(self, criteria: SearchCriteria, current_depth: int = 0) -> List[FileSystemObject]:
        """Search this file against criteria."""
        self.update_access_time()
        
        if criteria.matches_metadata(self.metadata):
            # Additional content search if needed
            if criteria.content_pattern:
                content = await self.read_content()
                if content and criteria.content_pattern.encode() in content:
                    return [self]
                else:
                    return []
            return [self]
        return []
    
    async def copy_to(self, destination_path: str) -> bool:
        """Copy file to destination."""
        start_time = time.time()
        try:
            # Simulate async file copy
            await asyncio.sleep(0.01)  # Simulate I/O
            logging.info(f"Copying file '{self.metadata.name}' to '{destination_path}'")
            return True
        except Exception as e:
            logging.error(f"Failed to copy file '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def move_to(self, destination_path: str) -> bool:
        """Move file to destination."""
        start_time = time.time()
        try:
            await asyncio.sleep(0.01)  # Simulate I/O
            logging.info(f"Moving file '{self.metadata.name}' to '{destination_path}'")
            if self.parent:
                await self.parent.remove_child(self)
            return True
        except Exception as e:
            logging.error(f"Failed to move file '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def delete(self) -> bool:
        """Delete this file."""
        start_time = time.time()
        try:
            logging.info(f"Deleting file '{self.metadata.name}'")
            if self.parent:
                await self.parent.remove_child(self)
            await self._cache.clear()
            return True
        except Exception as e:
            logging.error(f"Failed to delete file '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def compress(self, algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP) -> bool:
        """Compress file content."""
        start_time = time.time()
        try:
            if algorithm == CompressionAlgorithm.NONE:
                return True
            
            original_size = len(self._content)
            
            # Simulate compression with different algorithms
            compression_ratios = {
                CompressionAlgorithm.GZIP: 0.7,
                CompressionAlgorithm.LZMA: 0.6,
                CompressionAlgorithm.ZSTD: 0.65,
                CompressionAlgorithm.LZ4: 0.8
            }
            
            ratio = compression_ratios.get(algorithm, 0.7)
            compressed_size = int(original_size * ratio)
            
            await asyncio.sleep(0.05)  # Simulate compression time
            
            self.metadata.size_bytes = compressed_size
            self.metadata.compression = algorithm
            self.metadata.modified_at = datetime.now()
            
            # Clear content cache
            await self._cache.delete(self._content_cache_key)
            
            logging.info(f"Compressed '{self.metadata.name}': {original_size} -> {compressed_size} bytes ({algorithm.value})")
            return True
            
        except Exception as e:
            logging.error(f"Failed to compress file '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def read_content(self) -> Optional[bytes]:
        """Read file content with caching."""
        cached_content = await self._cache.get(self._content_cache_key)
        if cached_content is not None:
            self.update_access_time()
            return cached_content
        
        # Simulate async read
        await asyncio.sleep(0.001)
        await self._cache.set(self._content_cache_key, self._content, ttl=300)
        self.update_access_time()
        return self._content
    
    async def write_content(self, content: bytes) -> bool:
        """Write file content."""
        try:
            await asyncio.sleep(0.001)  # Simulate async write
            self._content = content
            self.metadata.size_bytes = len(content)
            self.metadata.modified_at = datetime.now()
            
            # Update cache
            await self._cache.set(self._content_cache_key, content, ttl=300)
            
            # Recalculate checksum
            await self.calculate_checksum()
            
            return True
        except Exception as e:
            logging.error(f"Failed to write content to '{self.metadata.name}': {e}")
            return False


# Enhanced Directory Implementation
class OptimizedDirectory(FileSystemObject):
    """Optimized directory implementation with concurrent operations."""
    
    def __init__(self, metadata: FileMetadata):
        super().__init__(metadata)
        self.children: Dict[str, FileSystemObject] = {}
        self.metadata.file_type = FileType.DIRECTORY
        self.metadata.size_bytes = 0
        self._search_index = SearchIndex()
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._lazy_loaded = False
        self._child_locks: Dict[str, asyncio.Lock] = {}
    
    async def _ensure_loaded(self) -> None:
        """Ensure directory is loaded (for lazy loading)."""
        if not self._lazy_loaded:
            # In a real implementation, this would load children from disk
            self._lazy_loaded = True
    
    async def add_child(self, child: FileSystemObject) -> bool:
        """Add a child object to this directory."""
        await self._ensure_loaded()
        
        async with self._lock:
            if child.metadata.name in self.children:
                raise ValueError(f"Object with name '{child.metadata.name}' already exists")
            
            self.children[child.metadata.name] = child
            child.parent = self
            
            # Update search index
            self._search_index.add_object(child._object_id, child.metadata)
            
            await self._update_size()
            return True
    
    async def remove_child(self, child: FileSystemObject) -> bool:
        """Remove a child object from this directory."""
        async with self._lock:
            if child.metadata.name in self.children:
                del self.children[child.metadata.name]
                child.parent = None
                
                # Update search index
                self._search_index.remove_object(child._object_id, child.metadata)
                
                await self._update_size()
                return True
            return False
    
    async def get_child(self, name: str) -> Optional[FileSystemObject]:
        """Get child by name."""
        await self._ensure_loaded()
        self.update_access_time()
        return self.children.get(name)
    
    async def _update_size(self) -> None:
        """Update directory size based on children."""
        size_tasks = [child.get_size() for child in self.children.values()]
        if size_tasks:
            sizes = await asyncio.gather(*size_tasks)
            self.metadata.size_bytes = sum(sizes)
        else:
            self.metadata.size_bytes = 0
        self.metadata.modified_at = datetime.now()
    
    async def get_size(self) -> int:
        """Get total size of directory and all contents."""
        cache_key = f"total_size_{self._object_id}"
        cached_size = await self._cache.get(cache_key)
        
        if cached_size is None:
            await self._ensure_loaded()
            size_tasks = [child.get_size() for child in self.children.values()]
            if size_tasks:
                sizes = await asyncio.gather(*size_tasks)
                total_size = sum(sizes)
            else:
                total_size = 0
            
            await self._cache.set(cache_key, total_size, ttl=60)
            return total_size
        
        return cached_size
    
    async def get_file_count(self) -> int:
        """Get total number of files in directory and subdirectories."""
        cache_key = f"file_count_{self._object_id}"
        cached_count = await self._cache.get(cache_key)
        
        if cached_count is None:
            await self._ensure_loaded()
            count_tasks = [child.get_file_count() for child in self.children.values()]
            if count_tasks:
                counts = await asyncio.gather(*count_tasks)
                total_count = sum(counts)
            else:
                total_count = 0
            
            await self._cache.set(cache_key, total_count, ttl=60)
            return total_count
        
        return cached_count
    
    async def search(self, criteria: SearchCriteria, current_depth: int = 0) -> List[FileSystemObject]:
        """Search this directory and all subdirectories concurrently."""
        await self._ensure_loaded()
        self.update_access_time()
        
        # Check depth limit
        if criteria.max_depth is not None and current_depth > criteria.max_depth:
            return []
        
        results = []
        
        # Check if this directory matches
        if criteria.matches_metadata(self.metadata):
            results.append(self)
        
        # Use search index for performance if possible
        if (criteria.name_pattern or criteria.tags or criteria.file_type or 
            criteria.owner or criteria.min_size or criteria.max_size):
            
            candidate_ids = self._search_index.search(criteria)
            candidate_children = [
                child for child in self.children.values() 
                if child._object_id in candidate_ids
            ]
        else:
            candidate_children = list(self.children.values())
        
        # Search children concurrently
        if candidate_children:
            search_tasks = [
                child.search(criteria, current_depth + 1) 
                for child in candidate_children
            ]
            
            child_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for result in child_results:
                if isinstance(result, list):
                    results.extend(result)
                elif isinstance(result, Exception):
                    logging.error(f"Search error in child: {result}")
        
        return results
    
    async def copy_to(self, destination_path: str) -> bool:
        """Copy directory and all contents concurrently."""
        start_time = time.time()
        try:
            await self._ensure_loaded()
            logging.info(f"Copying directory '{self.metadata.name}' to '{destination_path}'")
            
            # Copy all children concurrently
            if self.children:
                copy_tasks = []
                for child in self.children.values():
                    child_dest = f"{destination_path}/{self.metadata.name}/{child.metadata.name}"
                    copy_tasks.append(child.copy_to(child_dest))
                
                results = await asyncio.gather(*copy_tasks, return_exceptions=True)
                
                # Check if all copies succeeded
                success_count = sum(1 for result in results if result is True)
                total_count = len(results)
                
                if success_count < total_count:
                    logging.warning(f"Only {success_count}/{total_count} children copied successfully")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to copy directory '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def move_to(self, destination_path: str) -> bool:
        """Move directory and all contents."""
        start_time = time.time()
        try:
            success = await self.copy_to(destination_path)
            if success:
                await self.delete()
            return success
        except Exception as e:
            logging.error(f"Failed to move directory '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def delete(self) -> bool:
        """Delete directory and all contents concurrently."""
        start_time = time.time()
        try:
            await self._ensure_loaded()
            logging.info(f"Deleting directory '{self.metadata.name}' and all contents")
            
            # Delete all children concurrently
            if self.children:
                delete_tasks = [child.delete() for child in list(self.children.values())]
                await asyncio.gather(*delete_tasks, return_exceptions=True)
                self.children.clear()
            
            if self.parent:
                await self.parent.remove_child(self)
            
            await self._cache.clear()
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete directory '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def compress(self, algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP) -> bool:
        """Compress all files in directory concurrently."""
        start_time = time.time()
        try:
            await self._ensure_loaded()
            logging.info(f"Compressing directory '{self.metadata.name}' ({algorithm.value})")
            
            if self.children:
                compress_tasks = [child.compress(algorithm) for child in self.children.values()]
                results = await asyncio.gather(*compress_tasks, return_exceptions=True)
                
                success_count = sum(1 for result in results if result is True)
                logging.info(f"Successfully compressed {success_count}/{len(results)} items")
            
            await self._update_size()
            await self._cache.delete(f"total_size_{self._object_id}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to compress directory '{self.metadata.name}': {e}")
            return False
        finally:
            duration = (time.time() - start_time) * 1000
            # Performance monitoring would be recorded here
    
    async def list_contents(self, show_hidden: bool = False) -> List[FileSystemObject]:
        """List directory contents."""
        await self._ensure_loaded()
        self.update_access_time()
        
        if show_hidden:
            return list(self.children.values())
        else:
            return [child for child in self.children.values() 
                   if not child.metadata.name.startswith('.')]
    
    async def batch_operation(self, operation: Callable[[FileSystemObject], Awaitable[bool]], 
                            children: Optional[List[str]] = None) -> BatchOperationResult:
        """Perform batch operation on children."""
        await self._ensure_loaded()
        
        targets = []
        if children:
            targets = [self.children[name] for name in children if name in self.children]
        else:
            targets = list(self.children.values())
        
        start_time = time.time()
        results = []
        
        # Execute operations concurrently
        tasks = [operation(child) for child in targets]
        operation_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = 0
        total_bytes = 0
        
        for i, result in enumerate(operation_results):
            target = targets[i]
            if isinstance(result, Exception):
                results.append(OperationResult(
                    operation=OperationType.UPDATE,  # Generic
                    success=False,
                    object_path=await target.get_path(),
                    duration_ms=0,
                    error_message=str(result)
                ))
            else:
                success = bool(result)
                if success:
                    successful += 1
                    total_bytes += target.metadata.size_bytes
                
                results.append(OperationResult(
                    operation=OperationType.UPDATE,
                    success=success,
                    object_path=await target.get_path(),
                    duration_ms=(time.time() - start_time) * 1000,
                    bytes_processed=target.metadata.size_bytes
                ))
        
        total_duration = (time.time() - start_time) * 1000
        
        return BatchOperationResult(
            total_operations=len(targets),
            successful_operations=successful,
            failed_operations=len(targets) - successful,
            total_duration_ms=total_duration,
            total_bytes_processed=total_bytes,
            results=results
        )


# Enhanced File System Manager
class OptimizedFileSystemManager:
    """Optimized file system manager with advanced features."""
    
    def __init__(self):
        self.root = OptimizedDirectory(FileMetadata("root", owner="system"))
        self.current_directory = self.root
        self.performance_monitor = PerformanceMonitor()
        self.global_cache = AsyncLRUCache(max_size=50000, default_ttl=1800)
        self._transaction_stack: List[Transaction] = []
        self._background_tasks: Set[asyncio.Task] = set()
    
    async def start_background_tasks(self):
        """Start background maintenance tasks."""
        # Cache cleanup task
        cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        self._background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._background_tasks.discard)
        
        # Metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self._background_tasks.add(metrics_task)
        metrics_task.add_done_callback(self._background_tasks.discard)
    
    async def stop_background_tasks(self):
        """Stop all background tasks."""
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self._background_tasks.clear()
    
    async def _cache_cleanup_loop(self):
        """Background cache cleanup."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Get cache statistics
                stats = await self.global_cache.get_stats()
                if stats['hit_rate'] < 0.5 and stats['size'] > stats['max_size'] * 0.8:
                    # Clear some cache if hit rate is low and cache is full
                    await self.global_cache.clear()
                    logging.info("Performed cache cleanup due to low hit rate")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cache cleanup: {e}")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection."""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Collect system-wide metrics
                total_size = await self.root.get_size()
                total_files = await self.root.get_file_count()
                
                self.performance_monitor.record_operation(
                    OperationType.READ, 0, total_size, True
                )
                
                logging.debug(f"System metrics: {total_files} files, {total_size} bytes")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in metrics collection: {e}")
    
    async def change_directory(self, path: str) -> bool:
        """Change current directory."""
        if path == "/":
            self.current_directory = self.root
            return True
        elif path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
                return True
            return False
        else:
            child = await self.current_directory.get_child(path)
            if isinstance(child, OptimizedDirectory):
                self.current_directory = child
                return True
            return False
    
    async def search_files(self, criteria: SearchCriteria) -> List[FileSystemObject]:
        """Search files from current directory."""
        start_time = time.time()
        try:
            results = await self.current_directory.search(criteria)
            return results
        finally:
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_operation(
                OperationType.SEARCH, duration, len(results) if results else 0, True
            )
    
    async def bulk_operations(self, operation_type: str, 
                            targets: List[str]) -> BatchOperationResult:
        """Perform bulk operations on multiple files."""
        operation_map = {
            'delete': lambda obj: obj.delete(),
            'compress': lambda obj: obj.compress(),
            'copy': lambda obj: obj.copy_to(f"/backup/{obj.metadata.name}")
        }
        
        if operation_type not in operation_map:
            raise ValueError(f"Unsupported operation: {operation_type}")
        
        return await self.current_directory.batch_operation(
            operation_map[operation_type], targets
        )
    
    async def create_transaction(self) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction()
        self._transaction_stack.append(transaction)
        return transaction
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        cache_stats = await self.global_cache.get_stats()
        
        stats = {
            'total_size_gb': await self.root.get_size() / (1024**3),
            'total_files': await self.root.get_file_count(),
            'current_directory': await self.current_directory.get_path(),
            'cache_stats': cache_stats,
            'performance_stats': {}
        }
        
        # Add performance statistics for each operation type
        for op_type in OperationType:
            op_stats = self.performance_monitor.get_statistics(op_type)
            if op_stats:
                stats['performance_stats'][op_type.name.lower()] = op_stats
        
        return stats
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_background_tasks()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_background_tasks()


# Demonstration Function
async def demonstrate_optimized_composite_pattern():
    """Demonstrate the optimized Composite pattern implementation."""
    
    print("=== Optimized File System - Composite Pattern Demo ===\n")
    
    async with OptimizedFileSystemManager() as fs:
        # Create directory structure
        print("1. Creating Optimized Directory Structure:")
        print("-" * 45)
        
        # Create documents directory
        documents_meta = FileMetadata("Documents", owner="alice")
        documents = OptimizedDirectory(documents_meta)
        await fs.root.add_child(documents)
        
        # Create projects directory with tags
        projects_meta = FileMetadata("Projects", owner="alice")
        projects_meta.tags.update(["work", "code"])
        projects = OptimizedDirectory(projects_meta)
        await fs.root.add_child(projects)
        
        # Create files with different types
        resume_meta = FileMetadata("resume.pdf", owner="alice")
        resume_meta.file_type = FileType.DOCUMENT
        resume_meta.tags.update(["important", "personal"])
        resume = OptimizedFile(resume_meta, b"PDF content for resume" * 100)
        await documents.add_child(resume)
        
        code_meta = FileMetadata("main.py", owner="alice")
        code_meta.file_type = FileType.DOCUMENT
        code_meta.tags.update(["python", "code"])
        code_file = OptimizedFile(code_meta, b"print('Hello World')" * 50)
        await projects.add_child(code_file)
        
        # Create large video file
        video_meta = FileMetadata("presentation.mp4", owner="alice")
        video_meta.file_type = FileType.VIDEO
        video_meta.tags.update(["presentation", "work"])
        video = OptimizedFile(video_meta, b"Video data" * 10000)
        await documents.add_child(video)
        
        print(f"✓ Created directory structure with {await fs.root.get_file_count()} files")
        print(f"✓ Total size: {await fs.root.get_size() / 1024:.1f} KB")
        print()
        
        # Demonstrate concurrent operations
        print("2. Concurrent Operations:")
        print("-" * 30)
        
        # Concurrent size calculation
        start_time = time.time()
        size_tasks = [
            fs.root.get_size(),
            documents.get_size(),
            projects.get_size()
        ]
        sizes = await asyncio.gather(*size_tasks)
        concurrent_duration = time.time() - start_time
        
        print(f"Concurrent size calculation: {concurrent_duration:.3f}s")
        print(f"  Root: {sizes[0]} bytes")
        print(f"  Documents: {sizes[1]} bytes") 
        print(f"  Projects: {sizes[2]} bytes")
        print()
        
        # Demonstrate optimized search
        print("3. Optimized Search Operations:")
        print("-" * 35)
        
        # Search by tags
        start_time = time.time()
        tag_criteria = SearchCriteria(tags={"work"})
        work_files = await fs.search_files(tag_criteria)
        search_duration = time.time() - start_time
        
        print(f"Tag search ('work'): {search_duration:.3f}s")
        print(f"Found {len(work_files)} files:")
        for file_obj in work_files:
            print(f"  - {file_obj.metadata.name}")
        print()
        
        # Search by file type
        start_time = time.time()
        doc_criteria = SearchCriteria(file_type=FileType.DOCUMENT)
        doc_files = await fs.search_files(doc_criteria)
        type_search_duration = time.time() - start_time
        
        print(f"Type search (DOCUMENT): {type_search_duration:.3f}s")
        print(f"Found {len(doc_files)} document files")
        print()
        
        # Demonstrate caching performance
        print("4. Caching Performance:")
        print("-" * 25)
        
        # First access (cache miss)
        start_time = time.time()
        size1 = await documents.get_size()
        first_access = time.time() - start_time
        
        # Second access (cache hit)
        start_time = time.time()
        size2 = await documents.get_size()
        second_access = time.time() - start_time
        
        print(f"First access (cache miss): {first_access:.3f}s")
        print(f"Second access (cache hit): {second_access:.3f}s")
        print(f"Speedup: {first_access/max(second_access, 0.001):.1f}x")
        print()
        
        # Demonstrate batch operations
        print("5. Batch Operations:")
        print("-" * 20)
        
        # Batch compression
        targets = ["main.py"]  # Only compress the Python file
        compress_result = await fs.bulk_operations("compress", targets)
        
        print(f"Batch compression results:")
        print(f"  Total operations: {compress_result.total_operations}")
        print(f"  Successful: {compress_result.successful_operations}")
        print(f"  Success rate: {compress_result.success_rate:.1%}")
        print(f"  Total duration: {compress_result.total_duration_ms:.1f}ms")
        print(f"  Bytes processed: {compress_result.total_bytes_processed}")
        print()
        
        # Demonstrate transaction support
        print("6. Transaction Support:")
        print("-" * 25)
        
        transaction = await fs.create_transaction()
        
        # Add operations to transaction
        new_file_meta = FileMetadata("temp.txt", owner="alice")
        temp_file = OptimizedFile(new_file_meta, b"Temporary content")
        
        transaction.add_operation(
            lambda: documents.add_child(temp_file),
            lambda: documents.remove_child(temp_file)
        )
        
        # Commit transaction
        try:
            success = await transaction.commit()
            print(f"✓ Transaction committed successfully: {success}")
            
            # Verify file was created
            temp_check = await documents.get_child("temp.txt")
            print(f"✓ File exists after transaction: {temp_check is not None}")
            
        except Exception as e:
            print(f"✗ Transaction failed: {e}")
        print()
        
        # Show performance statistics
        print("7. Performance Statistics:")
        print("-" * 30)
        
        system_stats = await fs.get_system_stats()
        
        print(f"System Overview:")
        print(f"  Total size: {system_stats['total_size_gb']:.3f} GB")
        print(f"  Total files: {system_stats['total_files']}")
        print(f"  Current directory: {system_stats['current_directory']}")
        print()
        
        cache_stats = system_stats['cache_stats']
        print(f"Cache Performance:")
        print(f"  Hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"  Total requests: {cache_stats['total_requests']}")
        print(f"  Cache size: {cache_stats['size']}")
        print()
        
        # Show operation statistics
        perf_stats = system_stats['performance_stats']
        if perf_stats:
            print("Operation Performance:")
            for op_name, stats in perf_stats.items():
                if 'duration_stats' in stats:
                    duration_stats = stats['duration_stats']
                    print(f"  {op_name.title()}:")
                    print(f"    Mean duration: {duration_stats['mean']:.3f}ms")
                    print(f"    Success rate: {stats['success_rate']:.1%}")
        print()
        
        # Demonstrate lazy loading and memory efficiency
        print("8. Memory Efficiency:")
        print("-" * 20)
        
        # Create deep directory structure
        current_dir = projects
        for i in range(5):
            subdir_meta = FileMetadata(f"level_{i}", owner="alice")
            subdir = OptimizedDirectory(subdir_meta)
            await current_dir.add_child(subdir)
            current_dir = subdir
        
        # Add many files at the deepest level
        for i in range(100):
            file_meta = FileMetadata(f"file_{i:03d}.txt", owner="alice")
            small_file = OptimizedFile(file_meta, b"Small content")
            await current_dir.add_child(small_file)
        
        # Measure search performance on large structure
        start_time = time.time()
        all_files = await fs.root.search(SearchCriteria())
        large_search_duration = time.time() - start_time
        
        print(f"Deep structure search: {large_search_duration:.3f}s")
        print(f"Total objects found: {len(all_files)}")
        print(f"Search rate: {len(all_files)/large_search_duration:.0f} objects/second")
        print()
    
    print("=== Optimized Composite Pattern Benefits ===")
    print("✓ Async operations for non-blocking I/O")
    print("✓ Concurrent traversal and operations")
    print("✓ LRU caching for performance")
    print("✓ Search indexing for fast lookups")
    print("✓ Batch operations for efficiency")
    print("✓ Transaction support with rollback")
    print("✓ Performance monitoring and metrics")
    print("✓ Memory-efficient lazy loading")
    print("✓ Background maintenance tasks")
    print("✓ Type safety with protocols")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run the demonstration
    asyncio.run(demonstrate_optimized_composite_pattern())