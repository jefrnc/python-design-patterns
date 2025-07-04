"""
Abstract Factory Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Protocol classes for structural typing
- Dataclasses for configuration
- Enum for type safety
- Context managers for resource management
- Decorators for factory registration
- Type hints with generics
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic, Dict, Type, Optional, Any, runtime_checkable
from enum import Enum, auto
import functools


class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = auto()
    DOCX = auto()
    HTML = auto()


@dataclass(frozen=True)
class DocumentConfig:
    """Configuration for document creation."""
    title: str
    author: str
    format: DocumentFormat
    encoding: str = "utf-8"
    compress: bool = False


@runtime_checkable
class Document(Protocol):
    """Protocol defining document interface using structural typing."""
    
    def save(self, filename: str) -> str:
        """Save document to file."""
        ...
    
    def get_content(self) -> str:
        """Get document content."""
        ...
    
    def get_metadata(self) -> dict[str, Any]:
        """Get document metadata."""
        ...


@runtime_checkable
class Parser(Protocol):
    """Protocol defining parser interface."""
    
    def parse(self, content: str) -> dict[str, Any]:
        """Parse content and return structured data."""
        ...
    
    def validate(self, data: dict[str, Any]) -> bool:
        """Validate parsed data."""
        ...


@dataclass
class PDFDocument:
    """PDF document implementation."""
    
    config: DocumentConfig
    content: str = ""
    
    def __post_init__(self):
        if self.config.format != DocumentFormat.PDF:
            raise ValueError("Invalid format for PDF document")
    
    def save(self, filename: str) -> str:
        """Save PDF document."""
        result = f"Saving PDF document '{self.config.title}' to {filename}"
        if self.config.compress:
            result += " (compressed)"
        return result
    
    def get_content(self) -> str:
        return f"PDF Content: {self.content}"
    
    def get_metadata(self) -> dict[str, Any]:
        return {
            "title": self.config.title,
            "author": self.config.author,
            "format": "PDF",
            "encoding": self.config.encoding,
            "compressed": self.config.compress,
            "pages": len(self.content.split('\n'))
        }


@dataclass
class DOCXDocument:
    """DOCX document implementation."""
    
    config: DocumentConfig
    content: str = ""
    
    def __post_init__(self):
        if self.config.format != DocumentFormat.DOCX:
            raise ValueError("Invalid format for DOCX document")
    
    def save(self, filename: str) -> str:
        """Save DOCX document."""
        result = f"Saving DOCX document '{self.config.title}' to {filename}"
        if self.config.compress:
            result += " (ZIP compressed)"
        return result
    
    def get_content(self) -> str:
        return f"DOCX Content: {self.content}"
    
    def get_metadata(self) -> dict[str, Any]:
        return {
            "title": self.config.title,
            "author": self.config.author,
            "format": "DOCX",
            "encoding": self.config.encoding,
            "compressed": self.config.compress,
            "word_count": len(self.content.split())
        }


@dataclass
class HTMLDocument:
    """HTML document implementation."""
    
    config: DocumentConfig
    content: str = ""
    
    def __post_init__(self):
        if self.config.format != DocumentFormat.HTML:
            raise ValueError("Invalid format for HTML document")
    
    def save(self, filename: str) -> str:
        """Save HTML document."""
        result = f"Saving HTML document '{self.config.title}' to {filename}"
        if self.config.compress:
            result += " (minified)"
        return result
    
    def get_content(self) -> str:
        return f"<html><head><title>{self.config.title}</title></head><body>{self.content}</body></html>"
    
    def get_metadata(self) -> dict[str, Any]:
        return {
            "title": self.config.title,
            "author": self.config.author,
            "format": "HTML",
            "encoding": self.config.encoding,
            "compressed": self.config.compress,
            "html_tags": self.content.count('<')
        }


class PDFParser:
    """PDF parser implementation."""
    
    def parse(self, content: str) -> dict[str, Any]:
        """Parse PDF content."""
        return {
            "type": "pdf",
            "pages": content.count('\f') + 1,
            "text": content.replace('\f', ' '),
            "metadata": {"parser": "PDF"}
        }
    
    def validate(self, data: dict[str, Any]) -> bool:
        """Validate PDF data."""
        return data.get("type") == "pdf" and "pages" in data


class DOCXParser:
    """DOCX parser implementation."""
    
    def parse(self, content: str) -> dict[str, Any]:
        """Parse DOCX content."""
        return {
            "type": "docx",
            "paragraphs": content.split('\n'),
            "word_count": len(content.split()),
            "metadata": {"parser": "DOCX"}
        }
    
    def validate(self, data: dict[str, Any]) -> bool:
        """Validate DOCX data."""
        return data.get("type") == "docx" and "paragraphs" in data


class HTMLParser:
    """HTML parser implementation."""
    
    def parse(self, content: str) -> dict[str, Any]:
        """Parse HTML content."""
        return {
            "type": "html",
            "tags": content.count('<'),
            "text": content,
            "metadata": {"parser": "HTML"}
        }
    
    def validate(self, data: dict[str, Any]) -> bool:
        """Validate HTML data."""
        return data.get("type") == "html" and "tags" in data


# Type variables for generic factory
T = TypeVar('T')
U = TypeVar('U')


class DocumentFactory(ABC, Generic[T, U]):
    """
    Abstract factory with generic type support.
    """
    
    @abstractmethod
    def create_document(self, config: DocumentConfig) -> T:
        """Create a document of specific type."""
        pass
    
    @abstractmethod
    def create_parser(self) -> U:
        """Create a parser of specific type."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions."""
        pass


class PDFFactory(DocumentFactory[PDFDocument, PDFParser]):
    """Factory for PDF documents and parsers."""
    
    def create_document(self, config: DocumentConfig) -> PDFDocument:
        """Create PDF document."""
        if config.format != DocumentFormat.PDF:
            config = dataclass.replace(config, format=DocumentFormat.PDF)
        return PDFDocument(config)
    
    def create_parser(self) -> PDFParser:
        """Create PDF parser."""
        return PDFParser()
    
    def get_supported_extensions(self) -> list[str]:
        return [".pdf"]


class DOCXFactory(DocumentFactory[DOCXDocument, DOCXParser]):
    """Factory for DOCX documents and parsers."""
    
    def create_document(self, config: DocumentConfig) -> DOCXDocument:
        """Create DOCX document."""
        if config.format != DocumentFormat.DOCX:
            config = dataclass.replace(config, format=DocumentFormat.DOCX)
        return DOCXDocument(config)
    
    def create_parser(self) -> DOCXParser:
        """Create DOCX parser."""
        return DOCXParser()
    
    def get_supported_extensions(self) -> list[str]:
        return [".docx", ".doc"]


class HTMLFactory(DocumentFactory[HTMLDocument, HTMLParser]):
    """Factory for HTML documents and parsers."""
    
    def create_document(self, config: DocumentConfig) -> HTMLDocument:
        """Create HTML document."""
        if config.format != DocumentFormat.HTML:
            config = dataclass.replace(config, format=DocumentFormat.HTML)
        return HTMLDocument(config)
    
    def create_parser(self) -> HTMLParser:
        """Create HTML parser."""
        return HTMLParser()
    
    def get_supported_extensions(self) -> list[str]:
        return [".html", ".htm"]


# Factory registry using decorator
_factory_registry: Dict[DocumentFormat, Type[DocumentFactory]] = {}


def register_factory(format_type: DocumentFormat):
    """Decorator to register factories."""
    def decorator(factory_class: Type[DocumentFactory]):
        _factory_registry[format_type] = factory_class
        return factory_class
    return decorator


# Register factories using decorators
@register_factory(DocumentFormat.PDF)
class RegisteredPDFFactory(PDFFactory):
    pass


@register_factory(DocumentFormat.DOCX)
class RegisteredDOCXFactory(DOCXFactory):
    pass


@register_factory(DocumentFormat.HTML)
class RegisteredHTMLFactory(HTMLFactory):
    pass


class DocumentProcessor:
    """
    Document processor that uses factories with context management.
    """
    
    def __init__(self, format_type: DocumentFormat):
        self.format_type = format_type
        self.factory: Optional[DocumentFactory] = None
        self.document: Optional[Document] = None
        self.parser: Optional[Parser] = None
    
    def __enter__(self):
        """Context manager entry."""
        factory_class = _factory_registry.get(self.format_type)
        if not factory_class:
            raise ValueError(f"No factory registered for {self.format_type}")
        
        self.factory = factory_class()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.factory = None
        self.document = None
        self.parser = None
    
    def create_document(self, config: DocumentConfig) -> Document:
        """Create document using registered factory."""
        if not self.factory:
            raise RuntimeError("Processor not initialized. Use within context manager.")
        
        self.document = self.factory.create_document(config)
        return self.document
    
    def create_parser(self) -> Parser:
        """Create parser using registered factory."""
        if not self.factory:
            raise RuntimeError("Processor not initialized. Use within context manager.")
        
        self.parser = self.factory.create_parser()
        return self.parser
    
    def get_extensions(self) -> list[str]:
        """Get supported extensions."""
        if not self.factory:
            raise RuntimeError("Processor not initialized. Use within context manager.")
        
        return self.factory.get_supported_extensions()


def get_factory_for_format(format_type: DocumentFormat) -> DocumentFactory:
    """Get factory instance for given format."""
    factory_map = {
        DocumentFormat.PDF: PDFFactory(),
        DocumentFormat.DOCX: DOCXFactory(),
        DocumentFormat.HTML: HTMLFactory()
    }
    
    return factory_map.get(format_type, PDFFactory())


def main():
    """
    Demonstrate optimized abstract factory implementation.
    """
    print("=== Optimized Abstract Factory Pattern Demo ===")
    
    # Test different document formats
    formats = [DocumentFormat.PDF, DocumentFormat.DOCX, DocumentFormat.HTML]
    
    for format_type in formats:
        print(f"\n--- {format_type.name} DOCUMENTS ---")
        
        # Create configuration
        config = DocumentConfig(
            title=f"Sample {format_type.name} Document",
            author="Python Developer",
            format=format_type,
            compress=True
        )
        
        # Use context manager for resource management
        with DocumentProcessor(format_type) as processor:
            # Create document and parser
            document = processor.create_document(config)
            parser = processor.create_parser()
            
            # Test document operations
            print(f"Supported extensions: {processor.get_extensions()}")
            print(f"Document metadata: {document.get_metadata()}")
            print(f"Save result: {document.save('test_file')}")
            
            # Test parser operations
            test_content = "This is sample content for testing."
            parsed_data = parser.parse(test_content)
            print(f"Parsed data: {parsed_data}")
            print(f"Validation result: {parser.validate(parsed_data)}")
    
    # Demonstrate protocol usage
    print("\n=== Protocol Usage Demo ===")
    
    def process_document(doc: Document) -> None:
        """Function that works with any document implementing the protocol."""
        print(f"Processing document: {doc.get_metadata()['title']}")
        print(f"Content preview: {doc.get_content()[:50]}...")
    
    # Create different document types
    pdf_config = DocumentConfig("PDF Report", "Analyst", DocumentFormat.PDF)
    html_config = DocumentConfig("Web Page", "Developer", DocumentFormat.HTML)
    
    pdf_factory = PDFFactory()
    html_factory = HTMLFactory()
    
    pdf_doc = pdf_factory.create_document(pdf_config)
    html_doc = html_factory.create_document(html_config)
    
    # Both can be processed by the same function
    process_document(pdf_doc)
    process_document(html_doc)
    
    # Demonstrate generic factory benefits
    print("\n=== Generic Factory Benefits ===")
    
    def create_document_with_parser(factory: DocumentFactory[T, U], config: DocumentConfig) -> tuple[T, U]:
        """Generic function that works with any factory."""
        document = factory.create_document(config)
        parser = factory.create_parser()
        return document, parser
    
    # Type-safe factory usage
    docx_factory = DOCXFactory()
    docx_config = DocumentConfig("Word Document", "Writer", DocumentFormat.DOCX)
    
    doc, parser = create_document_with_parser(docx_factory, docx_config)
    print(f"Created: {type(doc).__name__} and {type(parser).__name__}")
    print(f"Document: {doc.get_metadata()}")
    
    # Demonstrate factory registry
    print("\n=== Factory Registry Demo ===")
    print(f"Registered factories: {list(_factory_registry.keys())}")
    
    for format_type in _factory_registry.keys():
        factory_class = _factory_registry[format_type]
        print(f"{format_type.name}: {factory_class.__name__}")


if __name__ == "__main__":
    main()