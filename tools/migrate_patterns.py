#!/usr/bin/env python3
"""
Pattern Migration Tool

This script automates the migration of patterns from our comprehensive implementation
to the professional repository structure with three tiers: basic, practical, advanced.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict


def create_pattern_structure():
    """Create the complete professional pattern structure."""
    
    # Pattern definitions
    patterns = {
        'behavioral': [
            'chain_of_responsibility', 'command', 'interpreter', 'iterator',
            'mediator', 'memento', 'observer', 'state', 'strategy', 
            'template_method', 'visitor'
        ],
        'creational': [
            'abstract_factory', 'builder', 'factory_method', 'prototype', 'singleton'
        ],
        'structural': [
            'adapter', 'bridge', 'composite', 'decorator', 'facade', 'flyweight', 'proxy'
        ]
    }
    
    repo_root = Path('/Users/Joseph/repos/python-design-patterns')
    source_root = Path('/Users/Joseph/Documents/Patterns/python_design_patterns')
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            # Create pattern directory
            pattern_dir = repo_root / category / pattern
            pattern_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy implementations from our source
            for tier in ['basic', 'practical', 'advanced']:
                source_file = source_root / tier / category / f"{pattern}.py"
                target_file = pattern_dir / f"{tier}.py"
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    print(f"✅ Copied {category}/{pattern}/{tier}.py")
                else:
                    print(f"⚠️ Missing {source_file}")
            
            # Create README for each pattern
            create_pattern_readme(pattern_dir, pattern, category)
    
    # Clean up old loose files
    cleanup_loose_files(repo_root)


def create_pattern_readme(pattern_dir: Path, pattern_name: str, category: str) -> None:
    """Create a comprehensive README for each pattern."""
    
    readme_content = f"""# {pattern_name.replace('_', ' ').title()} Pattern

## Overview
The {pattern_name.replace('_', ' ').title()} pattern is a {category} design pattern that...

## Implementation Tiers

This directory contains three implementations of the {pattern_name.replace('_', ' ').title()} pattern:

### 1. 📚 Basic Implementation (`basic.py`)
- Academic/textbook implementation
- Focuses on core pattern structure
- Minimal dependencies
- Educational purpose

### 2. 🏢 Practical Implementation (`practical.py`)  
- Real-world use case
- Production-ready code
- Proper error handling
- Business logic integration

### 3. ⚡ Advanced Implementation (`advanced.py`)
- Python-optimized version
- Modern language features
- Performance optimizations
- Comprehensive monitoring

## Usage

```python
# Basic usage
from {category}.{pattern_name}.basic import *

# Practical usage  
from {category}.{pattern_name}.practical import *

# Advanced usage
from {category}.{pattern_name}.advanced import *
```

## When to Use

The {pattern_name.replace('_', ' ').title()} pattern is useful when:
- [Use case 1]
- [Use case 2]
- [Use case 3]

## Related Patterns

- [Related Pattern 1]
- [Related Pattern 2]

## References

- [Gang of Four Design Patterns Book](https://www.goodreads.com/book/show/85009.Design_Patterns)
- [Pattern Documentation](../../docs/patterns/{category}/{pattern_name}.md)
"""
    
    readme_file = pattern_dir / "README.md"
    readme_file.write_text(readme_content)
    print(f"📝 Created README for {category}/{pattern_name}")


def cleanup_loose_files(repo_root: Path) -> None:
    """Clean up loose pattern files that have been migrated."""
    
    categories = ['behavioral', 'creational', 'structural']
    
    for category in categories:
        category_dir = repo_root / category
        if category_dir.exists():
            # Remove loose .py files (they should now be in subdirectories)
            for py_file in category_dir.glob("*.py"):
                if py_file.stem != "__init__":
                    print(f"🗑️ Removing loose file: {py_file}")
                    py_file.unlink()


if __name__ == "__main__":
    print("🚀 Starting professional pattern migration...")
    create_pattern_structure()
    print("✅ Migration completed successfully!")