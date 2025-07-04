"""
Template Method Design Pattern - Optimized Implementation

This optimized version demonstrates advanced Python features:
- Generic typing with TypeVar and Protocol for type safety
- Async template methods with non-blocking operations
- Dynamic step registration and runtime modification
- Performance monitoring and step-level metrics
- Memory-efficient step caching and memoization
- Thread-safe concurrent template execution
- Advanced error handling and recovery strategies
- Event-driven template lifecycle management
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Protocol, Optional, List, Dict, Any, 
    Callable, Union, Awaitable, Type, runtime_checkable,
    Set, Tuple, Iterator
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
from collections import defaultdict, deque, OrderedDict
from concurrent.futures import ThreadPoolExecutor
import logging

# Type variables
TemplateT = TypeVar('TemplateT', bound='TemplateMethod')
StepT = TypeVar('StepT', bound='TemplateStep')
ContextT = TypeVar('ContextT')
ResultT = TypeVar('ResultT')


class StepType(Enum):
    """Types of template steps."""
    REQUIRED = "required"
    OPTIONAL = "optional"
    HOOK = "hook"
    CONDITIONAL = "conditional"


class ExecutionMode(Enum):
    """Template execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"


class StepStatus(Enum):
    """Status of step execution."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    SKIPPED = auto()
    FAILED = auto()
    RETRYING = auto()


@dataclass
class StepMetadata:
    """Metadata for template steps."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    step_type: StepType = StepType.REQUIRED
    priority: int = 0
    timeout: Optional[float] = None
    max_retries: int = 0
    retry_delay: float = 1.0
    dependencies: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    description: str = ""


@dataclass
class StepMetrics:
    """Performance metrics for template steps."""
    executions: int = 0
    successes: int = 0
    failures: int = 0
    skips: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_executed: Optional[datetime] = None
    retry_count: int = 0
    
    def update(self, execution_time: float, status: StepStatus):
        """Update metrics with execution result."""
        self.executions += 1
        self.last_executed = datetime.now()
        
        if status == StepStatus.COMPLETED:
            self.successes += 1
        elif status == StepStatus.FAILED:
            self.failures += 1
        elif status == StepStatus.SKIPPED:
            self.skips += 1
        
        if status != StepStatus.SKIPPED:
            self.total_time += execution_time
            self.average_time = self.total_time / (self.executions - self.skips)
            self.min_time = min(self.min_time, execution_time)
            self.max_time = max(self.max_time, execution_time)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        executed = self.executions - self.skips
        return self.successes / max(1, executed)


@dataclass
class ExecutionResult(Generic[ResultT]):
    """Result of template execution."""
    success: bool
    result: Optional[ResultT] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    steps_executed: int = 0
    steps_skipped: int = 0
    steps_failed: int = 0
    step_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class TemplateStep(Protocol[ContextT, ResultT]):
    """Protocol for template steps."""
    
    def get_step_id(self) -> str:
        """Get unique identifier for this step."""
        ...
    
    async def execute(self, context: ContextT) -> ResultT:
        """Execute the step."""
        ...
    
    def should_execute(self, context: ContextT) -> bool:
        """Check if step should be executed."""
        ...
    
    def get_metadata(self) -> StepMetadata:
        """Get step metadata."""
        ...


class OptimizedTemplateStep(Generic[ContextT, ResultT], ABC):
    """
    High-performance template step with advanced features.
    """
    
    def __init__(self, metadata: StepMetadata = None):
        self.metadata = metadata or StepMetadata()
        self.metrics = StepMetrics()
        self.status = StepStatus.PENDING
        
        self._cache: Dict[str, Tuple[ResultT, datetime]] = {}
        self._cache_lock = threading.RLock()
        self._cache_ttl = timedelta(minutes=5)
        
        # Hooks
        self._pre_execution_hooks: List[Callable] = []
        self._post_execution_hooks: List[Callable] = []
        self._error_handlers: List[Callable] = []
        
        # Conditions
        self._execution_condition: Optional[Callable[[ContextT], bool]] = None
        self._retry_condition: Optional[Callable[[Exception], bool]] = None
    
    def get_step_id(self) -> str:
        return self.metadata.step_id
    
    def get_metadata(self) -> StepMetadata:
        return self.metadata
    
    async def execute(self, context: ContextT) -> ResultT:
        """Execute step with comprehensive monitoring."""
        start_time = time.time()
        self.status = StepStatus.RUNNING
        
        try:
            # Check cache
            cache_key = self._generate_cache_key(context)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result is not None:
                self.status = StepStatus.COMPLETED
                return cached_result
            
            # Execute pre-execution hooks
            for hook in self._pre_execution_hooks:
                if asyncio.iscoroutinefunction(hook):
                    await hook(context)
                else:
                    hook(context)
            
            # Execute with timeout and retry logic
            result = await self._execute_with_retry(context)
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Execute post-execution hooks
            for hook in self._post_execution_hooks:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(context, result)
                    else:
                        hook(context, result)
                except Exception as e:
                    logging.warning(f"Post-execution hook failed: {e}")
            
            self.status = StepStatus.COMPLETED
            execution_time = time.time() - start_time
            self.metrics.update(execution_time, StepStatus.COMPLETED)
            
            return result
            
        except Exception as e:
            self.status = StepStatus.FAILED
            execution_time = time.time() - start_time
            self.metrics.update(execution_time, StepStatus.FAILED)
            
            # Execute error handlers
            for handler in self._error_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(context, e)
                    else:
                        handler(context, e)
                except Exception as handler_error:
                    logging.error(f"Error handler failed: {handler_error}")
            
            raise
    
    async def _execute_with_retry(self, context: ContextT) -> ResultT:
        """Execute step with retry logic."""
        last_exception = None
        
        for attempt in range(self.metadata.max_retries + 1):
            try:
                if attempt > 0:
                    self.status = StepStatus.RETRYING
                    self.metrics.retry_count += 1
                    await asyncio.sleep(self.metadata.retry_delay * (2 ** (attempt - 1)))
                
                # Execute with timeout
                if self.metadata.timeout:
                    result = await asyncio.wait_for(
                        self.execute_step(context),
                        timeout=self.metadata.timeout
                    )
                else:
                    result = await self.execute_step(context)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check retry condition
                if (self._retry_condition and 
                    not self._retry_condition(e) or 
                    attempt == self.metadata.max_retries):
                    break
        
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Step execution failed")
    
    @abstractmethod
    async def execute_step(self, context: ContextT) -> ResultT:
        """Implement the actual step logic."""
        pass
    
    def should_execute(self, context: ContextT) -> bool:
        """Check if step should be executed."""
        if self._execution_condition:
            return self._execution_condition(context)
        
        # Required steps always execute, optional steps can be overridden
        return self.metadata.step_type in [StepType.REQUIRED, StepType.HOOK]
    
    def _generate_cache_key(self, context: ContextT) -> str:
        """Generate cache key for given context."""
        import hashlib
        import json
        
        try:
            context_str = json.dumps(context, sort_keys=True, default=str)
            return hashlib.md5(f"{self.get_step_id()}_{context_str}".encode()).hexdigest()
        except (TypeError, ValueError):
            return hashlib.md5(f"{self.get_step_id()}_{str(context)}".encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[ResultT]:
        """Get cached result if valid."""
        with self._cache_lock:
            if cache_key in self._cache:
                result, timestamp = self._cache[cache_key]
                if datetime.now() - timestamp < self._cache_ttl:
                    return result
                else:
                    del self._cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: ResultT) -> None:
        """Cache execution result."""
        with self._cache_lock:
            self._cache[cache_key] = (result, datetime.now())
            
            # Cleanup old entries
            if len(self._cache) > 100:
                oldest_keys = sorted(
                    self._cache.keys(),
                    key=lambda k: self._cache[k][1]
                )[:10]
                for key in oldest_keys:
                    del self._cache[key]
    
    def set_execution_condition(self, condition: Callable[[ContextT], bool]) -> None:
        """Set condition for step execution."""
        self._execution_condition = condition
    
    def set_retry_condition(self, condition: Callable[[Exception], bool]) -> None:
        """Set condition for retry attempts."""
        self._retry_condition = condition
    
    def add_pre_execution_hook(self, hook: Callable) -> None:
        """Add pre-execution hook."""
        self._pre_execution_hooks.append(hook)
    
    def add_post_execution_hook(self, hook: Callable) -> None:
        """Add post-execution hook."""
        self._post_execution_hooks.append(hook)
    
    def add_error_handler(self, handler: Callable) -> None:
        """Add error handler."""
        self._error_handlers.append(handler)
    
    def set_cache_ttl(self, ttl: timedelta) -> None:
        """Set cache TTL."""
        self._cache_ttl = ttl
    
    def clear_cache(self) -> None:
        """Clear step cache."""
        with self._cache_lock:
            self._cache.clear()
    
    def get_metrics(self) -> StepMetrics:
        return self.metrics


class FunctionalTemplateStep(OptimizedTemplateStep[ContextT, ResultT]):
    """Template step that wraps a function."""
    
    def __init__(self, step_func: Callable[[ContextT], Awaitable[ResultT]], 
                 metadata: StepMetadata = None):
        super().__init__(metadata)
        self.step_func = step_func
    
    async def execute_step(self, context: ContextT) -> ResultT:
        """Execute the wrapped function."""
        if asyncio.iscoroutinefunction(self.step_func):
            return await self.step_func(context)
        else:
            return self.step_func(context)


@runtime_checkable
class TemplateMethod(Protocol[ContextT, ResultT]):
    """Protocol for template method implementations."""
    
    def get_template_id(self) -> str:
        """Get unique identifier for this template."""
        ...
    
    async def execute(self, context: ContextT) -> ExecutionResult[ResultT]:
        """Execute the template method."""
        ...
    
    def get_steps(self) -> List[TemplateStep]:
        """Get all template steps."""
        ...


class OptimizedTemplateMethod(Generic[ContextT, ResultT], ABC):
    """
    High-performance template method with advanced features.
    """
    
    def __init__(self, template_id: str = None, 
                 execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL):
        self.template_id = template_id or f"template_{uuid.uuid4()}"
        self.execution_mode = execution_mode
        
        self._steps: OrderedDict[str, TemplateStep] = OrderedDict()
        self._step_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._execution_history: deque = deque(maxlen=100)
        
        self._execution_lock = asyncio.Lock()
        self._metrics = defaultdict(int)
        
        # Event listeners
        self._step_listeners: List[Callable] = []
        self._template_listeners: List[Callable] = []
        
        # Error handling
        self._error_strategy: str = "stop"  # "stop", "continue", "retry"
        self._global_error_handler: Optional[Callable] = None
        
        # Performance optimization
        self._step_cache: Dict[str, Any] = {}
        self._cache_lock = threading.RLock()
    
    def get_template_id(self) -> str:
        return self.template_id
    
    def add_step(self, step: TemplateStep, 
                dependencies: List[str] = None) -> None:
        """Add step to template with optional dependencies."""
        step_id = step.get_step_id()
        self._steps[step_id] = step
        
        if dependencies:
            self._step_dependencies[step_id].update(dependencies)
    
    def remove_step(self, step_id: str) -> bool:
        """Remove step from template."""
        if step_id in self._steps:
            del self._steps[step_id]
            
            # Remove dependencies
            if step_id in self._step_dependencies:
                del self._step_dependencies[step_id]
            
            # Remove this step from other dependencies
            for deps in self._step_dependencies.values():
                deps.discard(step_id)
            
            return True
        return False
    
    def get_steps(self) -> List[TemplateStep]:
        """Get all template steps."""
        return list(self._steps.values())
    
    def get_step(self, step_id: str) -> Optional[TemplateStep]:
        """Get specific step by ID."""
        return self._steps.get(step_id)
    
    async def execute(self, context: ContextT) -> ExecutionResult[ResultT]:
        """Execute template method with comprehensive monitoring."""
        
        async with self._execution_lock:
            start_time = time.time()
            
            result = ExecutionResult[ResultT](success=True)
            
            try:
                # Notify template start
                await self._notify_template_listeners("start", context)
                
                # Execute steps based on mode
                if self.execution_mode == ExecutionMode.SEQUENTIAL:
                    await self._execute_sequential(context, result)
                elif self.execution_mode == ExecutionMode.PARALLEL:
                    await self._execute_parallel(context, result)
                elif self.execution_mode == ExecutionMode.CONDITIONAL:
                    await self._execute_conditional(context, result)
                elif self.execution_mode == ExecutionMode.PIPELINE:
                    await self._execute_pipeline(context, result)
                
                # Execute post-processing
                result.result = await self.post_process(context, result.step_results)
                
                result.execution_time = time.time() - start_time
                self._metrics['successful_executions'] += 1
                
                # Notify template completion
                await self._notify_template_listeners("complete", context, result)
                
            except Exception as e:
                result.success = False
                result.error = e
                result.execution_time = time.time() - start_time
                self._metrics['failed_executions'] += 1
                
                # Handle global error
                if self._global_error_handler:
                    try:
                        if asyncio.iscoroutinefunction(self._global_error_handler):
                            await self._global_error_handler(context, e)
                        else:
                            self._global_error_handler(context, e)
                    except Exception as handler_error:
                        logging.error(f"Global error handler failed: {handler_error}")
                
                # Notify template error
                await self._notify_template_listeners("error", context, result)
            
            finally:
                # Record execution
                self._execution_history.append(result)
                self._metrics['total_executions'] += 1
            
            return result
    
    async def _execute_sequential(self, context: ContextT, 
                                 result: ExecutionResult[ResultT]) -> None:
        """Execute steps sequentially."""
        for step_id, step in self._steps.items():
            await self._execute_single_step(step, context, result)
            
            if not result.success and self._error_strategy == "stop":
                break
    
    async def _execute_parallel(self, context: ContextT, 
                               result: ExecutionResult[ResultT]) -> None:
        """Execute steps in parallel where possible."""
        # Build dependency graph
        dependency_graph = self._build_dependency_graph()
        
        # Execute in batches based on dependencies
        remaining_steps = set(self._steps.keys())
        
        while remaining_steps:
            # Find steps with no pending dependencies
            ready_steps = [
                step_id for step_id in remaining_steps
                if not (self._step_dependencies[step_id] & remaining_steps)
            ]
            
            if not ready_steps:
                # Circular dependency or other issue
                break
            
            # Execute ready steps in parallel
            tasks = []
            for step_id in ready_steps:
                step = self._steps[step_id]
                task = asyncio.create_task(
                    self._execute_single_step(step, context, result)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Remove completed steps
            remaining_steps -= set(ready_steps)
    
    async def _execute_conditional(self, context: ContextT, 
                                  result: ExecutionResult[ResultT]) -> None:
        """Execute steps based on conditions."""
        for step_id, step in self._steps.items():
            if step.should_execute(context):
                await self._execute_single_step(step, context, result)
            else:
                result.steps_skipped += 1
                await self._notify_step_listeners("skipped", step, context)
    
    async def _execute_pipeline(self, context: ContextT, 
                               result: ExecutionResult[ResultT]) -> None:
        """Execute steps as pipeline, passing output to next step."""
        current_context = context
        
        for step_id, step in self._steps.items():
            step_result = await self._execute_single_step(step, current_context, result)
            
            # Use step result as context for next step if successful
            if step_result and result.success:
                current_context = step_result
            elif not result.success and self._error_strategy == "stop":
                break
    
    async def _execute_single_step(self, step: TemplateStep, 
                                  context: ContextT, 
                                  result: ExecutionResult[ResultT]) -> Any:
        """Execute a single step with monitoring."""
        step_id = step.get_step_id()
        
        try:
            # Notify step start
            await self._notify_step_listeners("start", step, context)
            
            # Execute step
            step_result = await step.execute(context)
            
            # Record result
            result.step_results[step_id] = step_result
            result.steps_executed += 1
            
            # Notify step completion
            await self._notify_step_listeners("complete", step, context, step_result)
            
            return step_result
            
        except Exception as e:
            result.steps_failed += 1
            result.step_results[step_id] = e
            
            # Notify step error
            await self._notify_step_listeners("error", step, context, e)
            
            if self._error_strategy == "stop":
                result.success = False
                raise
            elif self._error_strategy == "continue":
                logging.warning(f"Step {step_id} failed but continuing: {e}")
                return None
            
            return None
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph for parallel execution."""
        return dict(self._step_dependencies)
    
    async def post_process(self, context: ContextT, 
                          step_results: Dict[str, Any]) -> Optional[ResultT]:
        """Post-process step results (override in subclasses)."""
        return None
    
    def set_error_strategy(self, strategy: str) -> None:
        """Set error handling strategy."""
        if strategy in ["stop", "continue", "retry"]:
            self._error_strategy = strategy
        else:
            raise ValueError(f"Invalid error strategy: {strategy}")
    
    def set_global_error_handler(self, handler: Callable) -> None:
        """Set global error handler."""
        self._global_error_handler = handler
    
    def add_step_listener(self, listener: Callable) -> None:
        """Add step execution listener."""
        self._step_listeners.append(listener)
    
    def add_template_listener(self, listener: Callable) -> None:
        """Add template execution listener."""
        self._template_listeners.append(listener)
    
    async def _notify_step_listeners(self, event: str, step: TemplateStep, 
                                   context: ContextT, data: Any = None) -> None:
        """Notify step listeners."""
        for listener in self._step_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event, step, context, data)
                else:
                    listener(event, step, context, data)
            except Exception as e:
                logging.error(f"Step listener error: {e}")
    
    async def _notify_template_listeners(self, event: str, context: ContextT, 
                                       data: Any = None) -> None:
        """Notify template listeners."""
        for listener in self._template_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event, self, context, data)
                else:
                    listener(event, self, context, data)
            except Exception as e:
                logging.error(f"Template listener error: {e}")
    
    def get_execution_history(self, limit: int = 10) -> List[ExecutionResult[ResultT]]:
        """Get recent execution history."""
        return list(self._execution_history)[-limit:]
    
    def get_template_metrics(self) -> Dict[str, Any]:
        """Get comprehensive template metrics."""
        step_metrics = {}
        for step_id, step in self._steps.items():
            if hasattr(step, 'get_metrics'):
                step_metrics[step_id] = step.get_metrics()
        
        return {
            "template_metrics": dict(self._metrics),
            "total_steps": len(self._steps),
            "execution_mode": self.execution_mode.value,
            "error_strategy": self._error_strategy,
            "execution_history_size": len(self._execution_history),
            "step_metrics": step_metrics
        }
    
    def validate_template(self) -> List[str]:
        """Validate template configuration."""
        issues = []
        
        # Check for circular dependencies
        def has_cycle(step_id: str, visited: Set[str], path: Set[str]) -> bool:
            if step_id in path:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            path.add(step_id)
            
            for dep in self._step_dependencies.get(step_id, set()):
                if has_cycle(dep, visited, path):
                    return True
            
            path.remove(step_id)
            return False
        
        visited = set()
        for step_id in self._steps.keys():
            if step_id not in visited:
                if has_cycle(step_id, visited, set()):
                    issues.append(f"Circular dependency detected involving step '{step_id}'")
        
        # Check for missing dependencies
        for step_id, deps in self._step_dependencies.items():
            for dep in deps:
                if dep not in self._steps:
                    issues.append(f"Step '{step_id}' depends on non-existent step '{dep}'")
        
        return issues


# Utility decorators and builders
def template_step(step_id: str = None, 
                 step_type: StepType = StepType.REQUIRED,
                 timeout: float = None,
                 max_retries: int = 0):
    """Decorator for creating template steps from functions."""
    
    def decorator(func):
        metadata = StepMetadata(
            step_id=step_id or func.__name__,
            name=func.__name__,
            step_type=step_type,
            timeout=timeout,
            max_retries=max_retries,
            description=func.__doc__ or ""
        )
        
        return FunctionalTemplateStep(func, metadata)
    
    return decorator


class TemplateBuilder:
    """Builder for creating template methods."""
    
    def __init__(self, template_id: str = None):
        self.template_id = template_id
        self._steps: List[Tuple[TemplateStep, List[str]]] = []
        self._execution_mode = ExecutionMode.SEQUENTIAL
        self._error_strategy = "stop"
    
    def add_step(self, step: TemplateStep, dependencies: List[str] = None) -> 'TemplateBuilder':
        """Add step to template."""
        self._steps.append((step, dependencies or []))
        return self
    
    def set_execution_mode(self, mode: ExecutionMode) -> 'TemplateBuilder':
        """Set execution mode."""
        self._execution_mode = mode
        return self
    
    def set_error_strategy(self, strategy: str) -> 'TemplateBuilder':
        """Set error handling strategy."""
        self._error_strategy = strategy
        return self
    
    def build(self) -> OptimizedTemplateMethod:
        """Build the template method."""
        template = ConcreteTemplateMethod(self.template_id, self._execution_mode)
        template.set_error_strategy(self._error_strategy)
        
        for step, dependencies in self._steps:
            template.add_step(step, dependencies)
        
        return template


class ConcreteTemplateMethod(OptimizedTemplateMethod):
    """Concrete implementation of template method."""
    
    async def post_process(self, context: Any, step_results: Dict[str, Any]) -> Any:
        """Default post-processing - return all step results."""
        return step_results


def main():
    """Demonstrate the optimized template method pattern."""
    print("=== Optimized Template Method Pattern Demo ===")
    print("This implementation provides:")
    print("✓ Generic typing with Protocol for type safety")
    print("✓ Async template methods with non-blocking operations")
    print("✓ Dynamic step registration and runtime modification")
    print("✓ Performance monitoring and step-level metrics")
    print("✓ Memory-efficient step caching and memoization")
    print("✓ Thread-safe concurrent template execution")
    print("✓ Advanced error handling and recovery strategies")
    print("✓ Event-driven template lifecycle management")
    print("✓ Multiple execution modes (sequential/parallel/conditional/pipeline)")
    print("✓ Dependency management and circular dependency detection")
    print("✓ Comprehensive validation and error reporting")
    print("✓ Builder pattern for easy template construction")


if __name__ == "__main__":
    main()