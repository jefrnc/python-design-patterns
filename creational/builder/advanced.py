"""
Builder Design Pattern - Python Optimized Implementation

This implementation leverages Python-specific features:
- Fluent interface with method chaining
- Dataclasses for immutable products
- Context managers for resource management
- Decorators for validation
- Type hints with generics
- Builder protocol for duck typing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, Generic, Optional, Callable, Any, Dict, List
from functools import wraps
import json


# Type variable for generic builder
T = TypeVar('T')


def validate_step(validation_func: Callable[[Any], bool], error_message: str):
    """Decorator to validate builder steps."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not validation_func(self):
                raise ValueError(f"Validation failed: {error_message}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


@dataclass(frozen=True)
class DatabaseConfig:
    """Immutable database configuration."""
    host: str
    port: int
    database: str
    username: str = ""
    password: str = ""
    ssl_enabled: bool = False
    connection_timeout: int = 30
    max_pool_size: int = 10
    additional_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_connection_string(self) -> str:
        """Generate connection string from configuration."""
        base = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        params = []
        
        if self.ssl_enabled:
            params.append("sslmode=require")
        
        params.append(f"connect_timeout={self.connection_timeout}")
        
        for key, value in self.additional_options.items():
            params.append(f"{key}={value}")
        
        if params:
            base += "?" + "&".join(params)
        
        return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "ssl_enabled": self.ssl_enabled,
            "connection_timeout": self.connection_timeout,
            "max_pool_size": self.max_pool_size,
            "additional_options": self.additional_options
        }


class DatabaseConfigBuilder:
    """
    Fluent builder for database configuration with method chaining.
    """
    
    def __init__(self):
        self._host: Optional[str] = None
        self._port: Optional[int] = None
        self._database: Optional[str] = None
        self._username: str = ""
        self._password: str = ""
        self._ssl_enabled: bool = False
        self._connection_timeout: int = 30
        self._max_pool_size: int = 10
        self._additional_options: Dict[str, Any] = {}
    
    def host(self, host: str) -> 'DatabaseConfigBuilder':
        """Set the database host."""
        self._host = host
        return self
    
    def port(self, port: int) -> 'DatabaseConfigBuilder':
        """Set the database port."""
        if port <= 0 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        self._port = port
        return self
    
    def database(self, database: str) -> 'DatabaseConfigBuilder':
        """Set the database name."""
        self._database = database
        return self
    
    def credentials(self, username: str, password: str) -> 'DatabaseConfigBuilder':
        """Set database credentials."""
        self._username = username
        self._password = password
        return self
    
    def enable_ssl(self, enabled: bool = True) -> 'DatabaseConfigBuilder':
        """Enable or disable SSL connection."""
        self._ssl_enabled = enabled
        return self
    
    def timeout(self, seconds: int) -> 'DatabaseConfigBuilder':
        """Set connection timeout."""
        if seconds <= 0:
            raise ValueError("Timeout must be positive")
        self._connection_timeout = seconds
        return self
    
    def pool_size(self, size: int) -> 'DatabaseConfigBuilder':
        """Set maximum pool size."""
        if size <= 0:
            raise ValueError("Pool size must be positive")
        self._max_pool_size = size
        return self
    
    def option(self, key: str, value: Any) -> 'DatabaseConfigBuilder':
        """Add additional option."""
        self._additional_options[key] = value
        return self
    
    def options(self, options: Dict[str, Any]) -> 'DatabaseConfigBuilder':
        """Add multiple options."""
        self._additional_options.update(options)
        return self
    
    @validate_step(
        lambda self: self._host is not None,
        "Host is required"
    )
    @validate_step(
        lambda self: self._port is not None,
        "Port is required"
    )
    @validate_step(
        lambda self: self._database is not None,
        "Database name is required"
    )
    def build(self) -> DatabaseConfig:
        """Build the database configuration."""
        return DatabaseConfig(
            host=self._host,
            port=self._port,
            database=self._database,
            username=self._username,
            password=self._password,
            ssl_enabled=self._ssl_enabled,
            connection_timeout=self._connection_timeout,
            max_pool_size=self._max_pool_size,
            additional_options=self._additional_options.copy()
        )


class BuilderProtocol(Protocol[T]):
    """Protocol for builders using structural typing."""
    
    def build(self) -> T:
        """Build and return the product."""
        ...


@dataclass(frozen=True)
class HttpRequest:
    """Immutable HTTP request configuration."""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    timeout: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True
    
    def to_curl_command(self) -> str:
        """Generate curl command equivalent."""
        cmd = f"curl -X {self.method}"
        
        for key, value in self.headers.items():
            cmd += f' -H "{key}: {value}"'
        
        if self.body:
            cmd += f' -d "{self.body}"'
        
        cmd += f' "{self.url}"'
        
        if self.params:
            separator = "&" if "?" in self.url else "?"
            param_str = "&".join(f"{k}={v}" for k, v in self.params.items())
            cmd = cmd.replace(f'"{self.url}"', f'"{self.url}{separator}{param_str}"')
        
        return cmd


class HttpRequestBuilder:
    """
    Fluent builder for HTTP requests with context manager support.
    """
    
    def __init__(self, url: str):
        self._url = url
        self._method = "GET"
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, str] = {}
        self._body: Optional[str] = None
        self._timeout = 30
        self._follow_redirects = True
        self._verify_ssl = True
    
    def method(self, method: str) -> 'HttpRequestBuilder':
        """Set HTTP method."""
        self._method = method.upper()
        return self
    
    def get(self) -> 'HttpRequestBuilder':
        """Set method to GET."""
        return self.method("GET")
    
    def post(self) -> 'HttpRequestBuilder':
        """Set method to POST."""
        return self.method("POST")
    
    def put(self) -> 'HttpRequestBuilder':
        """Set method to PUT."""
        return self.method("PUT")
    
    def delete(self) -> 'HttpRequestBuilder':
        """Set method to DELETE."""
        return self.method("DELETE")
    
    def header(self, key: str, value: str) -> 'HttpRequestBuilder':
        """Add a header."""
        self._headers[key] = value
        return self
    
    def headers(self, headers: Dict[str, str]) -> 'HttpRequestBuilder':
        """Add multiple headers."""
        self._headers.update(headers)
        return self
    
    def content_type(self, content_type: str) -> 'HttpRequestBuilder':
        """Set Content-Type header."""
        return self.header("Content-Type", content_type)
    
    def json_content(self) -> 'HttpRequestBuilder':
        """Set Content-Type to application/json."""
        return self.content_type("application/json")
    
    def form_content(self) -> 'HttpRequestBuilder':
        """Set Content-Type to application/x-www-form-urlencoded."""
        return self.content_type("application/x-www-form-urlencoded")
    
    def param(self, key: str, value: str) -> 'HttpRequestBuilder':
        """Add a query parameter."""
        self._params[key] = value
        return self
    
    def params(self, params: Dict[str, str]) -> 'HttpRequestBuilder':
        """Add multiple query parameters."""
        self._params.update(params)
        return self
    
    def body(self, body: str) -> 'HttpRequestBuilder':
        """Set request body."""
        self._body = body
        return self
    
    def json_body(self, data: Any) -> 'HttpRequestBuilder':
        """Set JSON body."""
        self._body = json.dumps(data)
        return self.json_content()
    
    def timeout(self, seconds: int) -> 'HttpRequestBuilder':
        """Set request timeout."""
        self._timeout = seconds
        return self
    
    def follow_redirects(self, follow: bool = True) -> 'HttpRequestBuilder':
        """Set redirect following behavior."""
        self._follow_redirects = follow
        return self
    
    def verify_ssl(self, verify: bool = True) -> 'HttpRequestBuilder':
        """Set SSL verification behavior."""
        self._verify_ssl = verify
        return self
    
    def build(self) -> HttpRequest:
        """Build the HTTP request."""
        return HttpRequest(
            url=self._url,
            method=self._method,
            headers=self._headers.copy(),
            params=self._params.copy(),
            body=self._body,
            timeout=self._timeout,
            follow_redirects=self._follow_redirects,
            verify_ssl=self._verify_ssl
        )
    
    def __enter__(self) -> 'HttpRequestBuilder':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        pass


class GenericBuilder(Generic[T]):
    """
    Generic builder base class with type safety.
    """
    
    def __init__(self, product_class: type[T]):
        self._product_class = product_class
        self._attributes: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> 'GenericBuilder[T]':
        """Set an attribute value."""
        self._attributes[key] = value
        return self
    
    def build(self) -> T:
        """Build the product using the collected attributes."""
        return self._product_class(**self._attributes)


@dataclass(frozen=True)
class EmailMessage:
    """Immutable email message."""
    to: List[str]
    subject: str
    body: str
    from_addr: str = "noreply@example.com"
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    html_body: Optional[str] = None
    priority: str = "normal"


class EmailBuilder:
    """
    Email builder with fluent interface and method chaining.
    """
    
    def __init__(self):
        self._to: List[str] = []
        self._subject: str = ""
        self._body: str = ""
        self._from_addr: str = "noreply@example.com"
        self._cc: List[str] = []
        self._bcc: List[str] = []
        self._attachments: List[str] = []
        self._html_body: Optional[str] = None
        self._priority: str = "normal"
    
    def to(self, *recipients: str) -> 'EmailBuilder':
        """Add recipients."""
        self._to.extend(recipients)
        return self
    
    def subject(self, subject: str) -> 'EmailBuilder':
        """Set email subject."""
        self._subject = subject
        return self
    
    def body(self, body: str) -> 'EmailBuilder':
        """Set email body."""
        self._body = body
        return self
    
    def from_addr(self, from_addr: str) -> 'EmailBuilder':
        """Set sender address."""
        self._from_addr = from_addr
        return self
    
    def cc(self, *recipients: str) -> 'EmailBuilder':
        """Add CC recipients."""
        self._cc.extend(recipients)
        return self
    
    def bcc(self, *recipients: str) -> 'EmailBuilder':
        """Add BCC recipients."""
        self._bcc.extend(recipients)
        return self
    
    def attach(self, *filenames: str) -> 'EmailBuilder':
        """Add attachments."""
        self._attachments.extend(filenames)
        return self
    
    def html_body(self, html_body: str) -> 'EmailBuilder':
        """Set HTML body."""
        self._html_body = html_body
        return self
    
    def priority(self, priority: str) -> 'EmailBuilder':
        """Set email priority."""
        if priority not in ["low", "normal", "high"]:
            raise ValueError("Priority must be 'low', 'normal', or 'high'")
        self._priority = priority
        return self
    
    def high_priority(self) -> 'EmailBuilder':
        """Set high priority."""
        return self.priority("high")
    
    def low_priority(self) -> 'EmailBuilder':
        """Set low priority."""
        return self.priority("low")
    
    def build(self) -> EmailMessage:
        """Build the email message."""
        if not self._to:
            raise ValueError("At least one recipient is required")
        if not self._subject:
            raise ValueError("Subject is required")
        if not self._body:
            raise ValueError("Body is required")
        
        return EmailMessage(
            to=self._to.copy(),
            subject=self._subject,
            body=self._body,
            from_addr=self._from_addr,
            cc=self._cc.copy(),
            bcc=self._bcc.copy(),
            attachments=self._attachments.copy(),
            html_body=self._html_body,
            priority=self._priority
        )


def create_database_config() -> DatabaseConfigBuilder:
    """Factory function to create database config builder."""
    return DatabaseConfigBuilder()


def create_http_request(url: str) -> HttpRequestBuilder:
    """Factory function to create HTTP request builder."""
    return HttpRequestBuilder(url)


def create_email() -> EmailBuilder:
    """Factory function to create email builder."""
    return EmailBuilder()


def main():
    """
    Demonstrate optimized builder implementations.
    """
    print("=== Optimized Builder Pattern Demo ===")
    
    # Test database configuration builder
    print("\n1. Database Configuration Builder:")
    db_config = (create_database_config()
                 .host("localhost")
                 .port(5432)
                 .database("myapp")
                 .credentials("user", "password")
                 .enable_ssl()
                 .timeout(60)
                 .pool_size(20)
                 .option("application_name", "MyApp")
                 .build())
    
    print(f"Database config: {db_config}")
    print(f"Connection string: {db_config.to_connection_string()}")
    
    # Test HTTP request builder with context manager
    print("\n2. HTTP Request Builder:")
    with create_http_request("https://api.example.com/users") as builder:
        request = (builder
                  .post()
                  .json_content()
                  .header("Authorization", "Bearer token123")
                  .param("limit", "10")
                  .json_body({"name": "John", "email": "john@example.com"})
                  .timeout(30)
                  .build())
    
    print(f"HTTP request: {request}")
    print(f"Curl command: {request.to_curl_command()}")
    
    # Test email builder
    print("\n3. Email Builder:")
    email = (create_email()
            .to("user1@example.com", "user2@example.com")
            .cc("manager@example.com")
            .subject("Important Update")
            .body("Hello, this is an important update.")
            .html_body("<h1>Important Update</h1><p>Hello, this is an important update.</p>")
            .attach("document.pdf", "image.jpg")
            .high_priority()
            .build())
    
    print(f"Email: {email}")
    
    # Test generic builder
    print("\n4. Generic Builder:")
    generic_builder = GenericBuilder(EmailMessage)
    generic_email = (generic_builder
                    .set("to", ["generic@example.com"])
                    .set("subject", "Generic Email")
                    .set("body", "This email was built with generic builder")
                    .build())
    
    print(f"Generic email: {generic_email}")
    
    # Test builder protocol
    print("\n5. Builder Protocol:")
    
    def process_with_builder(builder: BuilderProtocol[T]) -> T:
        """Function that works with any builder implementing the protocol."""
        return builder.build()
    
    # Different builders can be used with the same function
    db_builder = create_database_config().host("db.example.com").port(3306).database("test")
    http_builder = create_http_request("https://example.com").get()
    email_builder = create_email().to("test@example.com").subject("Test").body("Test body")
    
    try:
        # This will fail validation (missing required fields)
        result = process_with_builder(db_builder)
    except ValueError as e:
        print(f"Validation error: {e}")
    
    # Test successful builds
    complete_db_builder = (create_database_config()
                          .host("db.example.com")
                          .port(3306)
                          .database("testdb")
                          .credentials("testuser", "testpass"))
    
    db_result = process_with_builder(complete_db_builder)
    http_result = process_with_builder(http_builder)
    email_result = process_with_builder(email_builder)
    
    print(f"Protocol results:")
    print(f"  Database: {db_result.host}:{db_result.port}")
    print(f"  HTTP: {http_result.method} {http_result.url}")
    print(f"  Email: {email_result.subject} to {email_result.to}")
    
    # Demonstrate method chaining with complex configurations
    print("\n6. Complex Configuration:")
    complex_request = (create_http_request("https://api.complex.com/v1/data")
                      .post()
                      .json_content()
                      .headers({
                          "Authorization": "Bearer complex_token",
                          "User-Agent": "MyApp/1.0",
                          "Accept": "application/json"
                      })
                      .params({
                          "format": "json",
                          "version": "v1",
                          "limit": "100"
                      })
                      .json_body({
                          "filters": {
                              "status": "active",
                              "type": "premium"
                          },
                          "sort": "created_at",
                          "order": "desc"
                      })
                      .timeout(45)
                      .follow_redirects(False)
                      .build())
    
    print(f"Complex request method: {complex_request.method}")
    print(f"Complex request headers: {len(complex_request.headers)}")
    print(f"Complex request params: {len(complex_request.params)}")
    print(f"Complex request has body: {complex_request.body is not None}")


if __name__ == "__main__":
    main()