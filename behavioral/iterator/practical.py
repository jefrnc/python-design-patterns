"""
Iterator Design Pattern - Real World Implementation

Real-world example: Database Result Set Iterator and Data Processing Pipeline
A comprehensive data processing system that provides iterators for different data sources
(database results, CSV files, API responses) with filtering, transformation, and pagination.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Iterator, Generic, TypeVar, Union
from datetime import datetime
import json
import csv
import io
import time
import random

T = TypeVar('T')


class DataRecord:
    """Represents a single data record with metadata."""
    
    def __init__(self, data: Dict[str, Any], source: str = "unknown", 
                 timestamp: datetime = None, row_number: int = 0):
        self.data = data
        self.source = source
        self.timestamp = timestamp or datetime.now()
        self.row_number = row_number
        self.processed = False
        self.errors: List[str] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the data record."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the data record."""
        self.data[key] = value
    
    def has_error(self) -> bool:
        """Check if record has any errors."""
        return len(self.errors) > 0
    
    def add_error(self, error: str) -> None:
        """Add an error to the record."""
        self.errors.append(error)
    
    def mark_processed(self) -> None:
        """Mark record as processed."""
        self.processed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "row_number": self.row_number,
            "processed": self.processed,
            "errors": self.errors
        }


class DataIterator(ABC, Generic[T]):
    """
    Abstract iterator interface for data sources.
    """
    
    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        pass
    
    @abstractmethod
    def __next__(self) -> T:
        pass
    
    @abstractmethod
    def has_next(self) -> bool:
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset iterator to beginning."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the data source."""
        pass


class DatabaseResultIterator(DataIterator[DataRecord]):
    """
    Iterator for simulated database result sets with pagination.
    """
    
    def __init__(self, query: str, connection_params: Dict[str, Any], 
                 page_size: int = 100):
        self.query = query
        self.connection_params = connection_params
        self.page_size = page_size
        self.current_page = 0
        self.current_index = 0
        self.current_batch: List[DataRecord] = []
        self.total_records = 0
        self.fetched_records = 0
        self.is_exhausted = False
        
        # Simulate database connection
        self._simulate_connection()
        self._fetch_next_batch()
    
    def _simulate_connection(self) -> None:
        """Simulate database connection and get total record count."""
        print(f"🔗 Connecting to database: {self.connection_params.get('host', 'localhost')}")
        time.sleep(0.1)  # Simulate connection time
        
        # Simulate getting total count
        self.total_records = random.randint(250, 1000)
        print(f"📊 Query will return approximately {self.total_records} records")
    
    def _fetch_next_batch(self) -> None:
        """Fetch next batch of records from database."""
        if self.is_exhausted:
            return
        
        print(f"📥 Fetching page {self.current_page + 1} (records {self.fetched_records + 1}-{min(self.fetched_records + self.page_size, self.total_records)})")
        
        # Simulate database query execution time
        time.sleep(0.05)
        
        batch_size = min(self.page_size, self.total_records - self.fetched_records)
        
        if batch_size <= 0:
            self.is_exhausted = True
            self.current_batch = []
            return
        
        # Generate simulated records
        self.current_batch = []
        for i in range(batch_size):
            record_id = self.fetched_records + i + 1
            data = {
                "id": record_id,
                "name": f"User {record_id}",
                "email": f"user{record_id}@example.com",
                "age": random.randint(18, 80),
                "department": random.choice(["Engineering", "Marketing", "Sales", "HR", "Finance"]),
                "salary": random.randint(30000, 150000),
                "created_at": datetime.now().isoformat()
            }
            
            record = DataRecord(
                data=data,
                source=f"database:{self.connection_params.get('database', 'main')}",
                row_number=record_id
            )
            self.current_batch.append(record)
        
        self.fetched_records += batch_size
        self.current_page += 1
        self.current_index = 0
    
    def __iter__(self) -> Iterator[DataRecord]:
        return self
    
    def __next__(self) -> DataRecord:
        if not self.has_next():
            raise StopIteration
        
        # If we've exhausted current batch, fetch next one
        if self.current_index >= len(self.current_batch):
            self._fetch_next_batch()
            if not self.current_batch:
                raise StopIteration
        
        record = self.current_batch[self.current_index]
        self.current_index += 1
        return record
    
    def has_next(self) -> bool:
        return (self.current_index < len(self.current_batch) or 
                not self.is_exhausted)
    
    def reset(self) -> None:
        """Reset iterator to beginning."""
        self.current_page = 0
        self.current_index = 0
        self.fetched_records = 0
        self.is_exhausted = False
        self.current_batch = []
        self._fetch_next_batch()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "database",
            "query": self.query,
            "total_records": self.total_records,
            "fetched_records": self.fetched_records,
            "page_size": self.page_size,
            "current_page": self.current_page,
            "connection": self.connection_params
        }


class CSVFileIterator(DataIterator[DataRecord]):
    """
    Iterator for CSV files with header parsing and type conversion.
    """
    
    def __init__(self, csv_content: str, delimiter: str = ',', 
                 has_header: bool = True, type_mappings: Dict[str, Callable] = None):
        self.csv_content = csv_content
        self.delimiter = delimiter
        self.has_header = has_header
        self.type_mappings = type_mappings or {}
        
        self.headers: List[str] = []
        self.rows: List[List[str]] = []
        self.current_index = 0
        self.total_rows = 0
        self.source_name = "csv_file"
        
        self._parse_csv()
    
    def _parse_csv(self) -> None:
        """Parse CSV content into rows and headers."""
        csv_reader = csv.reader(io.StringIO(self.csv_content), delimiter=self.delimiter)
        all_rows = list(csv_reader)
        
        if self.has_header and all_rows:
            self.headers = all_rows[0]
            self.rows = all_rows[1:]
        else:
            # Generate numeric headers if no header row
            if all_rows:
                self.headers = [f"column_{i}" for i in range(len(all_rows[0]))]
                self.rows = all_rows
        
        self.total_rows = len(self.rows)
        print(f"📄 Parsed CSV: {self.total_rows} rows, {len(self.headers)} columns")
    
    def _convert_types(self, row_data: Dict[str, str]) -> Dict[str, Any]:
        """Convert string values to appropriate types."""
        converted = {}
        for key, value in row_data.items():
            if key in self.type_mappings:
                try:
                    converted[key] = self.type_mappings[key](value)
                except (ValueError, TypeError) as e:
                    converted[key] = value  # Keep original if conversion fails
            else:
                # Try to auto-detect and convert
                converted[key] = self._auto_convert(value)
        return converted
    
    def _auto_convert(self, value: str) -> Any:
        """Automatically convert string to appropriate type."""
        if not value or value.lower() in ['null', 'none', '']:
            return None
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Return as string
        return value
    
    def __iter__(self) -> Iterator[DataRecord]:
        return self
    
    def __next__(self) -> DataRecord:
        if not self.has_next():
            raise StopIteration
        
        row = self.rows[self.current_index]
        
        # Create dictionary from headers and row values
        row_dict = {}
        for i, header in enumerate(self.headers):
            value = row[i] if i < len(row) else ""
            row_dict[header] = value
        
        # Convert types
        converted_data = self._convert_types(row_dict)
        
        record = DataRecord(
            data=converted_data,
            source=self.source_name,
            row_number=self.current_index + 1
        )
        
        self.current_index += 1
        return record
    
    def has_next(self) -> bool:
        return self.current_index < len(self.rows)
    
    def reset(self) -> None:
        self.current_index = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "csv",
            "total_rows": self.total_rows,
            "headers": self.headers,
            "delimiter": self.delimiter,
            "has_header": self.has_header,
            "type_mappings": {k: v.__name__ for k, v in self.type_mappings.items()}
        }


class APIResponseIterator(DataIterator[DataRecord]):
    """
    Iterator for paginated API responses.
    """
    
    def __init__(self, base_url: str, api_key: str = "", page_size: int = 50):
        self.base_url = base_url
        self.api_key = api_key
        self.page_size = page_size
        self.current_page = 1
        self.current_index = 0
        self.current_batch: List[DataRecord] = []
        self.total_records = 0
        self.has_more_pages = True
        
        self._fetch_next_page()
    
    def _fetch_next_page(self) -> None:
        """Simulate fetching next page from API."""
        if not self.has_more_pages:
            return
        
        print(f"🌐 Fetching API page {self.current_page} from {self.base_url}")
        
        # Simulate API call delay
        time.sleep(0.1)
        
        # Simulate API response
        page_data = self._simulate_api_response()
        
        self.current_batch = []
        for i, item in enumerate(page_data["items"]):
            record = DataRecord(
                data=item,
                source=f"api:{self.base_url}",
                row_number=((self.current_page - 1) * self.page_size) + i + 1
            )
            self.current_batch.append(record)
        
        self.total_records = page_data["total"]
        self.has_more_pages = page_data["has_more"]
        self.current_index = 0
        
        if self.has_more_pages:
            self.current_page += 1
    
    def _simulate_api_response(self) -> Dict[str, Any]:
        """Simulate API response with pagination."""
        # Calculate items for this page
        items_per_page = min(self.page_size, 150 - (self.current_page - 1) * self.page_size)
        
        if items_per_page <= 0:
            return {"items": [], "total": 150, "has_more": False}
        
        items = []
        for i in range(items_per_page):
            item_id = (self.current_page - 1) * self.page_size + i + 1
            items.append({
                "id": item_id,
                "title": f"Product {item_id}",
                "price": round(random.uniform(10, 500), 2),
                "category": random.choice(["Electronics", "Books", "Clothing", "Home", "Sports"]),
                "rating": round(random.uniform(1, 5), 1),
                "in_stock": random.choice([True, False]),
                "created_at": datetime.now().isoformat()
            })
        
        return {
            "items": items,
            "total": 150,
            "page": self.current_page,
            "page_size": self.page_size,
            "has_more": self.current_page * self.page_size < 150
        }
    
    def __iter__(self) -> Iterator[DataRecord]:
        return self
    
    def __next__(self) -> DataRecord:
        if not self.has_next():
            raise StopIteration
        
        # If we've exhausted current batch, fetch next page
        if self.current_index >= len(self.current_batch):
            self._fetch_next_page()
            if not self.current_batch:
                raise StopIteration
        
        record = self.current_batch[self.current_index]
        self.current_index += 1
        return record
    
    def has_next(self) -> bool:
        return (self.current_index < len(self.current_batch) or 
                self.has_more_pages)
    
    def reset(self) -> None:
        self.current_page = 1
        self.current_index = 0
        self.has_more_pages = True
        self.current_batch = []
        self._fetch_next_page()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "api",
            "base_url": self.base_url,
            "total_records": self.total_records,
            "page_size": self.page_size,
            "current_page": self.current_page,
            "has_more_pages": self.has_more_pages
        }


class FilteredIterator(DataIterator[DataRecord]):
    """
    Iterator decorator that filters records based on criteria.
    """
    
    def __init__(self, source_iterator: DataIterator[DataRecord], 
                 filter_func: Callable[[DataRecord], bool]):
        self.source_iterator = source_iterator
        self.filter_func = filter_func
        self.filtered_count = 0
        self.total_processed = 0
    
    def __iter__(self) -> Iterator[DataRecord]:
        return self
    
    def __next__(self) -> DataRecord:
        while True:
            try:
                record = next(self.source_iterator)
                self.total_processed += 1
                
                if self.filter_func(record):
                    self.filtered_count += 1
                    return record
                # If record doesn't pass filter, continue to next
            except StopIteration:
                raise StopIteration
    
    def has_next(self) -> bool:
        return self.source_iterator.has_next()
    
    def reset(self) -> None:
        self.source_iterator.reset()
        self.filtered_count = 0
        self.total_processed = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        metadata = self.source_iterator.get_metadata()
        metadata.update({
            "type": f"filtered_{metadata['type']}",
            "filtered_count": self.filtered_count,
            "total_processed": self.total_processed,
            "filter_efficiency": (self.filtered_count / self.total_processed * 100) if self.total_processed > 0 else 0
        })
        return metadata


class TransformIterator(DataIterator[DataRecord]):
    """
    Iterator decorator that transforms records.
    """
    
    def __init__(self, source_iterator: DataIterator[DataRecord], 
                 transform_func: Callable[[DataRecord], DataRecord]):
        self.source_iterator = source_iterator
        self.transform_func = transform_func
        self.transformed_count = 0
        self.error_count = 0
    
    def __iter__(self) -> Iterator[DataRecord]:
        return self
    
    def __next__(self) -> DataRecord:
        record = next(self.source_iterator)
        
        try:
            transformed_record = self.transform_func(record)
            self.transformed_count += 1
            return transformed_record
        except Exception as e:
            # Add error to record and return it
            record.add_error(f"Transformation error: {str(e)}")
            self.error_count += 1
            return record
    
    def has_next(self) -> bool:
        return self.source_iterator.has_next()
    
    def reset(self) -> None:
        self.source_iterator.reset()
        self.transformed_count = 0
        self.error_count = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        metadata = self.source_iterator.get_metadata()
        metadata.update({
            "type": f"transformed_{metadata['type']}",
            "transformed_count": self.transformed_count,
            "error_count": self.error_count
        })
        return metadata


class BatchIterator(DataIterator[List[DataRecord]]):
    """
    Iterator that groups records into batches.
    """
    
    def __init__(self, source_iterator: DataIterator[DataRecord], batch_size: int):
        self.source_iterator = source_iterator
        self.batch_size = batch_size
        self.batch_count = 0
    
    def __iter__(self) -> Iterator[List[DataRecord]]:
        return self
    
    def __next__(self) -> List[DataRecord]:
        batch = []
        
        for _ in range(self.batch_size):
            try:
                record = next(self.source_iterator)
                batch.append(record)
            except StopIteration:
                break
        
        if not batch:
            raise StopIteration
        
        self.batch_count += 1
        return batch
    
    def has_next(self) -> bool:
        return self.source_iterator.has_next()
    
    def reset(self) -> None:
        self.source_iterator.reset()
        self.batch_count = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        metadata = self.source_iterator.get_metadata()
        metadata.update({
            "type": f"batched_{metadata['type']}",
            "batch_size": self.batch_size,
            "batch_count": self.batch_count
        })
        return metadata


class DataProcessingPipeline:
    """
    Data processing pipeline that chains multiple iterators.
    """
    
    def __init__(self, source_iterator: DataIterator):
        self.source_iterator = source_iterator
        self.pipeline_steps: List[str] = []
        self.current_iterator = source_iterator
    
    def filter(self, filter_func: Callable[[DataRecord], bool], 
               description: str = "filter") -> 'DataProcessingPipeline':
        """Add a filter step to the pipeline."""
        self.current_iterator = FilteredIterator(self.current_iterator, filter_func)
        self.pipeline_steps.append(f"Filter: {description}")
        return self
    
    def transform(self, transform_func: Callable[[DataRecord], DataRecord], 
                  description: str = "transform") -> 'DataProcessingPipeline':
        """Add a transform step to the pipeline."""
        self.current_iterator = TransformIterator(self.current_iterator, transform_func)
        self.pipeline_steps.append(f"Transform: {description}")
        return self
    
    def batch(self, batch_size: int) -> 'DataProcessingPipeline':
        """Add a batching step to the pipeline."""
        self.current_iterator = BatchIterator(self.current_iterator, batch_size)
        self.pipeline_steps.append(f"Batch: size={batch_size}")
        return self
    
    def execute(self) -> List[Any]:
        """Execute the pipeline and return all results."""
        results = []
        
        print(f"🔄 Executing pipeline with {len(self.pipeline_steps)} steps:")
        for i, step in enumerate(self.pipeline_steps, 1):
            print(f"  {i}. {step}")
        
        start_time = time.time()
        
        try:
            for item in self.current_iterator:
                results.append(item)
        except StopIteration:
            pass
        
        execution_time = time.time() - start_time
        
        print(f"✅ Pipeline completed in {execution_time:.3f}s")
        print(f"📊 Processed {len(results)} items")
        
        return results
    
    def get_iterator(self) -> DataIterator:
        """Get the final iterator from the pipeline."""
        return self.current_iterator
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the pipeline."""
        return {
            "pipeline_steps": self.pipeline_steps,
            "final_iterator": self.current_iterator.get_metadata()
        }


def main():
    """
    Demonstrate the Data Processing Iterator system.
    """
    print("=== Data Processing Iterator System Demo ===")
    
    # Test 1: Database Result Iterator
    print("\n🗄️  Test 1: Database Result Iterator")
    
    db_params = {
        "host": "localhost",
        "database": "users_db",
        "username": "admin",
        "password": "secret"
    }
    
    db_iterator = DatabaseResultIterator(
        query="SELECT * FROM users WHERE active = true",
        connection_params=db_params,
        page_size=25
    )
    
    # Process first few records
    count = 0
    for record in db_iterator:
        if count >= 5:  # Just show first 5 for demo
            break
        print(f"  Record {record.row_number}: {record.get('name')} - {record.get('department')}")
        count += 1
    
    print(f"📊 Database metadata: {db_iterator.get_metadata()}")
    
    # Test 2: CSV File Iterator
    print("\n📄 Test 2: CSV File Iterator")
    
    csv_data = """name,age,department,salary,active
John Doe,30,Engineering,75000,true
Jane Smith,25,Marketing,65000,true
Bob Johnson,35,Sales,55000,false
Alice Brown,28,Engineering,80000,true
Charlie Wilson,32,HR,60000,true
Diana Davis,27,Marketing,62000,true"""
    
    csv_iterator = CSVFileIterator(
        csv_content=csv_data,
        type_mappings={
            "age": int,
            "salary": int,
            "active": lambda x: x.lower() == 'true'
        }
    )
    
    print("CSV Records:")
    for record in csv_iterator:
        print(f"  {record.get('name')}: {record.get('age')} years, ${record.get('salary'):,}, Active: {record.get('active')}")
    
    # Test 3: API Response Iterator
    print("\n🌐 Test 3: API Response Iterator")
    
    api_iterator = APIResponseIterator(
        base_url="https://api.example.com/products",
        api_key="api_key_123",
        page_size=10
    )
    
    # Show first few API records
    count = 0
    for record in api_iterator:
        if count >= 8:  # Just show first 8 for demo
            break
        product = record.data
        print(f"  Product {product['id']}: {product['title']} - ${product['price']} ({product['category']})")
        count += 1
    
    # Test 4: Filtered Iterator
    print("\n🔍 Test 4: Filtered Iterator")
    
    # Reset CSV iterator for filtering
    csv_iterator.reset()
    
    # Filter for Engineering department with salary > 70000
    filtered_iterator = FilteredIterator(
        csv_iterator,
        lambda record: (record.get('department') == 'Engineering' and 
                       record.get('salary', 0) > 70000)
    )
    
    print("Filtered Records (Engineering, Salary > 70k):")
    for record in filtered_iterator:
        print(f"  {record.get('name')}: {record.get('department')} - ${record.get('salary'):,}")
    
    # Test 5: Transform Iterator
    print("\n🔄 Test 5: Transform Iterator")
    
    # Reset and transform data
    csv_iterator.reset()
    
    def add_bonus_calculation(record: DataRecord) -> DataRecord:
        salary = record.get('salary', 0)
        age = record.get('age', 0)
        
        # Calculate bonus based on salary and age
        base_bonus = salary * 0.1
        age_bonus = age * 100
        total_bonus = base_bonus + age_bonus
        
        record.set('bonus', total_bonus)
        record.set('total_compensation', salary + total_bonus)
        return record
    
    transform_iterator = TransformIterator(csv_iterator, add_bonus_calculation)
    
    print("Transformed Records (with bonus calculation):")
    for record in transform_iterator:
        print(f"  {record.get('name')}: Salary ${record.get('salary'):,}, "
              f"Bonus ${record.get('bonus'):,.0f}, "
              f"Total ${record.get('total_compensation'):,.0f}")
    
    # Test 6: Batch Iterator
    print("\n📦 Test 6: Batch Iterator")
    
    # Reset CSV iterator for batching
    csv_iterator.reset()
    
    batch_iterator = BatchIterator(csv_iterator, batch_size=3)
    
    batch_num = 1
    for batch in batch_iterator:
        print(f"  Batch {batch_num} ({len(batch)} records):")
        for record in batch:
            print(f"    - {record.get('name')} ({record.get('department')})")
        batch_num += 1
    
    # Test 7: Complete Data Processing Pipeline
    print("\n🔧 Test 7: Complete Data Processing Pipeline")
    
    # Create a new database iterator for the pipeline
    pipeline_db_iterator = DatabaseResultIterator(
        query="SELECT * FROM users WHERE department IN ('Engineering', 'Marketing')",
        connection_params=db_params,
        page_size=50
    )
    
    # Build processing pipeline
    pipeline = DataProcessingPipeline(pipeline_db_iterator)
    
    # Add pipeline steps
    pipeline.filter(
        lambda record: record.get('age', 0) >= 25,
        "age >= 25"
    ).filter(
        lambda record: record.get('salary', 0) >= 60000,
        "salary >= 60000"
    ).transform(
        lambda record: add_bonus_calculation(record),
        "calculate bonus and total compensation"
    ).transform(
        lambda record: add_performance_rating(record),
        "add performance rating"
    )
    
    def add_performance_rating(record: DataRecord) -> DataRecord:
        """Add performance rating based on age and salary."""
        age = record.get('age', 0)
        salary = record.get('salary', 0)
        
        # Simple performance rating algorithm
        if salary >= 80000 and age >= 30:
            rating = "Excellent"
        elif salary >= 65000 and age >= 25:
            rating = "Good"
        else:
            rating = "Average"
        
        record.set('performance_rating', rating)
        return record
    
    # Execute pipeline
    results = pipeline.execute()
    
    print(f"\n📊 Pipeline Results:")
    print(f"  Total records processed: {len(results)}")
    
    # Show sample results
    print(f"  Sample results (first 5):")
    for i, record in enumerate(results[:5]):
        print(f"    {i+1}. {record.get('name')}: "
              f"{record.get('department')}, "
              f"Age {record.get('age')}, "
              f"Salary ${record.get('salary'):,}, "
              f"Rating: {record.get('performance_rating')}")
    
    # Get pipeline metadata
    pipeline_metadata = pipeline.get_metadata()
    print(f"\n📋 Pipeline Metadata:")
    print(f"  Steps: {len(pipeline_metadata['pipeline_steps'])}")
    for step in pipeline_metadata['pipeline_steps']:
        print(f"    - {step}")
    
    # Test 8: Iterator Chaining and Reset
    print("\n🔄 Test 8: Iterator Reset and Reuse")
    
    print("Original CSV data (first iteration):")
    csv_iterator.reset()
    names_first = [record.get('name') for record in csv_iterator]
    print(f"  Names: {names_first}")
    
    print("Reset and iterate again:")
    csv_iterator.reset()
    names_second = [record.get('name') for record in csv_iterator]
    print(f"  Names: {names_second}")
    print(f"  Same data: {names_first == names_second}")
    
    # Performance statistics
    print("\n📊 Performance Statistics:")
    print(f"  Data sources tested: 3 (Database, CSV, API)")
    print(f"  Iterator decorators: 3 (Filter, Transform, Batch)")
    print(f"  Pipeline complexity: Multi-step with chaining")
    print(f"  Memory efficiency: Lazy evaluation with pagination")
    print(f"  Error handling: Integrated error tracking")
    print(f"  Reusability: Reset functionality for re-iteration")


if __name__ == "__main__":
    main()