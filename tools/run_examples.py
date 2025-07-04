#!/usr/bin/env python3
"""
Professional Design Patterns CLI Tool

A comprehensive command-line interface for exploring, running, and analyzing 
all 23 Gang of Four design patterns with their three implementation tiers.

Features:
- Interactive pattern exploration
- Performance benchmarking
- Code analysis and metrics
- Educational demonstrations
- Pattern comparison tools
"""

import argparse
import importlib.util
import sys
import time
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ImplementationTier(Enum):
    """Available implementation tiers."""
    BASIC = "basic"
    PRACTICAL = "practical" 
    ADVANCED = "advanced"
    ALL = "all"


class PatternCategory(Enum):
    """Pattern categories."""
    BEHAVIORAL = "behavioral"
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    ALL = "all"


@dataclass
class ExecutionResult:
    """Result of pattern execution."""
    pattern_name: str
    tier: str
    category: str
    success: bool
    execution_time: float
    output: str
    error: Optional[str] = None
    metrics: Dict[str, Any] = None


class PatternDiscovery:
    """Discovers and catalogs available patterns."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.patterns = self._discover_patterns()
    
    def _discover_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Discover all patterns and their available implementations."""
        patterns = {}
        
        for category in ["behavioral", "creational", "structural"]:
            category_path = self.repo_root / category
            if not category_path.exists():
                continue
                
            patterns[category] = {}
            
            for pattern_dir in category_path.iterdir():
                if pattern_dir.is_dir() and not pattern_dir.name.startswith('.'):
                    pattern_name = pattern_dir.name
                    patterns[category][pattern_name] = []
                    
                    # Check which tiers are available
                    for tier in ["basic", "practical", "advanced"]:
                        tier_file = pattern_dir / f"{tier}.py"
                        if tier_file.exists():
                            patterns[category][pattern_name].append(tier)
        
        return patterns
    
    def get_pattern_count(self) -> Tuple[int, int]:
        """Get total patterns and implementations count."""
        total_patterns = sum(len(patterns) for patterns in self.patterns.values())
        total_implementations = sum(
            len(tiers) 
            for category_patterns in self.patterns.values()
            for tiers in category_patterns.values()
        )
        return total_patterns, total_implementations
    
    def list_patterns(self, category: Optional[str] = None) -> None:
        """List all available patterns."""
        total_patterns, total_implementations = self.get_pattern_count()
        
        print(f"🐍 Python Design Patterns Repository")
        print(f"📊 {total_patterns} patterns, {total_implementations} implementations")
        print("=" * 60)
        
        categories = [category] if category and category != "all" else self.patterns.keys()
        
        for cat in categories:
            if cat not in self.patterns:
                continue
                
            print(f"\n📁 {cat.upper()} PATTERNS")
            print("-" * 40)
            
            for pattern_name, tiers in self.patterns[cat].items():
                tier_badges = " ".join([
                    f"{'✅' if tier in tiers else '❌'} {tier}" 
                    for tier in ["basic", "practical", "advanced"]
                ])
                print(f"  🔧 {pattern_name.replace('_', ' ').title()}")
                print(f"     {tier_badges}")


class PatternExecutor:
    """Executes pattern implementations and captures results."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
    
    def execute_pattern(self, category: str, pattern: str, tier: str) -> ExecutionResult:
        """Execute a single pattern implementation."""
        start_time = time.time()
        
        try:
            # Import the pattern module
            pattern_path = self.repo_root / category / pattern / f"{tier}.py"
            
            if not pattern_path.exists():
                return ExecutionResult(
                    pattern_name=pattern,
                    tier=tier,
                    category=category,
                    success=False,
                    execution_time=0,
                    output="",
                    error=f"Implementation file not found: {pattern_path}"
                )
            
            # Load and execute the module
            spec = importlib.util.spec_from_file_location(f"{category}_{pattern}_{tier}", pattern_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module from {pattern_path}")
            
            module = importlib.util.module_from_spec(spec)
            
            # Capture output
            from io import StringIO
            import contextlib
            
            output_capture = StringIO()
            with contextlib.redirect_stdout(output_capture):
                spec.loader.exec_module(module)
                
                # Try to run main function if it exists
                if hasattr(module, 'main'):
                    module.main()
                elif hasattr(module, 'demonstrate'):
                    module.demonstrate()
                elif hasattr(module, 'example'):
                    module.example()
            
            execution_time = time.time() - start_time
            output = output_capture.getvalue()
            
            return ExecutionResult(
                pattern_name=pattern,
                tier=tier,
                category=category,
                success=True,
                execution_time=execution_time,
                output=output,
                metrics=self._collect_metrics(module)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                pattern_name=pattern,
                tier=tier,
                category=category,
                success=False,
                execution_time=execution_time,
                output="",
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            )
    
    def _collect_metrics(self, module) -> Dict[str, Any]:
        """Collect metrics from the executed module."""
        metrics = {}
        
        # Count classes and functions
        classes = [name for name, obj in vars(module).items() 
                  if isinstance(obj, type) and not name.startswith('_')]
        functions = [name for name, obj in vars(module).items() 
                    if callable(obj) and not name.startswith('_') and not isinstance(obj, type)]
        
        metrics['classes'] = len(classes)
        metrics['functions'] = len(functions)
        metrics['module_size'] = len(str(module.__file__)) if hasattr(module, '__file__') else 0
        
        return metrics


class BenchmarkRunner:
    """Runs performance benchmarks on patterns."""
    
    def __init__(self, executor: PatternExecutor):
        self.executor = executor
    
    def benchmark_pattern(self, category: str, pattern: str, tier: str, iterations: int = 10) -> Dict[str, float]:
        """Benchmark a pattern implementation."""
        times = []
        
        print(f"🔄 Benchmarking {category}/{pattern}/{tier} ({iterations} iterations)...")
        
        for i in range(iterations):
            result = self.executor.execute_pattern(category, pattern, tier)
            if result.success:
                times.append(result.execution_time)
            else:
                print(f"❌ Benchmark failed on iteration {i+1}: {result.error}")
                break
        
        if not times:
            return {}
        
        return {
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'total_time': sum(times),
            'iterations': len(times)
        }


def create_cli() -> argparse.ArgumentParser:
    """Create the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Professional Design Patterns CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                              # List all patterns
  %(prog)s list --category behavioral        # List behavioral patterns
  %(prog)s run observer --tier advanced      # Run advanced observer pattern
  %(prog)s run --category creational         # Run all creational patterns
  %(prog)s benchmark observer --iterations 5 # Benchmark observer pattern
  %(prog)s analyze --category structural     # Analyze structural patterns
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available patterns')
    list_parser.add_argument('--category', choices=['behavioral', 'creational', 'structural', 'all'],
                           default='all', help='Pattern category to list')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run pattern implementations')
    run_parser.add_argument('pattern', nargs='?', help='Specific pattern to run')
    run_parser.add_argument('--category', choices=['behavioral', 'creational', 'structural'],
                          help='Run all patterns in category')
    run_parser.add_argument('--tier', choices=['basic', 'practical', 'advanced', 'all'],
                          default='practical', help='Implementation tier to run')
    run_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Benchmark pattern performance')
    benchmark_parser.add_argument('pattern', help='Pattern to benchmark')
    benchmark_parser.add_argument('--category', choices=['behavioral', 'creational', 'structural'],
                                help='Pattern category')
    benchmark_parser.add_argument('--tier', choices=['basic', 'practical', 'advanced'],
                                default='advanced', help='Implementation tier to benchmark')
    benchmark_parser.add_argument('--iterations', type=int, default=10, help='Number of iterations')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze patterns and generate reports')
    analyze_parser.add_argument('--category', choices=['behavioral', 'creational', 'structural', 'all'],
                              default='all', help='Category to analyze')
    analyze_parser.add_argument('--output', help='Output file for analysis report')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_cli()
    args = parser.parse_args()
    
    # Determine repository root
    repo_root = Path(__file__).parent.parent
    
    # Initialize components
    discovery = PatternDiscovery(repo_root)
    executor = PatternExecutor(repo_root)
    benchmarker = BenchmarkRunner(executor)
    
    try:
        if args.command == 'list':
            discovery.list_patterns(args.category)
            
        elif args.command == 'run':
            if args.pattern:
                # Run specific pattern
                category = args.category or _find_pattern_category(discovery, args.pattern)
                if not category:
                    print(f"❌ Pattern '{args.pattern}' not found")
                    sys.exit(1)
                
                tiers = [args.tier] if args.tier != 'all' else ['basic', 'practical', 'advanced']
                
                for tier in tiers:
                    print(f"\n🔧 Running {category}/{args.pattern}/{tier}")
                    print("-" * 50)
                    
                    result = executor.execute_pattern(category, args.pattern, tier)
                    _display_result(result, args.verbose)
                    
            elif args.category:
                # Run all patterns in category
                if args.category not in discovery.patterns:
                    print(f"❌ Category '{args.category}' not found")
                    sys.exit(1)
                
                for pattern in discovery.patterns[args.category]:
                    tiers = [args.tier] if args.tier != 'all' else ['basic', 'practical', 'advanced']
                    
                    for tier in tiers:
                        if tier in discovery.patterns[args.category][pattern]:
                            print(f"\n🔧 Running {args.category}/{pattern}/{tier}")
                            print("-" * 50)
                            
                            result = executor.execute_pattern(args.category, pattern, tier)
                            _display_result(result, args.verbose)
            else:
                print("❌ Please specify either --pattern or --category")
                sys.exit(1)
                
        elif args.command == 'benchmark':
            category = args.category or _find_pattern_category(discovery, args.pattern)
            if not category:
                print(f"❌ Pattern '{args.pattern}' not found")
                sys.exit(1)
            
            benchmark_results = benchmarker.benchmark_pattern(
                category, args.pattern, args.tier, args.iterations
            )
            
            if benchmark_results:
                print(f"\n📊 Benchmark Results for {category}/{args.pattern}/{args.tier}")
                print("-" * 60)
                print(f"Iterations: {benchmark_results['iterations']}")
                print(f"Min Time:   {benchmark_results['min_time']:.6f}s")
                print(f"Max Time:   {benchmark_results['max_time']:.6f}s")
                print(f"Avg Time:   {benchmark_results['avg_time']:.6f}s")
                print(f"Total Time: {benchmark_results['total_time']:.6f}s")
            
        elif args.command == 'analyze':
            print("🔍 Analysis feature coming soon...")
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.command == 'run' and hasattr(args, 'verbose') and args.verbose:
            traceback.print_exc()
        sys.exit(1)


def _find_pattern_category(discovery: PatternDiscovery, pattern_name: str) -> Optional[str]:
    """Find which category a pattern belongs to."""
    for category, patterns in discovery.patterns.items():
        if pattern_name in patterns:
            return category
    return None


def _display_result(result: ExecutionResult, verbose: bool = False) -> None:
    """Display execution result."""
    if result.success:
        print(f"✅ Success ({result.execution_time:.3f}s)")
        if result.output:
            print("\n📋 Output:")
            for line in result.output.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        if verbose and result.metrics:
            print(f"\n📊 Metrics:")
            for key, value in result.metrics.items():
                print(f"   {key}: {value}")
    else:
        print(f"❌ Failed ({result.execution_time:.3f}s)")
        if result.error:
            print(f"\n🚨 Error:")
            error_lines = result.error.split('\n')
            for line in error_lines[:5]:  # Show first 5 lines
                print(f"   {line}")
            if len(error_lines) > 5:
                print(f"   ... ({len(error_lines) - 5} more lines)")


if __name__ == "__main__":
    main()