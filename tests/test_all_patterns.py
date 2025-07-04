"""
Comprehensive Test Suite for All Design Patterns

This module provides automated testing for all 23 Gang of Four design patterns
across all three implementation tiers (basic, practical, advanced).

Features:
- Pattern import validation
- Basic functionality testing
- Interface compliance checking
- Performance validation
- Error handling verification
"""

import pytest
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import traceback
from dataclasses import dataclass


@dataclass
class PatternTestResult:
    """Result of pattern testing."""
    pattern_name: str
    category: str
    tier: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None


class PatternTester:
    """Comprehensive pattern testing framework."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.patterns = self._discover_patterns()
    
    def _discover_patterns(self) -> Dict[str, List[str]]:
        """Discover all available patterns."""
        patterns = {}
        
        for category in ["behavioral", "creational", "structural"]:
            category_path = self.repo_root / category
            if not category_path.exists():
                continue
                
            patterns[category] = []
            
            for pattern_dir in category_path.iterdir():
                if pattern_dir.is_dir() and not pattern_dir.name.startswith('.'):
                    patterns[category].append(pattern_dir.name)
        
        return patterns
    
    def test_pattern_import(self, category: str, pattern: str, tier: str) -> PatternTestResult:
        """Test if a pattern can be imported without errors."""
        start_time = time.time()
        
        try:
            pattern_path = self.repo_root / category / pattern / f"{tier}.py"
            
            if not pattern_path.exists():
                return PatternTestResult(
                    pattern_name=pattern,
                    category=category,
                    tier=tier,
                    success=False,
                    execution_time=0,
                    error_message=f"File not found: {pattern_path}"
                )
            
            # Import the module
            spec = importlib.util.spec_from_file_location(
                f"{category}_{pattern}_{tier}", pattern_path
            )
            
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create module spec for {pattern_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Basic validation - check if module has some expected elements
            self._validate_module_structure(module, tier)
            
            execution_time = time.time() - start_time
            
            return PatternTestResult(
                pattern_name=pattern,
                category=category,
                tier=tier,
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return PatternTestResult(
                pattern_name=pattern,
                category=category,
                tier=tier,
                success=False,
                execution_time=execution_time,
                error_message=f"{type(e).__name__}: {str(e)}"
            )
    
    def _validate_module_structure(self, module, tier: str):
        """Validate that the module has expected structure."""
        # Check for classes (all patterns should have at least one class)
        classes = [name for name, obj in vars(module).items() 
                  if isinstance(obj, type) and not name.startswith('_')]
        
        if not classes:
            raise ValueError(f"No classes found in {tier} implementation")
        
        # Check for main/demo functions in basic implementations
        if tier == "basic":
            demo_functions = [name for name in ['main', 'demonstrate', 'example', 'client_code']
                            if hasattr(module, name) and callable(getattr(module, name))]
            
            if not demo_functions:
                raise ValueError("Basic implementation should have a demonstration function")


# Create test fixture for the pattern tester
@pytest.fixture(scope="session")
def pattern_tester():
    """Provide a pattern tester instance."""
    return PatternTester()


# Parametrized tests for all patterns
def pytest_generate_tests(metafunc):
    """Generate parametrized tests for all discovered patterns."""
    if "pattern_test_case" in metafunc.fixturenames:
        tester = PatternTester()
        test_cases = []
        
        for category, pattern_list in tester.patterns.items():
            for pattern in pattern_list:
                for tier in ["basic", "practical", "advanced"]:
                    test_cases.append((category, pattern, tier))
        
        metafunc.parametrize("pattern_test_case", test_cases, 
                           ids=[f"{cat}-{pat}-{tier}" for cat, pat, tier in test_cases])


def test_pattern_import_and_structure(pattern_tester, pattern_test_case):
    """Test that all patterns can be imported and have correct structure."""
    category, pattern, tier = pattern_test_case
    
    result = pattern_tester.test_pattern_import(category, pattern, tier)
    
    # Assert the test passed
    assert result.success, f"Failed to import {category}/{pattern}/{tier}: {result.error_message}"
    
    # Assert reasonable execution time (should import quickly)
    assert result.execution_time < 5.0, f"Import took too long: {result.execution_time:.2f}s"


class TestPatternCategories:
    """Test pattern categories and organization."""
    
    def test_all_categories_exist(self, pattern_tester):
        """Test that all required pattern categories exist."""
        required_categories = ["behavioral", "creational", "structural"]
        
        for category in required_categories:
            assert category in pattern_tester.patterns, f"Missing category: {category}"
            assert len(pattern_tester.patterns[category]) > 0, f"Empty category: {category}"
    
    def test_behavioral_patterns_count(self, pattern_tester):
        """Test that all 11 behavioral patterns are present."""
        expected_behavioral = {
            'chain_of_responsibility', 'command', 'interpreter', 'iterator',
            'mediator', 'memento', 'observer', 'state', 'strategy', 
            'template_method', 'visitor'
        }
        
        actual_behavioral = set(pattern_tester.patterns.get("behavioral", []))
        
        assert len(actual_behavioral) == 11, f"Expected 11 behavioral patterns, found {len(actual_behavioral)}"
        assert actual_behavioral == expected_behavioral, f"Missing patterns: {expected_behavioral - actual_behavioral}"
    
    def test_creational_patterns_count(self, pattern_tester):
        """Test that all 5 creational patterns are present."""
        expected_creational = {
            'abstract_factory', 'builder', 'factory_method', 'prototype', 'singleton'
        }
        
        actual_creational = set(pattern_tester.patterns.get("creational", []))
        
        assert len(actual_creational) == 5, f"Expected 5 creational patterns, found {len(actual_creational)}"
        assert actual_creational == expected_creational, f"Missing patterns: {expected_creational - actual_creational}"
    
    def test_structural_patterns_count(self, pattern_tester):
        """Test that all 7 structural patterns are present."""
        expected_structural = {
            'adapter', 'bridge', 'composite', 'decorator', 'facade', 'flyweight', 'proxy'
        }
        
        actual_structural = set(pattern_tester.patterns.get("structural", []))
        
        assert len(actual_structural) == 7, f"Expected 7 structural patterns, found {len(actual_structural)}"
        assert actual_structural == expected_structural, f"Missing patterns: {expected_structural - actual_structural}"


class TestPatternImplementations:
    """Test pattern implementation quality."""
    
    def test_all_patterns_have_three_tiers(self, pattern_tester):
        """Test that each pattern has all three implementation tiers."""
        for category, pattern_list in pattern_tester.patterns.items():
            for pattern in pattern_list:
                pattern_dir = pattern_tester.repo_root / category / pattern
                
                for tier in ["basic", "practical", "advanced"]:
                    tier_file = pattern_dir / f"{tier}.py"
                    assert tier_file.exists(), f"Missing {tier}.py for {category}/{pattern}"
                    assert tier_file.stat().st_size > 0, f"Empty {tier}.py for {category}/{pattern}"
    
    def test_patterns_have_readme(self, pattern_tester):
        """Test that each pattern has a README file."""
        for category, pattern_list in pattern_tester.patterns.items():
            for pattern in pattern_list:
                readme_path = pattern_tester.repo_root / category / pattern / "README.md"
                assert readme_path.exists(), f"Missing README.md for {category}/{pattern}"
                assert readme_path.stat().st_size > 0, f"Empty README.md for {category}/{pattern}"


class TestPerformance:
    """Test pattern performance characteristics."""
    
    @pytest.mark.slow
    def test_import_performance(self, pattern_tester):
        """Test that patterns import within reasonable time limits."""
        slow_imports = []
        
        for category, pattern_list in pattern_tester.patterns.items():
            for pattern in pattern_list:
                for tier in ["basic", "practical", "advanced"]:
                    result = pattern_tester.test_pattern_import(category, pattern, tier)
                    
                    if result.success and result.execution_time > 2.0:
                        slow_imports.append(f"{category}/{pattern}/{tier}: {result.execution_time:.2f}s")
        
        # Report slow imports but don't fail the test unless they're extremely slow
        if slow_imports:
            print(f"\\nSlow imports detected:\\n" + "\\n".join(slow_imports))
        
        # Only fail if imports take more than 5 seconds
        very_slow = [imp for imp in slow_imports if float(imp.split(": ")[1].replace("s", "")) > 5.0]
        assert not very_slow, f"Extremely slow imports: {very_slow}"


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])