# 🐍 Python Design Patterns

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)

A comprehensive implementation of all 23 Gang of Four Design Patterns in modern Python 3.13+. This repository provides three tiers of implementation for each pattern: basic academic examples, practical real-world applications, and advanced Python-optimized versions.

## 🚀 Features

- **Complete Coverage**: All 23 Gang of Four patterns implemented
- **Three Implementation Tiers**: Basic, Practical, and Advanced versions
- **Modern Python**: Leverages Python 3.13+ features (type hints, dataclasses, async/await)
- **Real-World Examples**: Practical applications you can use in production
- **Comprehensive Testing**: 100% test coverage with pytest
- **Professional Quality**: CI/CD, linting, formatting, and documentation
- **Performance Optimized**: Advanced implementations with caching, monitoring, and async operations

## 📁 Repository Structure

```
python-design-patterns/
├── creational/              # Object creation patterns (5 patterns)
│   ├── abstract_factory/    # Creates families of related objects
│   ├── builder/            # Constructs complex objects step by step
│   ├── factory_method/     # Creates objects without specifying exact classes
│   ├── prototype/          # Creates objects by cloning existing instances
│   └── singleton/          # Ensures only one instance exists
├── structural/             # Object composition patterns (7 patterns)
│   ├── adapter/           # Allows incompatible interfaces to work together
│   ├── bridge/            # Separates abstraction from implementation
│   ├── composite/         # Composes objects into tree structures
│   ├── decorator/         # Adds behavior to objects dynamically
│   ├── facade/            # Provides simplified interface to complex subsystem
│   ├── flyweight/         # Minimizes memory usage by sharing object data
│   └── proxy/             # Provides placeholder/surrogate for another object
├── behavioral/            # Object interaction patterns (11 patterns)
│   ├── chain_of_responsibility/  # Passes requests along chain of handlers
│   ├── command/           # Encapsulates requests as objects
│   ├── interpreter/       # Defines grammar and interprets sentences
│   ├── iterator/          # Provides way to access elements sequentially
│   ├── mediator/          # Defines how objects interact with each other
│   ├── memento/           # Captures and restores object state
│   ├── observer/          # Notifies multiple objects about state changes
│   ├── state/             # Alters behavior when internal state changes
│   ├── strategy/          # Defines family of algorithms and makes them interchangeable
│   ├── template_method/   # Defines skeleton of algorithm in base class
│   └── visitor/           # Defines new operations without changing object structure
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation and guides
└── tools/                 # Development tools and utilities
```

## 🔧 Implementation Tiers

Each pattern includes three levels of implementation:

### 1. 📚 Basic (`basic.py`)
Classic textbook implementation focusing on the core pattern structure and relationships.

```python
# Simple, educational implementation
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. 🏢 Practical (`practical.py`)
Real-world implementation with business logic, error handling, and practical use cases.

```python
# Production-ready implementation
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, connection_string: str = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(connection_string)
            return cls._instance
```

### 3. ⚡ Advanced (`advanced.py`)
Python-optimized implementation using modern language features, async operations, performance monitoring, and advanced patterns.

```python
# High-performance, feature-rich implementation
class AsyncSingleton(metaclass=SingletonMeta):
    def __init__(self):
        self._cache: LRUCache = LRUCache(maxsize=1000)
        self._metrics: MetricsCollector = MetricsCollector()
    
    async def get_instance(self) -> 'AsyncSingleton':
        async with self._async_lock:
            # Implementation with monitoring, caching, etc.
```

## 🛠️ Quick Start

### Installation

```bash
git clone https://github.com/jefrnc/python-design-patterns.git
cd python-design-patterns
pip install -r requirements.txt
```

### Running Examples

```bash
# Run all pattern examples
python -m tools.run_examples

# Run specific pattern category
python -m tools.run_examples --category behavioral

# Run specific pattern
python -m tools.run_examples --pattern observer

# Run specific implementation tier
python -m tools.run_examples --tier advanced
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific pattern tests
pytest tests/test_behavioral/test_observer.py

# Run performance benchmarks
pytest tests/benchmarks/ -v
```

## 📋 Pattern Catalog

### Creational Patterns (5/5)

| Pattern | Purpose | Basic | Practical | Advanced |
|---------|---------|-------|-----------|----------|
| [Abstract Factory](creational/abstract_factory/) | Create families of related objects | ✅ | ✅ | ✅ |
| [Builder](creational/builder/) | Construct complex objects step-by-step | ✅ | ✅ | ✅ |
| [Factory Method](creational/factory_method/) | Create objects without specifying exact classes | ✅ | ✅ | ✅ |
| [Prototype](creational/prototype/) | Create objects by cloning existing instances | ✅ | ✅ | ✅ |
| [Singleton](creational/singleton/) | Ensure only one instance exists | ✅ | ✅ | ✅ |

### Structural Patterns (7/7)

| Pattern | Purpose | Basic | Practical | Advanced |
|---------|---------|-------|-----------|----------|
| [Adapter](structural/adapter/) | Allow incompatible interfaces to work together | ✅ | ✅ | ✅ |
| [Bridge](structural/bridge/) | Separate abstraction from implementation | ✅ | ✅ | ✅ |
| [Composite](structural/composite/) | Compose objects into tree structures | ✅ | ✅ | ✅ |
| [Decorator](structural/decorator/) | Add behavior to objects dynamically | ✅ | ✅ | ✅ |
| [Facade](structural/facade/) | Provide simplified interface to complex subsystem | ✅ | ✅ | ✅ |
| [Flyweight](structural/flyweight/) | Minimize memory usage by sharing data | ✅ | ✅ | ✅ |
| [Proxy](structural/proxy/) | Provide placeholder for another object | ✅ | ✅ | ✅ |

### Behavioral Patterns (11/11)

| Pattern | Purpose | Basic | Practical | Advanced |
|---------|---------|-------|-----------|----------|
| [Chain of Responsibility](behavioral/chain_of_responsibility/) | Pass requests along chain of handlers | ✅ | ✅ | ✅ |
| [Command](behavioral/command/) | Encapsulate requests as objects | ✅ | ✅ | ✅ |
| [Interpreter](behavioral/interpreter/) | Define grammar and interpret sentences | ✅ | ✅ | ✅ |
| [Iterator](behavioral/iterator/) | Access elements sequentially | ✅ | ✅ | ✅ |
| [Mediator](behavioral/mediator/) | Define how objects interact | ✅ | ✅ | ✅ |
| [Memento](behavioral/memento/) | Capture and restore object state | ✅ | ✅ | ✅ |
| [Observer](behavioral/observer/) | Notify multiple objects about state changes | ✅ | ✅ | ✅ |
| [State](behavioral/state/) | Alter behavior when state changes | ✅ | ✅ | ✅ |
| [Strategy](behavioral/strategy/) | Make algorithms interchangeable | ✅ | ✅ | ✅ |
| [Template Method](behavioral/template_method/) | Define algorithm skeleton in base class | ✅ | ✅ | ✅ |
| [Visitor](behavioral/visitor/) | Define new operations without changing structure | ✅ | ✅ | ✅ |

## 🧪 Testing & Quality

This repository maintains high code quality standards:

- **100% Test Coverage**: Comprehensive test suite with unit, integration, and performance tests
- **Type Safety**: Full mypy type checking
- **Code Formatting**: Black + isort for consistent style
- **Linting**: pylint + flake8 for code quality
- **Security**: bandit for security vulnerability scanning
- **Performance**: Benchmarks and profiling for advanced implementations

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Learning Resources

- [Design Patterns: Elements of Reusable Object-Oriented Software](https://www.goodreads.com/book/show/85009.Design_Patterns) - The original Gang of Four book
- [Pattern Documentation](docs/) - Detailed explanations and use cases for each pattern
- [Best Practices Guide](docs/best_practices.md) - When and how to use each pattern
- [Performance Analysis](docs/performance.md) - Benchmarks and optimization insights

## 📊 Performance Benchmarks

Our advanced implementations include comprehensive performance monitoring:

```python
# Example performance metrics
Pattern: Observer (Advanced)
├── Notification Time: 0.003ms avg
├── Memory Usage: 45MB (vs 120MB basic)
├── Throughput: 50,000 events/sec
└── Concurrent Subscribers: 10,000+
```

See [benchmarks](tests/benchmarks/) for detailed performance analysis.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐ **If this repository helped you understand design patterns better, please give it a star!** ⭐