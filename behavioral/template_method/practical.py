"""
Template Method Design Pattern - Real World Implementation

Real-world example: Data ETL (Extract, Transform, Load) Pipeline
A comprehensive ETL system that processes data from various sources (CSV, JSON, XML, API)
using a common pipeline structure while allowing source-specific customizations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json
import csv
import xml.etree.ElementTree as ET
import io
import time
import re


class DataValidationError(Exception):
    """Exception raised when data validation fails."""
    pass


class ETLMetrics:
    """Metrics container for ETL operations."""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.records_extracted = 0
        self.records_transformed = 0
        self.records_loaded = 0
        self.errors_count = 0
        self.warnings_count = 0
        self.validation_failures = 0
        self.transformation_time = 0.0
        self.load_time = 0.0
        self.total_time = 0.0
    
    def start_processing(self) -> None:
        """Mark the start of ETL processing."""
        self.start_time = datetime.now()
    
    def end_processing(self) -> None:
        """Mark the end of ETL processing."""
        self.end_time = datetime.now()
        if self.start_time:
            self.total_time = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "records_extracted": self.records_extracted,
            "records_transformed": self.records_transformed,
            "records_loaded": self.records_loaded,
            "errors_count": self.errors_count,
            "warnings_count": self.warnings_count,
            "validation_failures": self.validation_failures,
            "transformation_time": self.transformation_time,
            "load_time": self.load_time,
            "total_time": self.total_time,
            "success_rate": (self.records_loaded / self.records_extracted * 100) if self.records_extracted > 0 else 0
        }


class DataETLPipeline(ABC):
    """
    Abstract ETL pipeline that defines the template for data processing.
    
    The template method defines the skeleton of the ETL algorithm:
    1. Initialize
    2. Extract data from source
    3. Validate extracted data
    4. Transform data
    5. Validate transformed data
    6. Load data to destination
    7. Cleanup and finalize
    """
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        self.source_config = source_config
        self.target_config = target_config
        self.metrics = ETLMetrics()
        self.logger: List[str] = []
        self.raw_data: Any = None
        self.transformed_data: List[Dict[str, Any]] = []
        self.validation_rules: List[Callable] = []
        self.transformation_rules: List[Callable] = []
    
    def run_etl(self) -> ETLMetrics:
        """
        Template method that defines the ETL process flow.
        This is the main algorithm that subclasses should not override.
        """
        try:
            self.metrics.start_processing()
            self.log("Starting ETL pipeline")
            
            # Step 1: Initialize
            self.initialize()
            
            # Step 2: Extract
            self.log("Extracting data from source")
            self.raw_data = self.extract_data()
            self.metrics.records_extracted = self.count_extracted_records()
            self.log(f"Extracted {self.metrics.records_extracted} records")
            
            # Step 3: Validate raw data
            if self.should_validate_raw_data():
                self.log("Validating raw data")
                self.validate_raw_data()
            
            # Step 4: Transform
            self.log("Transforming data")
            transform_start = time.time()
            self.transformed_data = self.transform_data()
            self.metrics.transformation_time = time.time() - transform_start
            self.metrics.records_transformed = len(self.transformed_data)
            self.log(f"Transformed {self.metrics.records_transformed} records")
            
            # Step 5: Validate transformed data
            if self.should_validate_transformed_data():
                self.log("Validating transformed data")
                self.validate_transformed_data()
            
            # Step 6: Load
            self.log("Loading data to destination")
            load_start = time.time()
            self.load_data()
            self.metrics.load_time = time.time() - load_start
            self.metrics.records_loaded = self.count_loaded_records()
            self.log(f"Loaded {self.metrics.records_loaded} records")
            
            # Step 7: Cleanup
            self.cleanup()
            self.log("ETL pipeline completed successfully")
            
        except Exception as e:
            self.metrics.errors_count += 1
            self.log(f"ETL pipeline failed: {str(e)}")
            self.handle_error(e)
            raise
        
        finally:
            self.metrics.end_processing()
            self.finalize()
        
        return self.metrics
    
    # Template method steps - subclasses implement these
    
    def initialize(self) -> None:
        """Initialize the ETL process. Override if needed."""
        pass
    
    @abstractmethod
    def extract_data(self) -> Any:
        """Extract data from the source. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def transform_data(self) -> List[Dict[str, Any]]:
        """Transform the extracted data. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def load_data(self) -> None:
        """Load transformed data to destination. Must be implemented by subclasses."""
        pass
    
    # Hook methods - subclasses can override these
    
    def should_validate_raw_data(self) -> bool:
        """Hook: Whether to validate raw data. Override to customize."""
        return True
    
    def should_validate_transformed_data(self) -> bool:
        """Hook: Whether to validate transformed data. Override to customize."""
        return True
    
    def validate_raw_data(self) -> None:
        """Hook: Validate raw data. Override to add custom validation."""
        if self.raw_data is None:
            raise DataValidationError("No raw data to validate")
    
    def validate_transformed_data(self) -> None:
        """Hook: Validate transformed data. Override to add custom validation."""
        if not self.transformed_data:
            self.metrics.warnings_count += 1
            self.log("Warning: No transformed data to validate")
    
    def cleanup(self) -> None:
        """Hook: Cleanup resources. Override if needed."""
        pass
    
    def finalize(self) -> None:
        """Hook: Finalize the ETL process. Override if needed."""
        self.log("ETL pipeline finalized")
    
    def handle_error(self, error: Exception) -> None:
        """Hook: Handle errors. Override to add custom error handling."""
        self.log(f"Error handled: {str(error)}")
    
    # Utility methods
    
    def count_extracted_records(self) -> int:
        """Count extracted records. Override if needed."""
        if isinstance(self.raw_data, list):
            return len(self.raw_data)
        elif isinstance(self.raw_data, dict):
            return 1
        elif isinstance(self.raw_data, str):
            return len(self.raw_data.split('\n')) if self.raw_data else 0
        return 1 if self.raw_data else 0
    
    def count_loaded_records(self) -> int:
        """Count loaded records. Override if needed."""
        return len(self.transformed_data)
    
    def log(self, message: str) -> None:
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logger.append(log_entry)
        print(log_entry)
    
    def add_validation_rule(self, rule: Callable[[Dict[str, Any]], bool]) -> None:
        """Add a validation rule for transformed data."""
        self.validation_rules.append(rule)
    
    def add_transformation_rule(self, rule: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Add a transformation rule."""
        self.transformation_rules.append(rule)


class CSVETLPipeline(DataETLPipeline):
    """
    ETL pipeline for processing CSV files.
    """
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config)
        self.csv_data: List[Dict[str, Any]] = []
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """Extract data from CSV file or string."""
        csv_source = self.source_config.get('data', '')
        delimiter = self.source_config.get('delimiter', ',')
        
        # Simulate reading CSV data
        csv_reader = csv.DictReader(io.StringIO(csv_source), delimiter=delimiter)
        self.csv_data = list(csv_reader)
        return self.csv_data
    
    def validate_raw_data(self) -> None:
        """Validate CSV structure."""
        super().validate_raw_data()
        
        if not self.csv_data:
            raise DataValidationError("CSV file is empty")
        
        # Check for required columns
        required_columns = self.source_config.get('required_columns', [])
        if required_columns:
            first_row = self.csv_data[0]
            missing_columns = [col for col in required_columns if col not in first_row]
            if missing_columns:
                raise DataValidationError(f"Missing required columns: {missing_columns}")
    
    def transform_data(self) -> List[Dict[str, Any]]:
        """Transform CSV data with type conversion and cleaning."""
        transformed = []
        
        for row in self.csv_data:
            try:
                # Apply basic transformations
                cleaned_row = {}
                for key, value in row.items():
                    # Clean whitespace
                    if isinstance(value, str):
                        value = value.strip()
                    
                    # Convert data types based on configuration
                    type_mappings = self.source_config.get('type_mappings', {})
                    if key in type_mappings:
                        target_type = type_mappings[key]
                        if target_type == 'int':
                            value = int(float(value)) if value else 0
                        elif target_type == 'float':
                            value = float(value) if value else 0.0
                        elif target_type == 'bool':
                            value = value.lower() in ('true', '1', 'yes', 'on')
                    
                    cleaned_row[key] = value
                
                # Apply custom transformation rules
                for rule in self.transformation_rules:
                    cleaned_row = rule(cleaned_row)
                
                # Add metadata
                cleaned_row['_etl_timestamp'] = datetime.now().isoformat()
                cleaned_row['_etl_source'] = 'csv'
                
                transformed.append(cleaned_row)
                
            except Exception as e:
                self.metrics.errors_count += 1
                self.log(f"Error transforming row {len(transformed) + 1}: {str(e)}")
        
        return transformed
    
    def load_data(self) -> None:
        """Load data to target (simulated)."""
        target_type = self.target_config.get('type', 'database')
        
        if target_type == 'database':
            self._load_to_database()
        elif target_type == 'file':
            self._load_to_file()
        else:
            self.log(f"Loading {len(self.transformed_data)} records to {target_type}")
    
    def _load_to_database(self) -> None:
        """Simulate loading to database."""
        table_name = self.target_config.get('table_name', 'etl_data')
        batch_size = self.target_config.get('batch_size', 1000)
        
        for i in range(0, len(self.transformed_data), batch_size):
            batch = self.transformed_data[i:i + batch_size]
            self.log(f"Loading batch {i//batch_size + 1} ({len(batch)} records) to table {table_name}")
            time.sleep(0.1)  # Simulate database operation
    
    def _load_to_file(self) -> None:
        """Simulate loading to file."""
        filename = self.target_config.get('filename', 'output.json')
        self.log(f"Writing {len(self.transformed_data)} records to {filename}")


class JSONETLPipeline(DataETLPipeline):
    """
    ETL pipeline for processing JSON data.
    """
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config)
        self.json_data: Any = None
    
    def extract_data(self) -> Any:
        """Extract data from JSON source."""
        json_source = self.source_config.get('data', '{}')
        
        try:
            self.json_data = json.loads(json_source)
            return self.json_data
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON format: {str(e)}")
    
    def validate_raw_data(self) -> None:
        """Validate JSON structure."""
        super().validate_raw_data()
        
        # Check for required schema
        required_schema = self.source_config.get('required_schema', {})
        if required_schema:
            self._validate_schema(self.json_data, required_schema)
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """Validate JSON against schema."""
        if isinstance(data, dict):
            for key, expected_type in schema.items():
                if key not in data:
                    raise DataValidationError(f"Missing required field: {key}")
                
                actual_value = data[key]
                if expected_type == 'string' and not isinstance(actual_value, str):
                    raise DataValidationError(f"Field {key} should be string, got {type(actual_value)}")
                elif expected_type == 'number' and not isinstance(actual_value, (int, float)):
                    raise DataValidationError(f"Field {key} should be number, got {type(actual_value)}")
    
    def transform_data(self) -> List[Dict[str, Any]]:
        """Transform JSON data into normalized format."""
        transformed = []
        
        # Handle different JSON structures
        if isinstance(self.json_data, list):
            # Array of objects
            for item in self.json_data:
                transformed.append(self._transform_json_object(item))
        elif isinstance(self.json_data, dict):
            # Single object or nested structure
            if self.source_config.get('extract_nested', False):
                # Extract nested arrays
                nested_key = self.source_config.get('nested_key', 'data')
                if nested_key in self.json_data and isinstance(self.json_data[nested_key], list):
                    for item in self.json_data[nested_key]:
                        transformed.append(self._transform_json_object(item))
                else:
                    transformed.append(self._transform_json_object(self.json_data))
            else:
                transformed.append(self._transform_json_object(self.json_data))
        
        return transformed
    
    def _transform_json_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single JSON object."""
        # Flatten nested objects if configured
        if self.source_config.get('flatten_nested', False):
            obj = self._flatten_object(obj)
        
        # Apply field mappings
        field_mappings = self.source_config.get('field_mappings', {})
        if field_mappings:
            mapped_obj = {}
            for old_key, new_key in field_mappings.items():
                if old_key in obj:
                    mapped_obj[new_key] = obj[old_key]
            # Add unmapped fields
            for key, value in obj.items():
                if key not in field_mappings:
                    mapped_obj[key] = value
            obj = mapped_obj
        
        # Add metadata
        obj['_etl_timestamp'] = datetime.now().isoformat()
        obj['_etl_source'] = 'json'
        
        return obj
    
    def _flatten_object(self, obj: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested object structure."""
        flattened = {}
        
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_object(value, new_key))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle array of objects (take first element)
                flattened.update(self._flatten_object(value[0], new_key))
            else:
                flattened[new_key] = value
        
        return flattened
    
    def load_data(self) -> None:
        """Load JSON data to target."""
        self.log(f"Loading {len(self.transformed_data)} JSON records to target")


class XMLETLPipeline(DataETLPipeline):
    """
    ETL pipeline for processing XML data.
    """
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config)
        self.xml_root: Optional[ET.Element] = None
    
    def extract_data(self) -> ET.Element:
        """Extract data from XML source."""
        xml_source = self.source_config.get('data', '<root></root>')
        
        try:
            self.xml_root = ET.fromstring(xml_source)
            return self.xml_root
        except ET.ParseError as e:
            raise DataValidationError(f"Invalid XML format: {str(e)}")
    
    def validate_raw_data(self) -> None:
        """Validate XML structure."""
        super().validate_raw_data()
        
        if self.xml_root is None:
            raise DataValidationError("XML root is None")
        
        # Check for required elements
        required_elements = self.source_config.get('required_elements', [])
        for element_path in required_elements:
            if self.xml_root.find(element_path) is None:
                raise DataValidationError(f"Required XML element not found: {element_path}")
    
    def transform_data(self) -> List[Dict[str, Any]]:
        """Transform XML data to dictionary format."""
        transformed = []
        
        # Extract elements based on configuration
        element_selector = self.source_config.get('element_selector', './/*')
        elements = self.xml_root.findall(element_selector)
        
        for element in elements:
            obj = self._xml_element_to_dict(element)
            
            # Add metadata
            obj['_etl_timestamp'] = datetime.now().isoformat()
            obj['_etl_source'] = 'xml'
            obj['_xml_tag'] = element.tag
            
            transformed.append(obj)
        
        return transformed
    
    def _xml_element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            for attr_name, attr_value in element.attrib.items():
                result[f"@{attr_name}"] = attr_value
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_dict = self._xml_element_to_dict(child)
            if child.tag in result:
                # Handle multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        
        return result
    
    def load_data(self) -> None:
        """Load XML data to target."""
        self.log(f"Loading {len(self.transformed_data)} XML records to target")


class APIETLPipeline(DataETLPipeline):
    """
    ETL pipeline for processing API responses.
    """
    
    def __init__(self, source_config: Dict[str, Any], target_config: Dict[str, Any]):
        super().__init__(source_config, target_config)
        self.api_response: Any = None
    
    def extract_data(self) -> Any:
        """Extract data from API (simulated)."""
        # Simulate API call
        api_url = self.source_config.get('url', 'https://api.example.com/data')
        self.log(f"Calling API: {api_url}")
        
        # Simulate API response delay
        time.sleep(0.2)
        
        # Use mock data for demo
        mock_response = self.source_config.get('mock_data', {
            "status": "success",
            "data": [
                {"id": 1, "name": "Item 1", "value": 100},
                {"id": 2, "name": "Item 2", "value": 200}
            ],
            "meta": {"total": 2, "page": 1}
        })
        
        self.api_response = mock_response
        return self.api_response
    
    def validate_raw_data(self) -> None:
        """Validate API response."""
        super().validate_raw_data()
        
        if not isinstance(self.api_response, dict):
            raise DataValidationError("API response is not a valid JSON object")
        
        # Check for API errors
        if self.api_response.get('status') == 'error':
            error_message = self.api_response.get('message', 'Unknown API error')
            raise DataValidationError(f"API returned error: {error_message}")
        
        # Check for required response fields
        required_fields = self.source_config.get('required_response_fields', ['data'])
        for field in required_fields:
            if field not in self.api_response:
                raise DataValidationError(f"API response missing required field: {field}")
    
    def transform_data(self) -> List[Dict[str, Any]]:
        """Transform API response data."""
        data_key = self.source_config.get('data_key', 'data')
        api_data = self.api_response.get(data_key, [])
        
        if not isinstance(api_data, list):
            api_data = [api_data]  # Convert single object to list
        
        transformed = []
        for item in api_data:
            # Add API metadata
            item['_etl_timestamp'] = datetime.now().isoformat()
            item['_etl_source'] = 'api'
            item['_api_url'] = self.source_config.get('url', 'unknown')
            
            # Add pagination info if available
            meta = self.api_response.get('meta', {})
            if meta:
                item['_api_page'] = meta.get('page', 1)
                item['_api_total'] = meta.get('total', len(api_data))
            
            transformed.append(item)
        
        return transformed
    
    def should_validate_raw_data(self) -> bool:
        """Always validate API responses."""
        return True
    
    def load_data(self) -> None:
        """Load API data to target."""
        self.log(f"Loading {len(self.transformed_data)} API records to target")


def main():
    """
    Demonstrate the ETL Template Method pattern with different data sources.
    """
    print("=== ETL Pipeline Template Method Demo ===")
    
    # CSV ETL Pipeline
    print("\n📄 CSV ETL Pipeline:")
    csv_config = {
        'data': '''name,age,email,salary
John Doe,30,john@example.com,50000
Jane Smith,25,jane@example.com,60000
Bob Johnson,35,bob@example.com,55000
Alice Brown,28,alice@example.com,65000''',
        'delimiter': ',',
        'required_columns': ['name', 'email'],
        'type_mappings': {
            'age': 'int',
            'salary': 'float'
        }
    }
    
    target_config = {
        'type': 'database',
        'table_name': 'employees',
        'batch_size': 2
    }
    
    csv_pipeline = CSVETLPipeline(csv_config, target_config)
    
    # Add validation rule
    def validate_age(record):
        age = record.get('age', 0)
        if age < 18 or age > 100:
            raise DataValidationError(f"Invalid age: {age}")
        return True
    
    csv_pipeline.add_validation_rule(validate_age)
    
    # Add transformation rule
    def add_age_group(record):
        age = record.get('age', 0)
        if age < 30:
            record['age_group'] = 'young'
        elif age < 50:
            record['age_group'] = 'middle'
        else:
            record['age_group'] = 'senior'
        return record
    
    csv_pipeline.add_transformation_rule(add_age_group)
    
    csv_metrics = csv_pipeline.run_etl()
    print(f"CSV ETL Results: {csv_metrics.to_dict()}")
    
    # JSON ETL Pipeline
    print("\n📄 JSON ETL Pipeline:")
    json_config = {
        'data': '''{
            "users": [
                {"id": 1, "profile": {"name": "John", "details": {"age": 30, "city": "NYC"}}},
                {"id": 2, "profile": {"name": "Jane", "details": {"age": 25, "city": "LA"}}},
                {"id": 3, "profile": {"name": "Bob", "details": {"age": 35, "city": "Chicago"}}}
            ],
            "metadata": {"total": 3, "source": "user_api"}
        }''',
        'extract_nested': True,
        'nested_key': 'users',
        'flatten_nested': True,
        'field_mappings': {
            'profile.name': 'full_name',
            'profile.details.age': 'user_age',
            'profile.details.city': 'location'
        }
    }
    
    json_pipeline = JSONETLPipeline(json_config, target_config)
    json_metrics = json_pipeline.run_etl()
    print(f"JSON ETL Results: {json_metrics.to_dict()}")
    
    # XML ETL Pipeline
    print("\n📄 XML ETL Pipeline:")
    xml_config = {
        'data': '''<?xml version="1.0"?>
        <products>
            <product id="1" category="electronics">
                <name>Laptop</name>
                <price>999.99</price>
                <specs>
                    <cpu>Intel i7</cpu>
                    <ram>16GB</ram>
                </specs>
            </product>
            <product id="2" category="electronics">
                <name>Phone</name>
                <price>699.99</price>
                <specs>
                    <cpu>A15 Bionic</cpu>
                    <ram>6GB</ram>
                </specs>
            </product>
        </products>''',
        'element_selector': './/product',
        'required_elements': ['name', 'price']
    }
    
    xml_pipeline = XMLETLPipeline(xml_config, target_config)
    xml_metrics = xml_pipeline.run_etl()
    print(f"XML ETL Results: {xml_metrics.to_dict()}")
    
    # API ETL Pipeline
    print("\n📄 API ETL Pipeline:")
    api_config = {
        'url': 'https://api.example.com/products',
        'mock_data': {
            "status": "success",
            "data": [
                {"product_id": "P001", "name": "Widget A", "price": 29.99, "category": "tools"},
                {"product_id": "P002", "name": "Widget B", "price": 39.99, "category": "tools"},
                {"product_id": "P003", "name": "Gadget C", "price": 49.99, "category": "electronics"}
            ],
            "meta": {"total": 3, "page": 1, "per_page": 10}
        },
        'data_key': 'data',
        'required_response_fields': ['status', 'data']
    }
    
    api_pipeline = APIETLPipeline(api_config, target_config)
    api_metrics = api_pipeline.run_etl()
    print(f"API ETL Results: {api_metrics.to_dict()}")
    
    # Test error handling
    print("\n📄 Error Handling Demo:")
    
    # Create a pipeline with invalid data
    invalid_csv_config = {
        'data': '''name,age,email
John Doe,invalid_age,john@example.com
Jane Smith,25,invalid_email''',
        'required_columns': ['name', 'age', 'email'],
        'type_mappings': {'age': 'int'}
    }
    
    error_pipeline = CSVETLPipeline(invalid_csv_config, target_config)
    
    try:
        error_metrics = error_pipeline.run_etl()
        print(f"Error pipeline completed with {error_metrics.errors_count} errors")
    except Exception as e:
        print(f"Pipeline failed as expected: {str(e)}")
    
    # Performance comparison
    print("\n📊 Performance Comparison:")
    
    pipelines_results = [
        ("CSV", csv_metrics),
        ("JSON", json_metrics),
        ("XML", xml_metrics),
        ("API", api_metrics)
    ]
    
    print("Pipeline | Records | Success Rate | Total Time | Transform Time | Load Time")
    print("-" * 80)
    
    for name, metrics in pipelines_results:
        print(f"{name:8} | {metrics.records_extracted:7} | "
              f"{metrics.to_dict()['success_rate']:10.1f}% | "
              f"{metrics.total_time:9.3f}s | "
              f"{metrics.transformation_time:12.3f}s | "
              f"{metrics.load_time:8.3f}s")
    
    # Custom pipeline demonstration
    print("\n📄 Custom Pipeline with Hooks:")
    
    class CustomCSVPipeline(CSVETLPipeline):
        """Custom CSV pipeline with additional hooks."""
        
        def initialize(self):
            """Custom initialization."""
            super().initialize()
            self.log("Custom CSV pipeline initializing with enhanced features")
            self.processed_count = 0
        
        def should_validate_transformed_data(self) -> bool:
            """Always validate in custom pipeline."""
            return True
        
        def validate_transformed_data(self) -> None:
            """Custom validation with business rules."""
            super().validate_transformed_data()
            
            for record in self.transformed_data:
                # Business rule: salary must be reasonable
                if 'salary' in record and record['salary'] > 200000:
                    self.metrics.warnings_count += 1
                    self.log(f"Warning: High salary detected for {record.get('name', 'unknown')}")
        
        def cleanup(self) -> None:
            """Custom cleanup."""
            super().cleanup()
            self.log(f"Custom cleanup: Processed {len(self.transformed_data)} records")
        
        def finalize(self) -> None:
            """Custom finalization."""
            super().finalize()
            self.log("Custom pipeline finalized with enhanced reporting")
    
    # Test custom pipeline
    custom_config = {
        'data': '''name,age,email,salary
CEO Bob,45,ceo@example.com,300000
Manager Jane,35,manager@example.com,80000
Developer John,28,dev@example.com,70000''',
        'type_mappings': {'age': 'int', 'salary': 'float'}
    }
    
    custom_pipeline = CustomCSVPipeline(custom_config, target_config)
    custom_metrics = custom_pipeline.run_etl()
    
    print(f"\nCustom Pipeline Results:")
    print(f"  Records processed: {custom_metrics.records_loaded}")
    print(f"  Warnings generated: {custom_metrics.warnings_count}")
    print(f"  Total processing time: {custom_metrics.total_time:.3f}s")
    
    # Show logs from custom pipeline
    print(f"\nCustom Pipeline Logs (last 5):")
    for log_entry in custom_pipeline.logger[-5:]:
        print(f"  {log_entry}")


if __name__ == "__main__":
    main()