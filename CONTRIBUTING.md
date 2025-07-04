# Contributing to Python Design Patterns

Thank you for your interest in contributing to this comprehensive design patterns repository! This guide will help you get started with contributing effectively.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/python-design-patterns.git
   cd python-design-patterns
   ```
3. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## 📁 Repository Structure

```
python-design-patterns/
├── behavioral/           # Behavioral patterns (11 patterns)
├── creational/          # Creational patterns (5 patterns)  
├── structural/          # Structural patterns (7 patterns)
├── tests/              # Comprehensive test suite
├── tools/              # CLI tools and utilities
└── docs/               # Documentation
```

Each pattern follows a consistent structure:
```
pattern_name/
├── basic.py           # Academic implementation
├── practical.py       # Real-world example
├── advanced.py        # Python-optimized version
└── README.md          # Pattern documentation
```

## 🛠️ Development Guidelines

### Code Style

We maintain strict code quality standards:

- **Python 3.13+** features and syntax
- **Type hints** for all functions and methods
- **Docstrings** following Google style
- **Black** for code formatting
- **isort** for import sorting
- **pylint** for code quality

### Pattern Implementation Standards

Each pattern should include:

1. **Three Implementation Tiers**:
   - `basic.py`: Clean, academic implementation
   - `practical.py`: Real-world business scenario
   - `advanced.py`: Python-optimized with modern features

2. **Required Elements**:
   - Comprehensive docstrings
   - Type annotations
   - Error handling
   - Demonstration function (`main()`, `demonstrate()`, or `example()`)
   - Performance considerations for advanced implementations

3. **Code Quality**:
   - No external dependencies for basic implementations
   - Minimal dependencies for practical implementations
   - Modern Python features in advanced implementations
   - 100% test coverage

### Testing

- All patterns must have comprehensive tests
- Tests should cover all three implementation tiers
- Include both unit tests and integration tests
- Performance tests for advanced implementations

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific pattern tests
pytest tests/test_specific_pattern.py
```

## 📝 Contributing Types

### 🐛 Bug Fixes

1. Create an issue describing the bug
2. Reference the issue in your PR
3. Include tests that reproduce the bug
4. Verify the fix works across all Python versions

### ✨ New Features

For new pattern implementations:

1. **Research**: Ensure the pattern follows Gang of Four definitions
2. **Design**: Plan all three implementation tiers
3. **Implement**: Follow our coding standards
4. **Test**: Comprehensive test coverage
5. **Document**: Pattern README and inline documentation

### 📚 Documentation

- Fix typos or unclear explanations
- Add more examples or use cases
- Improve README files
- Add performance benchmarks

### 🔧 Tooling

- Improve the CLI tool
- Add new development utilities
- Enhance the build process
- Update CI/CD workflows

## 🔍 Code Review Process

All contributions go through thorough code review:

1. **Automated Checks**: CI pipeline runs tests, linting, and formatting
2. **Manual Review**: Code quality, design, and adherence to standards
3. **Testing**: Verify all tests pass and coverage is maintained
4. **Documentation**: Ensure proper documentation is included

### Review Criteria

- [ ] Follows established patterns and conventions
- [ ] Includes comprehensive tests
- [ ] Has proper documentation
- [ ] Passes all automated checks
- [ ] Maintains or improves performance
- [ ] Compatible with Python 3.13+

## 📋 Pull Request Guidelines

### PR Title Format
```
[Category] Brief description of changes

Examples:
[Behavioral] Add Chain of Responsibility advanced implementation
[Structural] Fix Adapter pattern type annotations  
[Tools] Improve CLI performance benchmarking
[Tests] Add integration tests for creational patterns
```

### PR Description Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added and passing
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🧪 Testing Your Changes

Before submitting a PR:

```bash
# Format code
black .
isort .

# Run linting
pylint creational/ structural/ behavioral/ tools/
flake8 .

# Type checking
mypy .

# Run tests
pytest --cov=. --cov-report=term-missing

# Test CLI tool
python -m tools.run_examples list
python -m tools.run_examples run observer --tier advanced
```

## 📊 Performance Considerations

For advanced implementations:

- **Async/await** for I/O operations
- **Caching** for expensive computations
- **Memory efficiency** for large-scale usage
- **Type checking** with protocols and generics
- **Performance monitoring** and metrics

## 🐞 Reporting Issues

When reporting bugs:

1. **Search existing issues** first
2. **Use the issue template**
3. **Provide minimal reproduction case**
4. **Include Python version and environment details**
5. **Add relevant error messages and stack traces**

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `performance`: Performance improvements
- `testing`: Test-related issues

## 🏆 Recognition

Contributors are recognized in several ways:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- GitHub contributor statistics
- Special recognition for significant contributions

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs and feature requests
- **Code Review**: Ask for feedback during PR review
- **Design Decisions**: Discuss major changes before implementation

## 📜 Code of Conduct

### Our Standards

- **Respectful**: Treat everyone with respect and kindness
- **Inclusive**: Welcome contributors from all backgrounds
- **Constructive**: Provide helpful, actionable feedback
- **Professional**: Maintain professional communication
- **Learning-Focused**: Help others learn and grow

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Spam or irrelevant content
- Sharing private information without permission

## 🎯 Project Goals

This repository aims to be:

- **Educational**: Clear, well-documented implementations
- **Practical**: Real-world applicable examples
- **Performant**: Optimized Python implementations
- **Comprehensive**: Complete coverage of all 23 patterns
- **Modern**: Using latest Python features and best practices

Thank you for contributing to making this the best design patterns resource for Python developers! 🐍✨