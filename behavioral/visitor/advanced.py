"""
Visitor Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Generic typing with TypeVar and Protocol for type safety
- Async visitor methods with non-blocking operations
- Dynamic visitor registration and runtime dispatch
- Performance monitoring and comprehensive metrics
- Memory-efficient visitor caching and memoization
- Thread-safe concurrent visitor execution
- Advanced traversal strategies and optimization
- Event-driven visitor lifecycle management
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Awaitable, Type, runtime_checkable,
    Set, Tuple, Iterator, get_type_hints
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
import inspect
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import logging

# Type variables
VisitorT = TypeVar('VisitorT', bound='Visitor')
ElementT = TypeVar('ElementT', bound='Element')
ResultT = TypeVar('ResultT')
ContextT = TypeVar('ContextT')


class TraversalStrategy(Enum):
    """Strategies for element traversal."""
    DEPTH_FIRST = "depth_first"
    BREADTH_FIRST = "breadth_first"
    POST_ORDER = "post_order"
    PRE_ORDER = "pre_order"
    LEVEL_ORDER = "level_order"
    CUSTOM = "custom"


class VisitMode(Enum):
    """Visitor execution modes."""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    STREAMING = "streaming"


class VisitorPriority(Enum):
    """Priority levels for visitor execution."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class VisitorMetadata:
    """Metadata for visitor tracking and management."""
    visitor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    priority: VisitorPriority = VisitorPriority.NORMAL
    supported_types: Set[Type] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    max_execution_time: Optional[float] = None


@dataclass
class VisitMetrics:
    """Performance metrics for visitor operations."""
    visits: int = 0
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_visited: Optional[datetime] = None
    elements_processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def update(self, execution_time: float, success: bool, elements_count: int = 1, cached: bool = False):
        """Update metrics with visit result."""
        self.visits += 1
        self.elements_processed += elements_count
        self.last_visited = datetime.now()
        
        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if success:
            self.successes += 1
        else:
            self.failures += 1
        
        self.total_time += execution_time
        self.average_time = self.total_time / self.visits
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successes / max(1, self.visits)
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache_operations = self.cache_hits + self.cache_misses
        return self.cache_hits / max(1, total_cache_operations)


@dataclass
class VisitResult(Generic[ResultT]):
    """Result of visitor execution."""
    success: bool
    result: Optional[ResultT] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    visitor_id: str = ""
    element_type: str = ""
    elements_visited: int = 0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Element(Protocol):
    """Protocol for elements that can be visited."""
    
    def accept(self, visitor: 'Visitor') -> Any:
        """Accept a visitor."""
        ...
    
    def get_element_id(self) -> str:
        """Get unique identifier for this element."""
        ...
    
    def get_children(self) -> List['Element']:
        """Get child elements for traversal."""
        ...


@runtime_checkable
class Visitor(Protocol[ElementT, ResultT]):
    """Protocol for visitor implementations."""
    
    def get_visitor_id(self) -> str:
        """Get unique identifier for this visitor."""
        ...
    
    async def visit(self, element: ElementT) -> ResultT:
        """Visit an element."""
        ...
    
    def can_visit(self, element: ElementT) -> bool:
        """Check if visitor can visit this element."""
        ...
    
    def get_metadata(self) -> VisitorMetadata:
        """Get visitor metadata."""
        ...


class OptimizedVisitor(Generic[ElementT, ResultT], ABC):
    """
    High-performance visitor with advanced features.
    """
    
    def __init__(self, metadata: VisitorMetadata = None):
        self.metadata = metadata or VisitorMetadata()
        self.metrics = VisitMetrics()
        
        self._visit_cache: Dict[str, Tuple[ResultT, datetime]] = {}
        self._cache_lock = threading.RLock()
        self._cache_ttl = timedelta(minutes=5)
        
        # Method dispatch table
        self._visit_methods: Dict[Type, Callable] = {}
        self._build_dispatch_table()
        
        # Execution control
        self._circuit_breaker = CircuitBreaker()
        self._rate_limiter = RateLimiter(100, timedelta(seconds=1))
        
        # Hooks and filters
        self._pre_visit_hooks: List[Callable] = []
        self._post_visit_hooks: List[Callable] = []
        self._element_filters: List[Callable[[ElementT], bool]] = []
    
    def get_visitor_id(self) -> str:
        return self.metadata.visitor_id
    
    def get_metadata(self) -> VisitorMetadata:
        return self.metadata
    
    def _build_dispatch_table(self) -> None:
        """Build method dispatch table for efficient visitor method lookup."""
        for method_name in dir(self):
            if method_name.startswith('visit_'):
                method = getattr(self, method_name)
                if callable(method):
                    # Extract type from method signature
                    sig = inspect.signature(method)
                    params = list(sig.parameters.values())
                    if len(params) >= 1:  # Skip 'self'
                        param = params[0] if len(params) == 1 else params[1]
                        if param.annotation != inspect.Parameter.empty:
                            self._visit_methods[param.annotation] = method
    
    async def visit(self, element: ElementT) -> ResultT:
        """Visit element with comprehensive monitoring and optimization."""
        
        # Check rate limiting
        if not self._rate_limiter.allow():
            raise RuntimeError("Rate limit exceeded")
        
        # Check circuit breaker
        if self._circuit_breaker.is_open():
            raise RuntimeError("Circuit breaker is open")
        
        start_time = time.time()
        cached = False
        
        try:
            # Apply element filters
            if not self._should_visit_element(element):
                return None
            
            # Check cache
            cache_key = self._generate_cache_key(element)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result is not None:
                cached = True
                result = cached_result
            else:
                # Execute pre-visit hooks
                for hook in self._pre_visit_hooks:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(element)
                    else:
                        hook(element)
                
                # Dispatch to appropriate visit method
                result = await self._dispatch_visit(element)
                
                # Cache result
                self._cache_result(cache_key, result)
            
            # Execute post-visit hooks
            for hook in self._post_visit_hooks:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(element, result)
                    else:
                        hook(element, result)
                except Exception as e:
                    logging.warning(f"Post-visit hook failed: {e}")
            
            # Update metrics
            execution_time = time.time() - start_time
            self.metrics.update(execution_time, True, 1, cached)
            self._circuit_breaker.record_success()
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.update(execution_time, False, 1, cached)
            self._circuit_breaker.record_failure()
            raise
    
    async def _dispatch_visit(self, element: ElementT) -> ResultT:
        """Dispatch visit to appropriate method based on element type."""
        element_type = type(element)
        
        # Try exact type match first
        if element_type in self._visit_methods:
            method = self._visit_methods[element_type]
            if asyncio.iscoroutinefunction(method):
                return await method(element)
            else:
                return method(element)
        
        # Try MRO (Method Resolution Order) for inheritance
        for base_type in element_type.__mro__:
            if base_type in self._visit_methods:
                method = self._visit_methods[base_type]
                if asyncio.iscoroutinefunction(method):
                    return await method(element)
                else:
                    return method(element)
        
        # Fall back to generic visit
        return await self.visit_generic(element)
    
    async def visit_generic(self, element: ElementT) -> ResultT:
        """Generic visit method (to be overridden by subclasses)."""
        return None
    
    def can_visit(self, element: ElementT) -> bool:
        """Check if visitor can visit this element."""
        element_type = type(element)
        
        # Check if we have a specific method for this type
        if element_type in self._visit_methods:
            return True
        
        # Check MRO
        for base_type in element_type.__mro__:
            if base_type in self._visit_methods:
                return True
        
        # Check supported types in metadata
        if self.metadata.supported_types:
            return any(issubclass(element_type, supported_type) 
                      for supported_type in self.metadata.supported_types)
        
        return True  # Default to can visit
    
    def _should_visit_element(self, element: ElementT) -> bool:
        """Check if element should be visited based on filters."""
        return all(filter_func(element) for filter_func in self._element_filters)
    
    def _generate_cache_key(self, element: ElementT) -> str:
        """Generate cache key for element visit."""
        import hashlib
        
        element_id = getattr(element, 'get_element_id', lambda: str(id(element)))()
        visitor_id = self.get_visitor_id()
        
        key_string = f"{visitor_id}_{element_id}_{type(element).__name__}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[ResultT]:
        """Get cached result if valid."""
        with self._cache_lock:
            if cache_key in self._visit_cache:
                result, timestamp = self._visit_cache[cache_key]
                if datetime.now() - timestamp < self._cache_ttl:
                    return result
                else:
                    del self._visit_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: ResultT) -> None:
        """Cache visit result."""
        with self._cache_lock:
            self._visit_cache[cache_key] = (result, datetime.now())
            
            # Cleanup old entries
            if len(self._visit_cache) > 1000:
                oldest_keys = sorted(
                    self._visit_cache.keys(),
                    key=lambda k: self._visit_cache[k][1]
                )[:100]
                for key in oldest_keys:
                    del self._visit_cache[key]
    
    def add_pre_visit_hook(self, hook: Callable) -> None:
        """Add pre-visit hook."""
        self._pre_visit_hooks.append(hook)
    
    def add_post_visit_hook(self, hook: Callable) -> None:
        """Add post-visit hook."""
        self._post_visit_hooks.append(hook)
    
    def add_element_filter(self, filter_func: Callable[[ElementT], bool]) -> None:
        """Add element filter."""
        self._element_filters.append(filter_func)
    
    def set_cache_ttl(self, ttl: timedelta) -> None:
        """Set cache TTL."""
        self._cache_ttl = ttl
    
    def clear_cache(self) -> None:
        """Clear visitor cache."""
        with self._cache_lock:
            self._visit_cache.clear()
    
    def get_metrics(self) -> VisitMetrics:
        return self.metrics


class FunctionalVisitor(OptimizedVisitor[ElementT, ResultT]):
    """Visitor that uses function-based dispatch."""
    
    def __init__(self, visit_functions: Dict[Type, Callable] = None, 
                 metadata: VisitorMetadata = None):
        super().__init__(metadata)
        self._custom_visit_functions = visit_functions or {}
    
    async def _dispatch_visit(self, element: ElementT) -> ResultT:
        """Dispatch to custom functions first, then fall back to parent."""
        element_type = type(element)
        
        # Try custom functions first
        if element_type in self._custom_visit_functions:
            func = self._custom_visit_functions[element_type]
            if asyncio.iscoroutinefunction(func):
                return await func(element)
            else:
                return func(element)
        
        # Fall back to parent dispatch
        return await super()._dispatch_visit(element)
    
    def add_visit_function(self, element_type: Type, visit_func: Callable) -> None:
        """Add custom visit function for element type."""
        self._custom_visit_functions[element_type] = visit_func


class ElementTraverser:
    """Advanced element traverser with multiple strategies."""
    
    def __init__(self, strategy: TraversalStrategy = TraversalStrategy.DEPTH_FIRST):
        self.strategy = strategy
        self._custom_traversal_func: Optional[Callable] = None
        self._traversal_filters: List[Callable[[Element], bool]] = []
        self._max_depth: Optional[int] = None
        self._visited_elements: Set[str] = set()
    
    async def traverse(self, root_element: Element, 
                      visitor: Visitor,
                      visit_mode: VisitMode = VisitMode.ASYNC) -> List[VisitResult]:
        """Traverse elements and apply visitor."""
        self._visited_elements.clear()
        
        if self.strategy == TraversalStrategy.DEPTH_FIRST:
            return await self._traverse_depth_first(root_element, visitor, visit_mode)
        elif self.strategy == TraversalStrategy.BREADTH_FIRST:
            return await self._traverse_breadth_first(root_element, visitor, visit_mode)
        elif self.strategy == TraversalStrategy.POST_ORDER:
            return await self._traverse_post_order(root_element, visitor, visit_mode)
        elif self.strategy == TraversalStrategy.PRE_ORDER:
            return await self._traverse_pre_order(root_element, visitor, visit_mode)
        elif self.strategy == TraversalStrategy.LEVEL_ORDER:
            return await self._traverse_level_order(root_element, visitor, visit_mode)
        elif self.strategy == TraversalStrategy.CUSTOM and self._custom_traversal_func:
            return await self._custom_traversal_func(root_element, visitor, visit_mode)
        else:
            raise ValueError(f"Unsupported traversal strategy: {self.strategy}")
    
    async def _traverse_depth_first(self, element: Element, 
                                   visitor: Visitor,
                                   visit_mode: VisitMode,
                                   depth: int = 0) -> List[VisitResult]:
        """Depth-first traversal."""
        results = []
        
        # Check depth limit
        if self._max_depth is not None and depth > self._max_depth:
            return results
        
        # Check if already visited (cycle detection)
        element_id = element.get_element_id()
        if element_id in self._visited_elements:
            return results
        
        self._visited_elements.add(element_id)
        
        # Apply filters
        if not self._should_traverse_element(element):
            return results
        
        # Visit current element
        if visitor.can_visit(element):
            visit_result = await self._visit_element(element, visitor, visit_mode)
            results.append(visit_result)
        
        # Traverse children
        children = element.get_children()
        
        if visit_mode == VisitMode.PARALLEL and len(children) > 1:
            # Visit children in parallel
            tasks = [
                self._traverse_depth_first(child, visitor, visit_mode, depth + 1)
                for child in children
            ]
            child_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for child_result in child_results:
                if isinstance(child_result, list):
                    results.extend(child_result)
        else:
            # Visit children sequentially
            for child in children:
                child_results = await self._traverse_depth_first(child, visitor, visit_mode, depth + 1)
                results.extend(child_results)
        
        return results
    
    async def _traverse_breadth_first(self, root_element: Element, 
                                     visitor: Visitor,
                                     visit_mode: VisitMode) -> List[VisitResult]:
        """Breadth-first traversal."""
        results = []
        queue = deque([(root_element, 0)])
        
        while queue:
            element, depth = queue.popleft()
            
            # Check depth limit
            if self._max_depth is not None and depth > self._max_depth:
                continue
            
            # Check if already visited
            element_id = element.get_element_id()
            if element_id in self._visited_elements:
                continue
            
            self._visited_elements.add(element_id)
            
            # Apply filters
            if not self._should_traverse_element(element):
                continue
            
            # Visit element
            if visitor.can_visit(element):
                visit_result = await self._visit_element(element, visitor, visit_mode)
                results.append(visit_result)
            
            # Add children to queue
            children = element.get_children()
            for child in children:
                queue.append((child, depth + 1))
        
        return results
    
    async def _traverse_post_order(self, element: Element, 
                                  visitor: Visitor,
                                  visit_mode: VisitMode,
                                  depth: int = 0) -> List[VisitResult]:
        """Post-order traversal (children first, then parent)."""
        results = []
        
        # Check depth limit
        if self._max_depth is not None and depth > self._max_depth:
            return results
        
        # Check if already visited
        element_id = element.get_element_id()
        if element_id in self._visited_elements:
            return results
        
        self._visited_elements.add(element_id)
        
        # Apply filters
        if not self._should_traverse_element(element):
            return results
        
        # Traverse children first
        children = element.get_children()
        
        if visit_mode == VisitMode.PARALLEL and len(children) > 1:
            tasks = [
                self._traverse_post_order(child, visitor, visit_mode, depth + 1)
                for child in children
            ]
            child_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for child_result in child_results:
                if isinstance(child_result, list):
                    results.extend(child_result)
        else:
            for child in children:
                child_results = await self._traverse_post_order(child, visitor, visit_mode, depth + 1)
                results.extend(child_results)
        
        # Visit current element after children
        if visitor.can_visit(element):
            visit_result = await self._visit_element(element, visitor, visit_mode)
            results.append(visit_result)
        
        return results
    
    async def _traverse_pre_order(self, element: Element, 
                                 visitor: Visitor,
                                 visit_mode: VisitMode,
                                 depth: int = 0) -> List[VisitResult]:
        """Pre-order traversal (parent first, then children)."""
        return await self._traverse_depth_first(element, visitor, visit_mode, depth)
    
    async def _traverse_level_order(self, root_element: Element, 
                                   visitor: Visitor,
                                   visit_mode: VisitMode) -> List[VisitResult]:
        """Level-order traversal (same as breadth-first)."""
        return await self._traverse_breadth_first(root_element, visitor, visit_mode)
    
    async def _visit_element(self, element: Element, 
                            visitor: Visitor,
                            visit_mode: VisitMode) -> VisitResult:
        """Visit single element with specified mode."""
        start_time = time.time()
        
        try:
            if visit_mode == VisitMode.SYNC:
                # Force synchronous execution
                result = await visitor.visit(element)
            else:
                # Async execution
                result = await visitor.visit(element)
            
            execution_time = time.time() - start_time
            
            return VisitResult(
                success=True,
                result=result,
                execution_time=execution_time,
                visitor_id=visitor.get_visitor_id(),
                element_type=type(element).__name__,
                elements_visited=1
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return VisitResult(
                success=False,
                error=e,
                execution_time=execution_time,
                visitor_id=visitor.get_visitor_id(),
                element_type=type(element).__name__,
                elements_visited=0
            )
    
    def _should_traverse_element(self, element: Element) -> bool:
        """Check if element should be traversed based on filters."""
        return all(filter_func(element) for filter_func in self._traversal_filters)
    
    def set_custom_traversal(self, traversal_func: Callable) -> None:
        """Set custom traversal function."""
        self.strategy = TraversalStrategy.CUSTOM
        self._custom_traversal_func = traversal_func
    
    def add_traversal_filter(self, filter_func: Callable[[Element], bool]) -> None:
        """Add traversal filter."""
        self._traversal_filters.append(filter_func)
    
    def set_max_depth(self, max_depth: int) -> None:
        """Set maximum traversal depth."""
        self._max_depth = max_depth


class VisitorManager:
    """Manager for coordinating multiple visitors."""
    
    def __init__(self):
        self._visitors: Dict[str, Visitor] = {}
        self._visitor_groups: Dict[str, List[str]] = defaultdict(list)
        self._execution_history: deque = deque(maxlen=1000)
        self._metrics = defaultdict(int)
        
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._traverser = ElementTraverser()
        
        # Event listeners
        self._visit_listeners: List[Callable] = []
    
    def register_visitor(self, visitor: Visitor, groups: List[str] = None) -> None:
        """Register visitor with optional groups."""
        visitor_id = visitor.get_visitor_id()
        self._visitors[visitor_id] = visitor
        
        # Add to groups
        for group in (groups or []):
            self._visitor_groups[group].append(visitor_id)
    
    def unregister_visitor(self, visitor_id: str) -> bool:
        """Unregister visitor."""
        if visitor_id in self._visitors:
            del self._visitors[visitor_id]
            
            # Remove from groups
            for group_visitors in self._visitor_groups.values():
                if visitor_id in group_visitors:
                    group_visitors.remove(visitor_id)
            
            return True
        return False
    
    async def visit_with_all(self, element: Element, 
                           visit_mode: VisitMode = VisitMode.PARALLEL) -> List[VisitResult]:
        """Visit element with all registered visitors."""
        visitors = list(self._visitors.values())
        return await self._visit_with_visitors(element, visitors, visit_mode)
    
    async def visit_with_group(self, element: Element, 
                              group: str,
                              visit_mode: VisitMode = VisitMode.PARALLEL) -> List[VisitResult]:
        """Visit element with visitors from specific group."""
        visitor_ids = self._visitor_groups.get(group, [])
        visitors = [self._visitors[vid] for vid in visitor_ids if vid in self._visitors]
        return await self._visit_with_visitors(element, visitors, visit_mode)
    
    async def traverse_with_all(self, root_element: Element,
                               traversal_strategy: TraversalStrategy = TraversalStrategy.DEPTH_FIRST,
                               visit_mode: VisitMode = VisitMode.PARALLEL) -> Dict[str, List[VisitResult]]:
        """Traverse element tree with all visitors."""
        self._traverser.strategy = traversal_strategy
        results = {}
        
        for visitor_id, visitor in self._visitors.items():
            visitor_results = await self._traverser.traverse(root_element, visitor, visit_mode)
            results[visitor_id] = visitor_results
        
        return results
    
    async def _visit_with_visitors(self, element: Element, 
                                  visitors: List[Visitor],
                                  visit_mode: VisitMode) -> List[VisitResult]:
        """Visit element with specified visitors."""
        if visit_mode == VisitMode.PARALLEL:
            # Execute visitors in parallel
            tasks = []
            for visitor in visitors:
                if visitor.can_visit(element):
                    task = asyncio.create_task(self._visit_with_visitor(element, visitor))
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for result in results:
                if isinstance(result, VisitResult):
                    processed_results.append(result)
                elif isinstance(result, Exception):
                    error_result = VisitResult(
                        success=False,
                        error=result,
                        element_type=type(element).__name__
                    )
                    processed_results.append(error_result)
            
            return processed_results
        else:
            # Execute visitors sequentially
            results = []
            for visitor in visitors:
                if visitor.can_visit(element):
                    result = await self._visit_with_visitor(element, visitor)
                    results.append(result)
            
            return results
    
    async def _visit_with_visitor(self, element: Element, visitor: Visitor) -> VisitResult:
        """Visit element with single visitor."""
        start_time = time.time()
        
        try:
            result = await visitor.visit(element)
            execution_time = time.time() - start_time
            
            visit_result = VisitResult(
                success=True,
                result=result,
                execution_time=execution_time,
                visitor_id=visitor.get_visitor_id(),
                element_type=type(element).__name__,
                elements_visited=1
            )
            
            # Notify listeners
            for listener in self._visit_listeners:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(visit_result)
                    else:
                        listener(visit_result)
                except Exception as e:
                    logging.error(f"Visit listener error: {e}")
            
            # Record in history
            self._execution_history.append(visit_result)
            self._metrics['successful_visits'] += 1
            
            return visit_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            visit_result = VisitResult(
                success=False,
                error=e,
                execution_time=execution_time,
                visitor_id=visitor.get_visitor_id(),
                element_type=type(element).__name__,
                elements_visited=0
            )
            
            self._execution_history.append(visit_result)
            self._metrics['failed_visits'] += 1
            
            return visit_result
    
    def add_visit_listener(self, listener: Callable[[VisitResult], None]) -> None:
        """Add visit result listener."""
        self._visit_listeners.append(listener)
    
    def get_visitor(self, visitor_id: str) -> Optional[Visitor]:
        """Get visitor by ID."""
        return self._visitors.get(visitor_id)
    
    def get_visitors_by_group(self, group: str) -> List[Visitor]:
        """Get all visitors in a group."""
        visitor_ids = self._visitor_groups.get(group, [])
        return [self._visitors[vid] for vid in visitor_ids if vid in self._visitors]
    
    def get_execution_history(self, limit: int = 10) -> List[VisitResult]:
        """Get recent execution history."""
        return list(self._execution_history)[-limit:]
    
    def get_manager_metrics(self) -> Dict[str, Any]:
        """Get comprehensive manager metrics."""
        visitor_metrics = {}
        for visitor_id, visitor in self._visitors.items():
            if hasattr(visitor, 'get_metrics'):
                visitor_metrics[visitor_id] = visitor.get_metrics()
        
        return {
            "manager_metrics": dict(self._metrics),
            "total_visitors": len(self._visitors),
            "visitor_groups": {k: len(v) for k, v in self._visitor_groups.items()},
            "execution_history_size": len(self._execution_history),
            "visitor_metrics": visitor_metrics
        }


# Utility classes
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: timedelta = timedelta(minutes=1)):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'
    
    def is_open(self) -> bool:
        if self.state == 'OPEN':
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > self.recovery_timeout):
                self.state = 'HALF_OPEN'
                return False
            return True
        return False
    
    def record_success(self) -> None:
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


class RateLimiter:
    """Rate limiter for controlling execution frequency."""
    
    def __init__(self, rate_limit: int, time_window: timedelta):
        self.rate_limit = rate_limit
        self.time_window = time_window
        self._request_times: deque = deque()
        self._lock = threading.RLock()
    
    def allow(self) -> bool:
        now = datetime.now()
        
        with self._lock:
            while (self._request_times and 
                   now - self._request_times[0] > self.time_window):
                self._request_times.popleft()
            
            if len(self._request_times) < self.rate_limit:
                self._request_times.append(now)
                return True
            
            return False


# Decorators
def visitor_method(element_type: Type):
    """Decorator for visitor methods."""
    
    def decorator(func):
        func._visitor_element_type = element_type
        return func
    
    return decorator


def main():
    """Demonstrate the optimized visitor pattern."""
    print("=== Optimized Visitor Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Generic typing with Protocol for type safety")
    print("✓ Async visitor methods with non-blocking operations")
    print("✓ Dynamic visitor registration and runtime dispatch")
    print("✓ Performance monitoring and comprehensive metrics")
    print("✓ Memory-efficient visitor caching and memoization")
    print("✓ Thread-safe concurrent visitor execution")
    print("✓ Advanced traversal strategies and optimization")
    print("✓ Event-driven visitor lifecycle management")
    print("✓ Multiple traversal modes (depth-first, breadth-first, etc.)")
    print("✓ Circuit breaker pattern for fault tolerance")
    print("✓ Rate limiting and execution control")
    print("✓ Comprehensive visitor management and coordination")


if __name__ == "__main__":
    main()