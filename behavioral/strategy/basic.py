"""
Strategy Design Pattern - Gang of Four Implementation

Intent: Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from clients that use it.

Structure:
- Strategy: declares an interface common to all concrete strategies
- ConcreteStrategy: implements the algorithm using the Strategy interface
- Context: maintains a reference to a Strategy object and delegates work to it
"""

from abc import ABC, abstractmethod
from typing import List, Any


class Strategy(ABC):
    """
    The Strategy interface declares operations common to all supported versions
    of some algorithm.
    
    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """
    
    @abstractmethod
    def do_algorithm(self, data: List[Any]) -> List[Any]:
        pass


class ConcreteStrategyA(Strategy):
    """
    Concrete Strategies implement the algorithm while following the base Strategy
    interface. The interface makes them interchangeable in the Context.
    """
    
    def do_algorithm(self, data: List[Any]) -> List[Any]:
        return sorted(data)


class ConcreteStrategyB(Strategy):
    """
    Concrete Strategies implement the algorithm while following the base Strategy
    interface. The interface makes them interchangeable in the Context.
    """
    
    def do_algorithm(self, data: List[Any]) -> List[Any]:
        return sorted(data, reverse=True)


class Context:
    """
    The Context defines the interface of interest to clients.
    """
    
    def __init__(self, strategy: Strategy):
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._strategy = strategy
    
    @property
    def strategy(self) -> Strategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """
        self._strategy = strategy
    
    def do_some_business_logic(self, data: List[Any]) -> List[Any]:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        print(f"Context: Sorting data using the {type(self._strategy).__name__}")
        result = self._strategy.do_algorithm(data)
        return result


# More practical example: Payment processing
class PaymentStrategy(ABC):
    """
    Abstract strategy for payment processing.
    """
    
    @abstractmethod
    def pay(self, amount: float) -> str:
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        pass


class CreditCardStrategy(PaymentStrategy):
    """
    Concrete strategy for credit card payments.
    """
    
    def __init__(self, card_number: str, cvv: str, expiry_date: str):
        self._card_number = card_number
        self._cvv = cvv
        self._expiry_date = expiry_date
    
    def validate(self) -> bool:
        # Simple validation logic
        return (len(self._card_number) == 16 and 
                len(self._cvv) == 3 and 
                len(self._expiry_date) == 5)
    
    def pay(self, amount: float) -> str:
        if not self.validate():
            return "Credit card validation failed"
        
        masked_card = f"****-****-****-{self._card_number[-4:]}"
        return f"Paid ${amount:.2f} using Credit Card {masked_card}"


class PayPalStrategy(PaymentStrategy):
    """
    Concrete strategy for PayPal payments.
    """
    
    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password
    
    def validate(self) -> bool:
        # Simple validation logic
        return "@" in self._email and len(self._password) >= 6
    
    def pay(self, amount: float) -> str:
        if not self.validate():
            return "PayPal validation failed"
        
        return f"Paid ${amount:.2f} using PayPal account {self._email}"


class BankTransferStrategy(PaymentStrategy):
    """
    Concrete strategy for bank transfer payments.
    """
    
    def __init__(self, account_number: str, routing_number: str):
        self._account_number = account_number
        self._routing_number = routing_number
    
    def validate(self) -> bool:
        # Simple validation logic
        return (len(self._account_number) >= 8 and 
                len(self._routing_number) == 9)
    
    def pay(self, amount: float) -> str:
        if not self.validate():
            return "Bank transfer validation failed"
        
        masked_account = f"****{self._account_number[-4:]}"
        return f"Paid ${amount:.2f} using Bank Transfer from account {masked_account}"


class ShoppingCart:
    """
    Context class that uses payment strategies.
    """
    
    def __init__(self):
        self._items: List[tuple] = []
        self._payment_strategy: PaymentStrategy = None
    
    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """
        Add an item to the shopping cart.
        """
        self._items.append((name, price, quantity))
    
    def remove_item(self, name: str) -> bool:
        """
        Remove an item from the shopping cart.
        """
        for i, (item_name, _, _) in enumerate(self._items):
            if item_name == name:
                del self._items[i]
                return True
        return False
    
    def get_total(self) -> float:
        """
        Calculate the total price of items in the cart.
        """
        return sum(price * quantity for _, price, quantity in self._items)
    
    def set_payment_strategy(self, strategy: PaymentStrategy) -> None:
        """
        Set the payment strategy.
        """
        self._payment_strategy = strategy
    
    def checkout(self) -> str:
        """
        Process the payment using the selected strategy.
        """
        if not self._payment_strategy:
            return "No payment method selected"
        
        if not self._items:
            return "Cart is empty"
        
        total = self.get_total()
        return self._payment_strategy.pay(total)
    
    def get_cart_summary(self) -> str:
        """
        Get a summary of items in the cart.
        """
        if not self._items:
            return "Cart is empty"
        
        summary = ["Shopping Cart:"]
        for name, price, quantity in self._items:
            summary.append(f"  {name}: ${price:.2f} x {quantity} = ${price * quantity:.2f}")
        
        summary.append(f"Total: ${self.get_total():.2f}")
        return "\n".join(summary)


# Compression strategies example
class CompressionStrategy(ABC):
    """
    Abstract strategy for data compression.
    """
    
    @abstractmethod
    def compress(self, data: str) -> str:
        pass
    
    @abstractmethod
    def decompress(self, compressed_data: str) -> str:
        pass


class ZipCompressionStrategy(CompressionStrategy):
    """
    ZIP compression strategy.
    """
    
    def compress(self, data: str) -> str:
        # Simulate ZIP compression
        return f"ZIP_COMPRESSED[{data}]"
    
    def decompress(self, compressed_data: str) -> str:
        # Simulate ZIP decompression
        if compressed_data.startswith("ZIP_COMPRESSED[") and compressed_data.endswith("]"):
            return compressed_data[15:-1]
        return compressed_data


class RarCompressionStrategy(CompressionStrategy):
    """
    RAR compression strategy.
    """
    
    def compress(self, data: str) -> str:
        # Simulate RAR compression
        return f"RAR_COMPRESSED[{data}]"
    
    def decompress(self, compressed_data: str) -> str:
        # Simulate RAR decompression
        if compressed_data.startswith("RAR_COMPRESSED[") and compressed_data.endswith("]"):
            return compressed_data[15:-1]
        return compressed_data


class FileCompressor:
    """
    Context class for file compression.
    """
    
    def __init__(self, strategy: CompressionStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: CompressionStrategy) -> None:
        """
        Change the compression strategy.
        """
        self._strategy = strategy
    
    def compress_file(self, filename: str, data: str) -> str:
        """
        Compress a file using the current strategy.
        """
        compressed = self._strategy.compress(data)
        strategy_name = type(self._strategy).__name__
        return f"File '{filename}' compressed using {strategy_name}: {compressed}"
    
    def decompress_file(self, filename: str, compressed_data: str) -> str:
        """
        Decompress a file using the current strategy.
        """
        decompressed = self._strategy.decompress(compressed_data)
        strategy_name = type(self._strategy).__name__
        return f"File '{filename}' decompressed using {strategy_name}: {decompressed}"


def main():
    """
    The client code demonstrates the Strategy pattern.
    """
    print("=== Strategy Pattern Demo ===")
    
    # Basic strategy pattern
    print("\n1. Basic Sorting Strategies:")
    
    data = ["a", "b", "c", "d", "e"]
    
    context = Context(ConcreteStrategyA())
    print(f"Original data: {data}")
    result1 = context.do_some_business_logic(data.copy())
    print(f"Ascending sort: {result1}")
    
    context.strategy = ConcreteStrategyB()
    result2 = context.do_some_business_logic(data.copy())
    print(f"Descending sort: {result2}")
    
    # Payment strategies
    print("\n2. Payment Processing Strategies:")
    
    cart = ShoppingCart()
    cart.add_item("Laptop", 999.99)
    cart.add_item("Mouse", 29.99, 2)
    cart.add_item("Keyboard", 79.99)
    
    print(cart.get_cart_summary())
    
    # Test different payment methods
    payment_methods = [
        ("Credit Card", CreditCardStrategy("1234567890123456", "123", "12/25")),
        ("PayPal", PayPalStrategy("user@example.com", "securepassword")),
        ("Bank Transfer", BankTransferStrategy("123456789", "987654321"))
    ]
    
    for method_name, strategy in payment_methods:
        print(f"\nTrying {method_name}:")
        cart.set_payment_strategy(strategy)
        result = cart.checkout()
        print(f"Result: {result}")
    
    # Invalid payment method
    print(f"\nTrying invalid credit card:")
    invalid_card = CreditCardStrategy("123", "12", "1/1")
    cart.set_payment_strategy(invalid_card)
    result = cart.checkout()
    print(f"Result: {result}")
    
    # Compression strategies
    print("\n3. File Compression Strategies:")
    
    test_data = "This is some test data that needs to be compressed."
    
    # ZIP compression
    zip_compressor = FileCompressor(ZipCompressionStrategy())
    compressed_zip = zip_compressor.compress_file("test.txt", test_data)
    print(compressed_zip)
    
    decompressed_zip = zip_compressor.decompress_file("test.txt", "ZIP_COMPRESSED[This is some test data that needs to be compressed.]")
    print(decompressed_zip)
    
    # RAR compression
    zip_compressor.set_strategy(RarCompressionStrategy())
    compressed_rar = zip_compressor.compress_file("test.txt", test_data)
    print(compressed_rar)
    
    decompressed_rar = zip_compressor.decompress_file("test.txt", "RAR_COMPRESSED[This is some test data that needs to be compressed.]")
    print(decompressed_rar)
    
    # Strategy selection at runtime
    print("\n4. Runtime Strategy Selection:")
    
    strategies = {
        "zip": ZipCompressionStrategy(),
        "rar": RarCompressionStrategy()
    }
    
    user_choice = "zip"  # Simulate user input
    selected_strategy = strategies.get(user_choice, ZipCompressionStrategy())
    
    runtime_compressor = FileCompressor(selected_strategy)
    result = runtime_compressor.compress_file("runtime.txt", "Runtime data")
    print(f"User selected '{user_choice}': {result}")
    
    # Different data with same strategies
    print("\n5. Same Strategy, Different Data:")
    
    datasets = [
        [1, 5, 3, 9, 2],
        ["zebra", "apple", "banana", "cherry"],
        [3.14, 2.71, 1.41, 1.73]
    ]
    
    sort_context = Context(ConcreteStrategyA())
    
    for i, dataset in enumerate(datasets):
        print(f"Dataset {i+1}: {dataset}")
        sorted_data = sort_context.do_some_business_logic(dataset.copy())
        print(f"Sorted: {sorted_data}")


if __name__ == "__main__":
    main()