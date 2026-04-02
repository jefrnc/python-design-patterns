"""
Proxy Design Pattern - Real World Implementation

A real-world example demonstrating the Proxy pattern through a 
cloud storage and content delivery system that provides various
proxy types including virtual proxy (lazy loading), protection proxy
(access control), caching proxy, and smart proxy with additional
functionality like compression, encryption, and analytics.

This example shows how to:
- Control access to expensive or remote resources
- Implement lazy loading for large objects
- Add security and access control
- Provide caching and performance optimization
- Add functionality without modifying original objects
- Handle network resources transparently
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import hashlib
import base64
import gzip
import os
import logging
from threading import Lock
import weakref


class FileType(Enum):
    """Types of files in the cloud storage."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


class AccessLevel(Enum):
    """Access levels for security proxy."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class CompressionType(Enum):
    """Compression algorithms available."""
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"


@dataclass
class FileMetadata:
    """Metadata for cloud storage files."""
    filename: str
    file_size: int
    file_type: FileType
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    owner: str = "anonymous"
    permissions: Dict[str, List[AccessLevel]] = field(default_factory=dict)
    content_hash: Optional[str] = None
    encryption_key: Optional[str] = None
    compression: CompressionType = CompressionType.NONE
    download_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class User:
    """User information for access control."""
    user_id: str
    username: str
    roles: List[str] = field(default_factory=list)
    permissions: List[AccessLevel] = field(default_factory=list)
    is_authenticated: bool = False
    last_login: Optional[datetime] = None


@dataclass
class AnalyticsData:
    """Analytics data for file operations."""
    operation: str
    user_id: str
    file_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    file_size: Optional[int] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


# Subject Interface
class CloudStorageService(ABC):
    """
    Abstract interface for cloud storage operations.
    This is the Subject interface in the Proxy pattern.
    """
    
    @abstractmethod
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload a file to cloud storage."""
        pass
    
    @abstractmethod
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download a file from cloud storage."""
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from cloud storage."""
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get file metadata."""
        pass
    
    @abstractmethod
    def list_files(self, directory: str = "/") -> List[str]:
        """List files in a directory."""
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for file access."""
        pass


# Real Subject (Expensive/Remote Service)
class RealCloudStorageService(CloudStorageService):
    """
    Real cloud storage service implementation.
    This represents the expensive/remote service that we want to proxy.
    """
    
    def __init__(self, service_url: str, api_key: str):
        self.service_url = service_url
        self.api_key = api_key
        self.storage: Dict[str, bytes] = {}  # Simulated cloud storage
        self.metadata_store: Dict[str, FileMetadata] = {}
        self.connection_count = 0
        
    def _simulate_network_delay(self, base_delay: float = 0.1) -> None:
        """Simulate network latency."""
        time.sleep(base_delay)
    
    def _simulate_authentication(self) -> bool:
        """Simulate API authentication."""
        self._simulate_network_delay(0.05)
        return len(self.api_key) > 0
    
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload file to real cloud storage."""
        if not self._simulate_authentication():
            return False
        
        self._simulate_network_delay(0.2)  # Upload is slower
        self.connection_count += 1
        
        try:
            # Calculate content hash
            metadata.content_hash = hashlib.sha256(content).hexdigest()
            metadata.file_size = len(content)
            metadata.modified_at = datetime.now()
            
            # Store file and metadata
            self.storage[file_path] = content
            self.metadata_store[file_path] = metadata
            
            logging.info(f"Real service: Uploaded {file_path} ({len(content)} bytes)")
            return True
            
        except Exception as e:
            logging.error(f"Real service: Upload failed for {file_path}: {e}")
            return False
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file from real cloud storage."""
        if not self._simulate_authentication():
            return None
        
        self._simulate_network_delay(0.15)
        self.connection_count += 1
        
        if file_path in self.storage:
            content = self.storage[file_path]
            
            # Update access statistics
            if file_path in self.metadata_store:
                metadata = self.metadata_store[file_path]
                metadata.download_count += 1
                metadata.last_accessed = datetime.now()
            
            logging.info(f"Real service: Downloaded {file_path} ({len(content)} bytes)")
            return content
        
        logging.warning(f"Real service: File not found: {file_path}")
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from real cloud storage."""
        if not self._simulate_authentication():
            return False
        
        self._simulate_network_delay(0.1)
        self.connection_count += 1
        
        if file_path in self.storage:
            del self.storage[file_path]
            del self.metadata_store[file_path]
            logging.info(f"Real service: Deleted {file_path}")
            return True
        
        return False
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get file metadata from real cloud storage."""
        if not self._simulate_authentication():
            return None
        
        self._simulate_network_delay(0.05)
        self.connection_count += 1
        
        metadata = self.metadata_store.get(file_path)
        if metadata:
            logging.info(f"Real service: Retrieved metadata for {file_path}")
        
        return metadata
    
    def list_files(self, directory: str = "/") -> List[str]:
        """List files in directory."""
        if not self._simulate_authentication():
            return []
        
        self._simulate_network_delay(0.1)
        self.connection_count += 1
        
        # Simple directory filtering
        files = [path for path in self.storage.keys() 
                if path.startswith(directory) and path != directory]
        
        logging.info(f"Real service: Listed {len(files)} files in {directory}")
        return files
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        if not self._simulate_authentication():
            return False
        
        self._simulate_network_delay(0.03)
        self.connection_count += 1
        
        exists = file_path in self.storage
        logging.info(f"Real service: File exists check for {file_path}: {exists}")
        return exists
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for file access."""
        if not self._simulate_authentication():
            return None
        
        self._simulate_network_delay(0.05)
        self.connection_count += 1
        
        if file_path in self.storage:
            # Generate signed URL (simplified)
            expiry = int((datetime.now() + timedelta(seconds=expires_in)).timestamp())
            signature = hashlib.md5(f"{file_path}{expiry}{self.api_key}".encode()).hexdigest()
            url = f"{self.service_url}/files{file_path}?expires={expiry}&signature={signature}"
            
            logging.info(f"Real service: Generated URL for {file_path}")
            return url
        
        return None
    
    def get_connection_count(self) -> int:
        """Get number of connections made to real service."""
        return self.connection_count


# Virtual Proxy (Lazy Loading)
class VirtualCloudStorageProxy(CloudStorageService):
    """
    Virtual proxy that implements lazy loading for the cloud storage service.
    Only creates the real service when actually needed.
    """
    
    def __init__(self, service_url: str, api_key: str):
        self._service_url = service_url
        self._api_key = api_key
        self._real_service: Optional[RealCloudStorageService] = None
        self._service_lock = Lock()
    
    def _get_real_service(self) -> RealCloudStorageService:
        """Lazy initialization of real service."""
        if self._real_service is None:
            with self._service_lock:
                if self._real_service is None:  # Double-checked locking
                    logging.info("Virtual proxy: Initializing real cloud storage service")
                    self._real_service = RealCloudStorageService(self._service_url, self._api_key)
        
        return self._real_service
    
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload file through lazy-loaded real service."""
        return self._get_real_service().upload_file(file_path, content, metadata)
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file through lazy-loaded real service."""
        return self._get_real_service().download_file(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file through lazy-loaded real service."""
        return self._get_real_service().delete_file(file_path)
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get metadata through lazy-loaded real service."""
        return self._get_real_service().get_file_metadata(file_path)
    
    def list_files(self, directory: str = "/") -> List[str]:
        """List files through lazy-loaded real service."""
        return self._get_real_service().list_files(directory)
    
    def file_exists(self, file_path: str) -> bool:
        """Check file existence through lazy-loaded real service."""
        return self._get_real_service().file_exists(file_path)
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get file URL through lazy-loaded real service."""
        return self._get_real_service().get_file_url(file_path, expires_in)
    
    def is_service_initialized(self) -> bool:
        """Check if real service has been initialized."""
        return self._real_service is not None


# Protection Proxy (Access Control)
class ProtectionCloudStorageProxy(CloudStorageService):
    """
    Protection proxy that adds access control and security to cloud storage.
    """
    
    def __init__(self, real_service: CloudStorageService):
        self._real_service = real_service
        self._current_user: Optional[User] = None
        self._access_logs: List[AnalyticsData] = []
        self._failed_attempts: Dict[str, int] = {}
        self._banned_users: Set[str] = set()
    
    def authenticate_user(self, user: User) -> bool:
        """Authenticate user for access."""
        if user.user_id in self._banned_users:
            logging.warning(f"Protection proxy: Banned user attempted access: {user.user_id}")
            return False
        
        if user.is_authenticated:
            self._current_user = user
            user.last_login = datetime.now()
            logging.info(f"Protection proxy: User authenticated: {user.username}")
            return True
        
        # Track failed attempts
        self._failed_attempts[user.user_id] = self._failed_attempts.get(user.user_id, 0) + 1
        if self._failed_attempts[user.user_id] >= 3:
            self._banned_users.add(user.user_id)
            logging.warning(f"Protection proxy: User banned after failed attempts: {user.user_id}")
        
        return False
    
    def logout_user(self) -> None:
        """Logout current user."""
        if self._current_user:
            logging.info(f"Protection proxy: User logged out: {self._current_user.username}")
            self._current_user = None
    
    def _check_permission(self, required_permission: AccessLevel, file_path: str) -> bool:
        """Check if current user has required permission."""
        if not self._current_user:
            logging.warning("Protection proxy: No authenticated user")
            return False
        
        # Check user permissions
        if required_permission in self._current_user.permissions:
            return True
        
        # Check file-specific permissions
        metadata = self._real_service.get_file_metadata(file_path)
        if metadata and self._current_user.user_id in metadata.permissions:
            file_permissions = metadata.permissions[self._current_user.user_id]
            if required_permission in file_permissions:
                return True
        
        # Check admin access
        if AccessLevel.ADMIN in self._current_user.permissions:
            return True
        
        # Check if user is file owner
        if metadata and metadata.owner == self._current_user.user_id:
            return True
        
        logging.warning(f"Protection proxy: Access denied for {self._current_user.username} "
                       f"to {file_path} (required: {required_permission.value})")
        return False
    
    def _log_access(self, operation: str, file_path: str, success: bool, 
                   error_message: str = None, file_size: int = None,
                   duration_ms: float = None) -> None:
        """Log access attempt."""
        user_id = self._current_user.user_id if self._current_user else "anonymous"
        
        analytics = AnalyticsData(
            operation=operation,
            user_id=user_id,
            file_path=file_path,
            file_size=file_size,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        self._access_logs.append(analytics)
    
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload file with permission check."""
        start_time = time.time()
        
        if not self._check_permission(AccessLevel.WRITE, file_path):
            self._log_access("upload", file_path, False, "Permission denied")
            return False
        
        # Set owner if not specified
        if self._current_user and not metadata.owner:
            metadata.owner = self._current_user.user_id
        
        result = self._real_service.upload_file(file_path, content, metadata)
        duration_ms = (time.time() - start_time) * 1000
        
        self._log_access("upload", file_path, result, 
                        None if result else "Upload failed", 
                        len(content), duration_ms)
        
        return result
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file with permission check."""
        start_time = time.time()
        
        if not self._check_permission(AccessLevel.READ, file_path):
            self._log_access("download", file_path, False, "Permission denied")
            return None
        
        content = self._real_service.download_file(file_path)
        duration_ms = (time.time() - start_time) * 1000
        
        self._log_access("download", file_path, content is not None,
                        None if content else "Download failed",
                        len(content) if content else None, duration_ms)
        
        return content
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file with permission check."""
        start_time = time.time()
        
        if not self._check_permission(AccessLevel.DELETE, file_path):
            self._log_access("delete", file_path, False, "Permission denied")
            return False
        
        result = self._real_service.delete_file(file_path)
        duration_ms = (time.time() - start_time) * 1000
        
        self._log_access("delete", file_path, result,
                        None if result else "Delete failed",
                        duration_ms=duration_ms)
        
        return result
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get metadata with permission check."""
        if not self._check_permission(AccessLevel.READ, file_path):
            self._log_access("metadata", file_path, False, "Permission denied")
            return None
        
        metadata = self._real_service.get_file_metadata(file_path)
        self._log_access("metadata", file_path, metadata is not None)
        
        return metadata
    
    def list_files(self, directory: str = "/") -> List[str]:
        """List files with permission filtering."""
        if not self._current_user:
            return []
        
        all_files = self._real_service.list_files(directory)
        
        # Filter files based on read permission
        accessible_files = []
        for file_path in all_files:
            if self._check_permission(AccessLevel.READ, file_path):
                accessible_files.append(file_path)
        
        self._log_access("list", directory, True, file_size=len(accessible_files))
        return accessible_files
    
    def file_exists(self, file_path: str) -> bool:
        """Check file existence with permission check."""
        if not self._check_permission(AccessLevel.READ, file_path):
            return False  # Hide existence from unauthorized users
        
        exists = self._real_service.file_exists(file_path)
        self._log_access("exists", file_path, exists)
        
        return exists
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get file URL with permission check."""
        if not self._check_permission(AccessLevel.READ, file_path):
            self._log_access("url", file_path, False, "Permission denied")
            return None
        
        url = self._real_service.get_file_url(file_path, expires_in)
        self._log_access("url", file_path, url is not None)
        
        return url
    
    def get_access_logs(self, limit: int = 100) -> List[AnalyticsData]:
        """Get recent access logs."""
        if self._current_user and AccessLevel.ADMIN in self._current_user.permissions:
            return self._access_logs[-limit:]
        return []
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security statistics."""
        if not (self._current_user and AccessLevel.ADMIN in self._current_user.permissions):
            return {}
        
        total_accesses = len(self._access_logs)
        failed_accesses = sum(1 for log in self._access_logs if not log.success)
        
        return {
            "total_accesses": total_accesses,
            "failed_accesses": failed_accesses,
            "success_rate": (total_accesses - failed_accesses) / max(1, total_accesses) * 100,
            "banned_users": len(self._banned_users),
            "failed_attempts": dict(self._failed_attempts),
            "current_user": self._current_user.username if self._current_user else None
        }


# Caching Proxy
class CachingCloudStorageProxy(CloudStorageService):
    """
    Caching proxy that adds intelligent caching to reduce remote calls.
    """
    
    def __init__(self, real_service: CloudStorageService, 
                 cache_size_mb: int = 100, cache_ttl_seconds: int = 3600):
        self._real_service = real_service
        self._cache_size_bytes = cache_size_mb * 1024 * 1024
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        
        # File content cache
        self._content_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._metadata_cache: Dict[str, Tuple[FileMetadata, datetime]] = {}
        self._list_cache: Dict[str, Tuple[List[str], datetime]] = {}
        
        # Cache statistics
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_lock = Lock()
        
        # Current cache size
        self._current_cache_size = 0
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid."""
        return datetime.now() - timestamp < self._cache_ttl
    
    def _evict_if_needed(self, new_content_size: int) -> None:
        """Evict cache entries if space is needed."""
        if self._current_cache_size + new_content_size <= self._cache_size_bytes:
            return
        
        # Sort by access time (LRU eviction)
        cache_items = [(path, content, timestamp) 
                      for path, (content, timestamp) in self._content_cache.items()]
        cache_items.sort(key=lambda x: x[2])  # Sort by timestamp
        
        # Remove oldest entries
        for path, content, _ in cache_items:
            if self._current_cache_size + new_content_size <= self._cache_size_bytes:
                break
            
            del self._content_cache[path]
            self._current_cache_size -= len(content)
            logging.info(f"Caching proxy: Evicted {path} from cache")
    
    def _cache_content(self, file_path: str, content: bytes) -> None:
        """Cache file content."""
        with self._cache_lock:
            # Check if we should cache this file
            if len(content) > self._cache_size_bytes * 0.1:  # Don't cache files > 10% of cache size
                return
            
            self._evict_if_needed(len(content))
            
            if file_path in self._content_cache:
                # Remove old entry
                old_content, _ = self._content_cache[file_path]
                self._current_cache_size -= len(old_content)
            
            self._content_cache[file_path] = (content, datetime.now())
            self._current_cache_size += len(content)
            
            logging.info(f"Caching proxy: Cached {file_path} ({len(content)} bytes)")
    
    def _get_cached_content(self, file_path: str) -> Optional[bytes]:
        """Get content from cache if valid."""
        with self._cache_lock:
            if file_path in self._content_cache:
                content, timestamp = self._content_cache[file_path]
                if self._is_cache_valid(timestamp):
                    self._cache_hits += 1
                    logging.info(f"Caching proxy: Cache hit for {file_path}")
                    return content
                else:
                    # Remove expired entry
                    del self._content_cache[file_path]
                    self._current_cache_size -= len(content)
            
            self._cache_misses += 1
            return None
    
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload file and invalidate cache."""
        result = self._real_service.upload_file(file_path, content, metadata)
        
        if result:
            # Cache the uploaded content
            self._cache_content(file_path, content)
            
            # Update metadata cache
            with self._cache_lock:
                self._metadata_cache[file_path] = (metadata, datetime.now())
                
                # Invalidate directory listing cache
                directory = os.path.dirname(file_path) or "/"
                if directory in self._list_cache:
                    del self._list_cache[directory]
        
        return result
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file with caching."""
        # Try cache first
        cached_content = self._get_cached_content(file_path)
        if cached_content is not None:
            return cached_content
        
        # Cache miss - get from real service
        content = self._real_service.download_file(file_path)
        if content is not None:
            self._cache_content(file_path, content)
        
        return content
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file and invalidate cache."""
        result = self._real_service.delete_file(file_path)
        
        if result:
            with self._cache_lock:
                # Remove from caches
                if file_path in self._content_cache:
                    content, _ = self._content_cache[file_path]
                    self._current_cache_size -= len(content)
                    del self._content_cache[file_path]
                
                if file_path in self._metadata_cache:
                    del self._metadata_cache[file_path]
                
                # Invalidate directory listing cache
                directory = os.path.dirname(file_path) or "/"
                if directory in self._list_cache:
                    del self._list_cache[directory]
        
        return result
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get metadata with caching."""
        with self._cache_lock:
            if file_path in self._metadata_cache:
                metadata, timestamp = self._metadata_cache[file_path]
                if self._is_cache_valid(timestamp):
                    self._cache_hits += 1
                    return metadata
                else:
                    del self._metadata_cache[file_path]
        
        # Cache miss
        self._cache_misses += 1
        metadata = self._real_service.get_file_metadata(file_path)
        
        if metadata:
            with self._cache_lock:
                self._metadata_cache[file_path] = (metadata, datetime.now())
        
        return metadata
    
    def list_files(self, directory: str = "/") -> List[str]:
        """List files with caching."""
        with self._cache_lock:
            if directory in self._list_cache:
                file_list, timestamp = self._list_cache[directory]
                if self._is_cache_valid(timestamp):
                    self._cache_hits += 1
                    return file_list
                else:
                    del self._list_cache[directory]
        
        # Cache miss
        self._cache_misses += 1
        file_list = self._real_service.list_files(directory)
        
        with self._cache_lock:
            self._list_cache[directory] = (file_list, datetime.now())
        
        return file_list
    
    def file_exists(self, file_path: str) -> bool:
        """Check file existence (use metadata cache)."""
        # Try metadata cache first
        if self.get_file_metadata(file_path) is not None:
            return True
        
        return self._real_service.file_exists(file_path)
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get file URL (not cached due to expiration)."""
        return self._real_service.get_file_url(file_path, expires_in)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / max(1, total_requests)) * 100
        
        with self._cache_lock:
            return {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_rate_percent": hit_rate,
                "cached_files": len(self._content_cache),
                "cache_size_bytes": self._current_cache_size,
                "cache_size_mb": self._current_cache_size / (1024 * 1024),
                "cache_utilization_percent": (self._current_cache_size / self._cache_size_bytes) * 100
            }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self._cache_lock:
            self._content_cache.clear()
            self._metadata_cache.clear()
            self._list_cache.clear()
            self._current_cache_size = 0
            logging.info("Caching proxy: Cache cleared")


# Smart Proxy (Additional Functionality)
class SmartCloudStorageProxy(CloudStorageService):
    """
    Smart proxy that adds compression, encryption, and analytics.
    """
    
    def __init__(self, real_service: CloudStorageService):
        self._real_service = real_service
        self._analytics: List[AnalyticsData] = []
        self._compression_stats = {"compressed": 0, "uncompressed": 0, "savings_bytes": 0}
        self._encryption_key = "default_encryption_key_12345"  # In practice, use proper key management
    
    def _compress_content(self, content: bytes, compression_type: CompressionType) -> bytes:
        """Compress content using specified algorithm."""
        if compression_type == CompressionType.GZIP:
            return gzip.compress(content)
        elif compression_type == CompressionType.LZMA:
            import lzma
            return lzma.compress(content)
        else:
            return content
    
    def _decompress_content(self, content: bytes, compression_type: CompressionType) -> bytes:
        """Decompress content using specified algorithm."""
        if compression_type == CompressionType.GZIP:
            return gzip.decompress(content)
        elif compression_type == CompressionType.LZMA:
            import lzma
            return lzma.decompress(content)
        else:
            return content
    
    def _encrypt_content(self, content: bytes) -> bytes:
        """Simple encryption (in practice, use proper encryption)."""
        # Simple XOR encryption for demonstration
        key_bytes = self._encryption_key.encode()
        encrypted = bytearray()
        
        for i, byte in enumerate(content):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return bytes(encrypted)
    
    def _decrypt_content(self, content: bytes) -> bytes:
        """Simple decryption."""
        # XOR encryption is symmetric
        return self._encrypt_content(content)
    
    def _should_compress(self, content: bytes, file_type: FileType) -> bool:
        """Determine if content should be compressed."""
        # Don't compress already compressed formats
        if file_type in [FileType.IMAGE, FileType.VIDEO, FileType.ARCHIVE]:
            return False
        
        # Only compress files larger than 1KB
        return len(content) > 1024
    
    def _analyze_upload(self, file_path: str, original_size: int, final_size: int,
                       compressed: bool, encrypted: bool) -> None:
        """Record analytics for upload operation."""
        analytics = AnalyticsData(
            operation="smart_upload",
            user_id="system",
            file_path=file_path,
            file_size=original_size
        )
        
        analytics.metadata = {
            "compressed": compressed,
            "encrypted": encrypted,
            "original_size": original_size,
            "final_size": final_size,
            "compression_ratio": final_size / original_size if compressed else 1.0
        }
        
        self._analytics.append(analytics)
    
    def upload_file(self, file_path: str, content: bytes, metadata: FileMetadata) -> bool:
        """Upload with compression and encryption."""
        original_size = len(content)
        processed_content = content
        compressed = False
        encrypted = False
        
        # Apply compression if beneficial
        if self._should_compress(content, metadata.file_type):
            compression_type = CompressionType.GZIP
            compressed_content = self._compress_content(content, compression_type)
            
            # Only use compression if it actually saves space
            if len(compressed_content) < len(content) * 0.9:  # At least 10% savings
                processed_content = compressed_content
                metadata.compression = compression_type
                compressed = True
                
                savings = len(content) - len(compressed_content)
                self._compression_stats["compressed"] += 1
                self._compression_stats["savings_bytes"] += savings
                
                logging.info(f"Smart proxy: Compressed {file_path} "
                           f"({original_size} -> {len(compressed_content)} bytes, "
                           f"{savings/original_size*100:.1f}% savings)")
            else:
                self._compression_stats["uncompressed"] += 1
        else:
            self._compression_stats["uncompressed"] += 1
        
        # Apply encryption if specified
        if metadata.encryption_key:
            processed_content = self._encrypt_content(processed_content)
            encrypted = True
            logging.info(f"Smart proxy: Encrypted {file_path}")
        
        # Update metadata with final size
        metadata.file_size = len(processed_content)
        
        # Upload processed content
        result = self._real_service.upload_file(file_path, processed_content, metadata)
        
        # Record analytics
        self._analyze_upload(file_path, original_size, len(processed_content), compressed, encrypted)
        
        return result
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download with decompression and decryption."""
        # Get file content and metadata
        content = self._real_service.download_file(file_path)
        if content is None:
            return None
        
        metadata = self._real_service.get_file_metadata(file_path)
        if metadata is None:
            return content
        
        processed_content = content
        
        # Apply decryption if needed
        if metadata.encryption_key:
            processed_content = self._decrypt_content(processed_content)
            logging.info(f"Smart proxy: Decrypted {file_path}")
        
        # Apply decompression if needed
        if metadata.compression != CompressionType.NONE:
            processed_content = self._decompress_content(processed_content, metadata.compression)
            logging.info(f"Smart proxy: Decompressed {file_path} "
                        f"({len(content)} -> {len(processed_content)} bytes)")
        
        return processed_content
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file (passthrough)."""
        return self._real_service.delete_file(file_path)
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get metadata (passthrough)."""
        return self._real_service.get_file_metadata(file_path)
    
    def list_files(self, directory: str = "/") -> List[str]:
        """List files (passthrough)."""
        return self._real_service.list_files(directory)
    
    def file_exists(self, file_path: str) -> bool:
        """Check file existence (passthrough)."""
        return self._real_service.file_exists(file_path)
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get file URL (passthrough)."""
        return self._real_service.get_file_url(file_path, expires_in)
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """Get compression performance statistics."""
        total_files = self._compression_stats["compressed"] + self._compression_stats["uncompressed"]
        compression_rate = (self._compression_stats["compressed"] / max(1, total_files)) * 100
        
        return {
            "total_files_processed": total_files,
            "files_compressed": self._compression_stats["compressed"],
            "files_uncompressed": self._compression_stats["uncompressed"],
            "compression_rate_percent": compression_rate,
            "total_savings_bytes": self._compression_stats["savings_bytes"],
            "total_savings_mb": self._compression_stats["savings_bytes"] / (1024 * 1024)
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        if not self._analytics:
            return {}
        
        total_uploads = len(self._analytics)
        compressed_uploads = sum(1 for a in self._analytics if a.metadata.get("compressed", False))
        encrypted_uploads = sum(1 for a in self._analytics if a.metadata.get("encrypted", False))
        
        avg_compression_ratio = sum(
            a.metadata.get("compression_ratio", 1.0) for a in self._analytics
        ) / total_uploads
        
        return {
            "total_operations": total_uploads,
            "compressed_operations": compressed_uploads,
            "encrypted_operations": encrypted_uploads,
            "average_compression_ratio": avg_compression_ratio,
            "compression_usage_percent": (compressed_uploads / total_uploads) * 100,
            "encryption_usage_percent": (encrypted_uploads / total_uploads) * 100
        }


# Demonstration Function
def demonstrate_proxy_pattern():
    """Demonstrate the Proxy pattern with cloud storage system."""
    
    print("=== Cloud Storage System - Proxy Pattern Demo ===\n")
    
    # 1. Virtual Proxy Demo (Lazy Loading)
    print("1. Virtual Proxy (Lazy Loading):")
    print("-" * 40)
    
    virtual_proxy = VirtualCloudStorageProxy("https://api.cloudstorage.com", "api_key_123")
    print(f"Service initialized: {virtual_proxy.is_service_initialized()}")
    
    # First operation triggers lazy loading
    metadata = FileMetadata("test.txt", 0, FileType.DOCUMENT)
    virtual_proxy.upload_file("/documents/test.txt", b"Hello World", metadata)
    print(f"Service initialized after operation: {virtual_proxy.is_service_initialized()}")
    print()
    
    # 2. Protection Proxy Demo (Access Control)
    print("2. Protection Proxy (Access Control):")
    print("-" * 45)
    
    # Create real service for protection proxy
    real_service = RealCloudStorageService("https://secure.cloudstorage.com", "secure_key")
    protection_proxy = ProtectionCloudStorageProxy(real_service)
    
    # Create users with different permissions
    admin_user = User("admin", "admin_user", ["admin"], [AccessLevel.ADMIN], True)
    regular_user = User("user1", "regular_user", ["user"], [AccessLevel.READ, AccessLevel.WRITE], True)
    readonly_user = User("user2", "readonly_user", ["readonly"], [AccessLevel.READ], True)
    
    # Demonstrate access control
    print("Testing access control:")
    
    # Admin user can do everything
    protection_proxy.authenticate_user(admin_user)
    admin_metadata = FileMetadata("admin_file.txt", 0, FileType.DOCUMENT, owner="admin")
    success = protection_proxy.upload_file("/admin/config.txt", b"Admin config data", admin_metadata)
    print(f"Admin upload: {success}")
    
    # Regular user operations
    protection_proxy.authenticate_user(regular_user)
    user_metadata = FileMetadata("user_file.txt", 0, FileType.DOCUMENT, owner="user1")
    success = protection_proxy.upload_file("/users/document.txt", b"User document", user_metadata)
    print(f"Regular user upload: {success}")
    
    # Read-only user trying to upload (should fail)
    protection_proxy.authenticate_user(readonly_user)
    readonly_metadata = FileMetadata("readonly_file.txt", 0, FileType.DOCUMENT, owner="user2")
    success = protection_proxy.upload_file("/users/readonly.txt", b"Should fail", readonly_metadata)
    print(f"Read-only user upload: {success}")
    
    # Show security report
    protection_proxy.authenticate_user(admin_user)
    security_report = protection_proxy.get_security_report()
    print(f"Security report: {security_report['total_accesses']} total accesses, "
          f"{security_report['success_rate']:.1f}% success rate")
    print()
    
    # 3. Caching Proxy Demo
    print("3. Caching Proxy (Performance Optimization):")
    print("-" * 50)
    
    caching_proxy = CachingCloudStorageProxy(real_service, cache_size_mb=10, cache_ttl_seconds=300)
    
    # Upload files to cache
    large_content = b"Large file content " * 1000  # ~19KB
    cache_metadata = FileMetadata("cached_file.txt", len(large_content), FileType.DOCUMENT)
    
    caching_proxy.upload_file("/cache/large_file.txt", large_content, cache_metadata)
    
    # First download (cache miss)
    print("First download (cache miss):")
    start_time = time.time()
    content1 = caching_proxy.download_file("/cache/large_file.txt")
    time1 = time.time() - start_time
    print(f"Downloaded {len(content1)} bytes in {time1*1000:.1f}ms")
    
    # Second download (cache hit)
    print("Second download (cache hit):")
    start_time = time.time()
    content2 = caching_proxy.download_file("/cache/large_file.txt")
    time2 = time.time() - start_time
    print(f"Downloaded {len(content2)} bytes in {time2*1000:.1f}ms")
    
    cache_stats = caching_proxy.get_cache_statistics()
    print(f"Cache performance: {cache_stats['hit_rate_percent']:.1f}% hit rate, "
          f"{cache_stats['cache_size_mb']:.2f}MB used")
    print()
    
    # 4. Smart Proxy Demo (Additional Functionality)
    print("4. Smart Proxy (Compression & Encryption):")
    print("-" * 50)
    
    smart_proxy = SmartCloudStorageProxy(real_service)
    
    # Upload compressible content
    compressible_content = b"This is repeated text. " * 500  # Highly compressible
    smart_metadata = FileMetadata("compressible.txt", len(compressible_content), FileType.DOCUMENT)
    
    print(f"Original content size: {len(compressible_content)} bytes")
    smart_proxy.upload_file("/smart/compressible.txt", compressible_content, smart_metadata)
    
    # Upload with encryption
    secret_content = b"This is secret data that should be encrypted"
    encrypted_metadata = FileMetadata("secret.txt", len(secret_content), FileType.DOCUMENT)
    encrypted_metadata.encryption_key = "secret_key_123"
    
    smart_proxy.upload_file("/smart/secret.txt", secret_content, encrypted_metadata)
    
    # Download and verify
    downloaded_compressible = smart_proxy.download_file("/smart/compressible.txt")
    downloaded_secret = smart_proxy.download_file("/smart/secret.txt")
    
    print(f"Downloaded compressible: {len(downloaded_compressible)} bytes "
          f"(matches original: {downloaded_compressible == compressible_content})")
    print(f"Downloaded secret: {len(downloaded_secret)} bytes "
          f"(matches original: {downloaded_secret == secret_content})")
    
    # Show smart proxy statistics
    compression_stats = smart_proxy.get_compression_statistics()
    print(f"Compression stats: {compression_stats['compression_rate_percent']:.1f}% of files compressed, "
          f"{compression_stats['total_savings_mb']:.2f}MB saved")
    
    analytics = smart_proxy.get_analytics_summary()
    print(f"Analytics: {analytics['compression_usage_percent']:.1f}% compression rate, "
          f"{analytics['encryption_usage_percent']:.1f}% encryption rate")
    print()
    
    # 5. Proxy Chain Demo (Combining Multiple Proxies)
    print("5. Proxy Chain (Multiple Proxies Combined):")
    print("-" * 50)
    
    # Create a chain: Real Service -> Smart -> Caching -> Protection
    base_service = RealCloudStorageService("https://api.example.com", "key123")
    smart_layer = SmartCloudStorageProxy(base_service)
    cache_layer = CachingCloudStorageProxy(smart_layer, cache_size_mb=5)
    protection_layer = ProtectionCloudStorageProxy(cache_layer)
    
    # Authenticate user
    protection_layer.authenticate_user(regular_user)
    
    # Upload through the proxy chain
    chain_content = b"Content processed through proxy chain " * 100
    chain_metadata = FileMetadata("chain_file.txt", len(chain_content), FileType.DOCUMENT)
    
    print("Processing through proxy chain:")
    print("User -> Protection -> Caching -> Smart -> Real Service")
    
    success = protection_layer.upload_file("/chain/test.txt", chain_content, chain_metadata)
    print(f"Upload through chain: {success}")
    
    # Download through the chain (should hit cache)
    downloaded_chain = protection_layer.download_file("/chain/test.txt")
    print(f"Download through chain: {len(downloaded_chain)} bytes")
    
    # Show combined statistics
    chain_cache_stats = cache_layer.get_cache_statistics()
    chain_compression_stats = smart_layer.get_compression_statistics()
    
    print(f"Chain cache hit rate: {chain_cache_stats['hit_rate_percent']:.1f}%")
    print(f"Chain compression savings: {chain_compression_stats['total_savings_mb']:.2f}MB")
    print()
    
    # 6. Performance Comparison
    print("6. Performance Comparison:")
    print("-" * 35)
    
    # Compare direct access vs proxy access
    direct_service = RealCloudStorageService("https://direct.api.com", "direct_key")
    
    test_content = b"Performance test content " * 50
    test_metadata = FileMetadata("perf_test.txt", len(test_content), FileType.DOCUMENT)
    
    # Direct access
    start_time = time.time()
    direct_service.upload_file("/perf/direct.txt", test_content, test_metadata)
    direct_service.download_file("/perf/direct.txt")
    direct_time = time.time() - start_time
    
    # Proxy access (with caching)
    start_time = time.time()
    cache_layer.upload_file("/perf/proxy.txt", test_content, test_metadata)
    cache_layer.download_file("/perf/proxy.txt")  # Cache miss
    cache_layer.download_file("/perf/proxy.txt")  # Cache hit
    proxy_time = time.time() - start_time
    
    print(f"Direct access time: {direct_time*1000:.1f}ms")
    print(f"Proxy access time: {proxy_time*1000:.1f}ms")
    print(f"Real service connections: {direct_service.get_connection_count()}")
    print()
    
    print("=== Proxy Pattern Benefits Demonstrated ===")
    print("✓ Lazy loading reduces initial overhead")
    print("✓ Access control provides security")
    print("✓ Caching improves performance")
    print("✓ Smart proxies add functionality transparently")
    print("✓ Proxy chains enable sophisticated behavior")
    print("✓ Transparent to client code")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the demonstration
    demonstrate_proxy_pattern()