"""
Decorator Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Function decorators and class decorators
- Dataclasses for clean data structures
- Type hints with generics
- Context managers
- Property decorators
- __slots__ for memory efficiency
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Protocol, TypeVar, Generic, Callable, Any
import time


# Protocol for timing decorator
class TimingProtocol(Protocol):
    def execute(self) -> Any: ...


# Generic type for decorators
T = TypeVar('T')


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """
    Function decorator that adds timing functionality.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"⏱️  {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper


def logging_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """
    Function decorator that adds logging functionality.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        print(f"📝 Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"📝 {func.__name__} returned: {result}")
        return result
    return wrapper


@dataclass
class ProcessingResult:
    """Result of a processing operation."""
    data: Any
    success: bool
    message: str
    execution_time: float = 0.0


class DataProcessor(ABC):
    """
    Abstract base class for data processors.
    """
    
    @abstractmethod
    def process(self, data: Any) -> ProcessingResult:
        pass


class BasicDataProcessor(DataProcessor):
    """
    Basic data processor implementation.
    """
    
    __slots__ = ('_name',)
    
    def __init__(self, name: str = "BasicProcessor"):
        self._name = name
    
    def process(self, data: Any) -> ProcessingResult:
        # Simulate processing
        processed_data = f"Processed: {data}"
        return ProcessingResult(
            data=processed_data,
            success=True,
            message=f"Processing completed by {self._name}"
        )
    
    @property
    def name(self) -> str:
        return self._name


class ProcessorDecorator(DataProcessor):
    """
    Base decorator class for processors.
    """
    
    __slots__ = ('_processor',)
    
    def __init__(self, processor: DataProcessor):
        self._processor = processor
    
    def process(self, data: Any) -> ProcessingResult:
        return self._processor.process(data)
    
    @property
    def processor(self) -> DataProcessor:
        return self._processor


class TimingDecorator(ProcessorDecorator):
    """
    Decorator that adds timing functionality to processors.
    """
    
    def process(self, data: Any) -> ProcessingResult:
        start_time = time.time()
        result = super().process(data)
        end_time = time.time()
        
        # Add timing information
        result.execution_time = end_time - start_time
        result.message += f" (took {result.execution_time:.4f}s)"
        
        return result


class ValidationDecorator(ProcessorDecorator):
    """
    Decorator that adds validation functionality to processors.
    """
    
    __slots__ = ('_validator',)
    
    def __init__(self, processor: DataProcessor, validator: Callable[[Any], bool]):
        super().__init__(processor)
        self._validator = validator
    
    def process(self, data: Any) -> ProcessingResult:
        # Validate input
        if not self._validator(data):
            return ProcessingResult(
                data=data,
                success=False,
                message="Validation failed: Invalid input data"
            )
        
        # Process if validation passes
        result = super().process(data)
        result.message += " (validated)"
        return result


class CachingDecorator(ProcessorDecorator):
    """
    Decorator that adds caching functionality to processors.
    """
    
    __slots__ = ('_cache',)
    
    def __init__(self, processor: DataProcessor):
        super().__init__(processor)
        self._cache: dict[str, ProcessingResult] = {}
    
    def process(self, data: Any) -> ProcessingResult:
        # Create cache key
        cache_key = str(data)
        
        # Check cache
        if cache_key in self._cache:
            cached_result = self._cache[cache_key]
            cached_result.message += " (from cache)"
            print("🔄 Retrieved from cache")
            return cached_result
        
        # Process and cache
        result = super().process(data)
        self._cache[cache_key] = result
        result.message += " (cached)"
        print("💾 Stored in cache")
        return result
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        print("🗑️  Cache cleared")
    
    @property
    def cache_size(self) -> int:
        return len(self._cache)


class CompressionDecorator(ProcessorDecorator):
    """
    Decorator that adds compression functionality to processors.
    """
    
    def process(self, data: Any) -> ProcessingResult:
        result = super().process(data)
        
        if result.success:
            # Simulate compression
            original_size = len(str(result.data))
            compressed_data = f"COMPRESSED[{result.data}]"
            compressed_size = len(compressed_data)
            
            result.data = compressed_data
            result.message += f" (compressed {original_size}→{compressed_size} bytes)"
        
        return result


# Python-specific decorator using __call__
class RetryDecorator(ProcessorDecorator):
    """
    Decorator that adds retry functionality to processors.
    """
    
    __slots__ = ('_max_retries', '_retry_count')
    
    def __init__(self, processor: DataProcessor, max_retries: int = 3):
        super().__init__(processor)
        self._max_retries = max_retries
        self._retry_count = 0
    
    def process(self, data: Any) -> ProcessingResult:
        for attempt in range(self._max_retries + 1):
            try:
                result = super().process(data)
                if result.success:
                    if attempt > 0:
                        result.message += f" (succeeded on retry {attempt})"
                    return result
                else:
                    if attempt < self._max_retries:
                        print(f"🔄 Retry {attempt + 1}/{self._max_retries}")
                        continue
                    else:
                        result.message += f" (failed after {self._max_retries} retries)"
                        return result
            except Exception as e:
                if attempt < self._max_retries:
                    print(f"❌ Attempt {attempt + 1} failed: {e}")
                    continue
                else:
                    return ProcessingResult(
                        data=data,
                        success=False,
                        message=f"Failed after {self._max_retries} retries: {str(e)}"
                    )
        
        return ProcessingResult(
            data=data,
            success=False,
            message="Unexpected error in retry logic"
        )


def main():
    """
    Demonstrate optimized decorator implementations.
    """
    print("=== Optimized Decorator Pattern Demo ===")
    
    # Test basic processor
    print("\n1. Basic processor:")
    processor = BasicDataProcessor("MyProcessor")
    result = processor.process("hello world")
    print(f"Result: {result}")
    
    # Test single decorator
    print("\n2. With timing decorator:")
    timing_processor = TimingDecorator(processor)
    result = timing_processor.process("hello world")
    print(f"Result: {result}")
    
    # Test validation decorator
    print("\n3. With validation decorator:")
    def validate_string(data: Any) -> bool:
        return isinstance(data, str) and len(data) > 0
    
    validating_processor = ValidationDecorator(processor, validate_string)
    
    # Valid data
    result = validating_processor.process("valid data")
    print(f"Valid result: {result}")
    
    # Invalid data
    result = validating_processor.process("")
    print(f"Invalid result: {result}")
    
    # Test caching decorator
    print("\n4. With caching decorator:")
    caching_processor = CachingDecorator(processor)
    
    # First call
    result1 = caching_processor.process("cached data")
    print(f"First call: {result1}")
    
    # Second call (should be from cache)
    result2 = caching_processor.process("cached data")
    print(f"Second call: {result2}")
    
    print(f"Cache size: {caching_processor.cache_size}")
    
    # Test multiple decorators
    print("\n5. Multiple decorators combined:")
    complex_processor = CompressionDecorator(
        CachingDecorator(
            TimingDecorator(
                ValidationDecorator(
                    BasicDataProcessor("ComplexProcessor"),
                    validate_string
                )
            )
        )
    )
    
    result = complex_processor.process("complex processing test")
    print(f"Complex result: {result}")
    
    # Test function decorators
    print("\n6. Function decorators:")
    
    @timing_decorator
    @logging_decorator
    def process_data(data: str) -> str:
        time.sleep(0.1)  # Simulate processing
        return data.upper()
    
    result = process_data("function decorator test")
    print(f"Function result: {result}")
    
    # Test retry decorator
    print("\n7. Retry decorator:")
    
    class UnreliableProcessor(DataProcessor):
        def __init__(self):
            self.attempt_count = 0
        
        def process(self, data: Any) -> ProcessingResult:
            self.attempt_count += 1
            if self.attempt_count < 3:  # Fail first 2 attempts
                return ProcessingResult(
                    data=data,
                    success=False,
                    message=f"Simulated failure (attempt {self.attempt_count})"
                )
            return ProcessingResult(
                data=f"Success: {data}",
                success=True,
                message=f"Succeeded on attempt {self.attempt_count}"
            )
    
    unreliable = UnreliableProcessor()
    retry_processor = RetryDecorator(unreliable, max_retries=3)
    result = retry_processor.process("retry test")
    print(f"Retry result: {result}")


if __name__ == "__main__":
    main()