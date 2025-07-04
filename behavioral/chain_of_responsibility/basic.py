"""
Chain of Responsibility Design Pattern - Gang of Four Implementation

Intent: Avoid coupling the sender of a request to its receiver by giving more than
one object a chance to handle the request. Chain the receiving objects and pass
the request along the chain until an object handles it.

Structure:
- Handler: defines an interface for handling requests and optionally implements successor link
- ConcreteHandler: handles requests it is responsible for and can access its successor
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """
    
    def __init__(self):
        self._next_handler: Optional[Handler] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        """
        Set the next handler in the chain. Returns the handler to allow chaining.
        """
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request: Any) -> Optional[str]:
        """
        Handle the request or pass it to the next handler.
        """
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class MonkeyHandler(Handler):
    """
    Concrete handler that handles requests for bananas.
    """
    
    def handle(self, request: Any) -> Optional[str]:
        if request == "Banana":
            return f"Monkey: I'll eat the {request}"
        else:
            return super().handle(request)


class SquirrelHandler(Handler):
    """
    Concrete handler that handles requests for nuts.
    """
    
    def handle(self, request: Any) -> Optional[str]:
        if request == "Nut":
            return f"Squirrel: I'll eat the {request}"
        else:
            return super().handle(request)


class DogHandler(Handler):
    """
    Concrete handler that handles requests for meat.
    """
    
    def handle(self, request: Any) -> Optional[str]:
        if request == "MeatBall":
            return f"Dog: I'll eat the {request}"
        else:
            return super().handle(request)


class DefaultHandler(Handler):
    """
    Default handler that handles any unprocessed requests.
    """
    
    def handle(self, request: Any) -> Optional[str]:
        return f"Default: No one wants to handle {request}"


# More complex example with different request types
class Request:
    """
    Request object with type and data.
    """
    def __init__(self, request_type: str, data: Any):
        self.type = request_type
        self.data = data
    
    def __str__(self):
        return f"Request(type={self.type}, data={self.data})"


class AuthenticationHandler(Handler):
    """
    Handler for authentication requests.
    """
    
    def handle(self, request: Request) -> Optional[str]:
        if request.type == "authentication":
            if request.data.get("token") == "valid_token":
                return "AuthenticationHandler: User authenticated successfully"
            else:
                return "AuthenticationHandler: Authentication failed"
        else:
            return super().handle(request)


class AuthorizationHandler(Handler):
    """
    Handler for authorization requests.
    """
    
    def handle(self, request: Request) -> Optional[str]:
        if request.type == "authorization":
            user_role = request.data.get("role", "guest")
            required_role = request.data.get("required_role", "user")
            
            roles_hierarchy = {"admin": 3, "user": 2, "guest": 1}
            
            if roles_hierarchy.get(user_role, 0) >= roles_hierarchy.get(required_role, 0):
                return f"AuthorizationHandler: Access granted for {user_role}"
            else:
                return f"AuthorizationHandler: Access denied - insufficient privileges"
        else:
            return super().handle(request)


class ValidationHandler(Handler):
    """
    Handler for validation requests.
    """
    
    def handle(self, request: Request) -> Optional[str]:
        if request.type == "validation":
            data = request.data.get("data", "")
            if len(data) > 0 and data.isalnum():
                return "ValidationHandler: Data is valid"
            else:
                return "ValidationHandler: Data validation failed"
        else:
            return super().handle(request)


class LoggingHandler(Handler):
    """
    Handler that logs all requests and passes them to the next handler.
    """
    
    def handle(self, request: Request) -> Optional[str]:
        print(f"LoggingHandler: Logging request - {request}")
        # Always pass to next handler (this is a logging middleware)
        return super().handle(request)


def client_code(handler: Handler, requests: list) -> None:
    """
    The client code is usually suited to work with a single handler. In most
    cases, it is not even aware that the handler is part of a chain.
    """
    for request in requests:
        print(f"\nProcessing: {request}")
        result = handler.handle(request)
        if result:
            print(f"  Result: {result}")
        else:
            print(f"  Result: Request was not handled")


def main():
    """
    The client code demonstrates the Chain of Responsibility pattern.
    """
    print("=== Chain of Responsibility Pattern Demo ===")
    
    # Simple chain example
    print("\n1. Simple food chain:")
    monkey = MonkeyHandler()
    squirrel = SquirrelHandler()
    dog = DogHandler()
    default = DefaultHandler()
    
    # Build the chain
    monkey.set_next(squirrel).set_next(dog).set_next(default)
    
    # Test different foods
    foods = ["Nut", "Banana", "MeatBall", "Coffee"]
    client_code(monkey, foods)
    
    # Complex chain example with request objects
    print("\n2. Complex request processing chain:")
    
    # Create handlers
    auth_handler = AuthenticationHandler()
    authz_handler = AuthorizationHandler()
    validation_handler = ValidationHandler()
    logging_handler = LoggingHandler()
    
    # Build chain with logging at the front
    logging_handler.set_next(auth_handler).set_next(authz_handler).set_next(validation_handler)
    
    # Test requests
    requests = [
        Request("authentication", {"token": "valid_token"}),
        Request("authentication", {"token": "invalid_token"}),
        Request("authorization", {"role": "admin", "required_role": "user"}),
        Request("authorization", {"role": "guest", "required_role": "admin"}),
        Request("validation", {"data": "ValidData123"}),
        Request("validation", {"data": "Invalid Data!"}),
        Request("unknown", {"data": "some data"})
    ]
    
    print("\nProcessing complex requests:")
    for request in requests:
        print(f"\nProcessing: {request}")
        result = logging_handler.handle(request)
        if result:
            print(f"  Result: {result}")
        else:
            print(f"  Result: Request was not handled")
    
    # Different chain configurations
    print("\n3. Different chain configurations:")
    
    # Chain 1: Only authentication
    print("\nChain 1 - Authentication only:")
    auth_only_chain = AuthenticationHandler()
    
    auth_request = Request("authentication", {"token": "valid_token"})
    authz_request = Request("authorization", {"role": "admin", "required_role": "user"})
    
    print(f"Auth request: {auth_only_chain.handle(auth_request)}")
    print(f"Authz request: {auth_only_chain.handle(authz_request)}")
    
    # Chain 2: Different order
    print("\nChain 2 - Different order (Validation -> Auth -> Authz):")
    validation_first = ValidationHandler()
    validation_first.set_next(AuthenticationHandler()).set_next(AuthorizationHandler())
    
    mixed_request = Request("authorization", {"role": "user", "required_role": "user"})
    print(f"Mixed request: {validation_first.handle(mixed_request)}")
    
    # Single handler
    print("\n4. Single handler (no chain):")
    single_handler = DogHandler()
    single_foods = ["MeatBall", "Banana"]
    
    for food in single_foods:
        result = single_handler.handle(food)
        print(f"  {food}: {result if result else 'Not handled'}")


if __name__ == "__main__":
    main()