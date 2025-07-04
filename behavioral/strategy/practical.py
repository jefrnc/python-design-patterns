"""
Strategy Design Pattern - Real World Implementation

Real-world example: Payment Processing System
A comprehensive payment processing system that supports multiple payment methods
(credit card, PayPal, bank transfer, cryptocurrency) with different processing
strategies, fees, and validation rules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import re
import random


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    BTC = "BTC"
    ETH = "ETH"


class PaymentRequest:
    """Payment request containing all necessary information."""
    
    def __init__(self, amount: float, currency: Currency, merchant_id: str,
                 customer_id: str, order_id: str, description: str = ""):
        self.request_id = f"PAY_{int(datetime.now().timestamp() * 1000)}"
        self.amount = amount
        self.currency = currency
        self.merchant_id = merchant_id
        self.customer_id = customer_id
        self.order_id = order_id
        self.description = description
        self.timestamp = datetime.now()


class PaymentResult:
    """Result of a payment processing attempt."""
    
    def __init__(self, success: bool, transaction_id: Optional[str] = None,
                 status: PaymentStatus = PaymentStatus.PENDING,
                 message: str = "", fee: float = 0.0,
                 processing_time: float = 0.0):
        self.success = success
        self.transaction_id = transaction_id
        self.status = status
        self.message = message
        self.fee = fee
        self.processing_time = processing_time
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "transaction_id": self.transaction_id,
            "status": self.status.value,
            "message": self.message,
            "fee": self.fee,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat()
        }


class PaymentStrategy(ABC):
    """
    Abstract payment strategy interface.
    """
    
    @abstractmethod
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Validate payment-specific data."""
        pass
    
    @abstractmethod
    def calculate_fee(self, amount: float, currency: Currency) -> float:
        """Calculate processing fee for this payment method."""
        pass
    
    @abstractmethod
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any]) -> PaymentResult:
        """Process the payment using this strategy."""
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> List[Currency]:
        """Get list of supported currencies."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this payment strategy."""
        pass
    
    def is_currency_supported(self, currency: Currency) -> bool:
        """Check if currency is supported by this strategy."""
        return currency in self.get_supported_currencies()


class CreditCardStrategy(PaymentStrategy):
    """
    Credit card payment strategy with validation and fraud detection.
    """
    
    def __init__(self):
        self.fee_percentage = 2.9  # 2.9% + $0.30
        self.fixed_fee = 0.30
        self.max_amount = 10000.0  # Maximum transaction amount
        self.fraud_threshold = 5000.0  # Amount that triggers fraud check
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Validate credit card data."""
        required_fields = ["card_number", "expiry_month", "expiry_year", "cvv", "holder_name"]
        
        # Check required fields
        for field in required_fields:
            if field not in payment_data:
                return False
        
        # Validate card number (simplified Luhn algorithm check)
        card_number = payment_data["card_number"].replace(" ", "").replace("-", "")
        if not self._validate_card_number(card_number):
            return False
        
        # Validate expiry date
        try:
            month = int(payment_data["expiry_month"])
            year = int(payment_data["expiry_year"])
            if month < 1 or month > 12:
                return False
            
            expiry_date = datetime(year, month, 1)
            if expiry_date < datetime.now():
                return False
        except (ValueError, TypeError):
            return False
        
        # Validate CVV
        cvv = payment_data["cvv"]
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            return False
        
        return True
    
    def _validate_card_number(self, card_number: str) -> bool:
        """Simplified Luhn algorithm validation."""
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False
        
        # Simplified validation - just check length and digits
        return True
    
    def calculate_fee(self, amount: float, currency: Currency) -> float:
        """Calculate credit card processing fee."""
        percentage_fee = amount * (self.fee_percentage / 100)
        return percentage_fee + self.fixed_fee
    
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any]) -> PaymentResult:
        """Process credit card payment."""
        import time
        start_time = time.time()
        
        # Validate payment data
        if not self.validate_payment_data(payment_data):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Invalid credit card data",
                processing_time=time.time() - start_time
            )
        
        # Check amount limits
        if request.amount > self.max_amount:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"Amount exceeds maximum limit of ${self.max_amount}",
                processing_time=time.time() - start_time
            )
        
        # Fraud detection
        if request.amount > self.fraud_threshold:
            # Simulate fraud check delay
            time.sleep(0.5)
            
            # Random fraud detection (90% success rate for demo)
            if random.random() < 0.1:
                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    message="Transaction flagged by fraud detection",
                    processing_time=time.time() - start_time
                )
        
        # Simulate payment processing
        time.sleep(0.2)
        
        # Calculate fee
        fee = self.calculate_fee(request.amount, request.currency)
        
        # Generate transaction ID
        transaction_id = f"CC_{int(datetime.now().timestamp() * 1000)}"
        
        # Simulate 95% success rate
        if random.random() < 0.95:
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                status=PaymentStatus.COMPLETED,
                message="Credit card payment processed successfully",
                fee=fee,
                processing_time=time.time() - start_time
            )
        else:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Credit card declined",
                processing_time=time.time() - start_time
            )
    
    def get_supported_currencies(self) -> List[Currency]:
        return [Currency.USD, Currency.EUR, Currency.GBP]
    
    def get_strategy_name(self) -> str:
        return "Credit Card"


class PayPalStrategy(PaymentStrategy):
    """
    PayPal payment strategy with OAuth authentication.
    """
    
    def __init__(self):
        self.fee_percentage = 3.4  # 3.4% + $0.30
        self.fixed_fee = 0.30
        self.max_amount = 25000.0
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Validate PayPal payment data."""
        required_fields = ["email", "access_token"]
        
        for field in required_fields:
            if field not in payment_data:
                return False
        
        # Validate email format
        email = payment_data["email"]
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Validate access token (simplified)
        access_token = payment_data["access_token"]
        if len(access_token) < 10:
            return False
        
        return True
    
    def calculate_fee(self, amount: float, currency: Currency) -> float:
        """Calculate PayPal processing fee."""
        percentage_fee = amount * (self.fee_percentage / 100)
        return percentage_fee + self.fixed_fee
    
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any]) -> PaymentResult:
        """Process PayPal payment."""
        import time
        start_time = time.time()
        
        # Validate payment data
        if not self.validate_payment_data(payment_data):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Invalid PayPal credentials",
                processing_time=time.time() - start_time
            )
        
        # Check amount limits
        if request.amount > self.max_amount:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"Amount exceeds PayPal limit of ${self.max_amount}",
                processing_time=time.time() - start_time
            )
        
        # Simulate OAuth verification
        time.sleep(0.3)
        
        # Calculate fee
        fee = self.calculate_fee(request.amount, request.currency)
        
        # Generate transaction ID
        transaction_id = f"PP_{int(datetime.now().timestamp() * 1000)}"
        
        # Simulate 98% success rate for PayPal
        if random.random() < 0.98:
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                status=PaymentStatus.COMPLETED,
                message="PayPal payment processed successfully",
                fee=fee,
                processing_time=time.time() - start_time
            )
        else:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="PayPal payment failed - insufficient funds",
                processing_time=time.time() - start_time
            )
    
    def get_supported_currencies(self) -> List[Currency]:
        return [Currency.USD, Currency.EUR, Currency.GBP]
    
    def get_strategy_name(self) -> str:
        return "PayPal"


class BankTransferStrategy(PaymentStrategy):
    """
    Bank transfer payment strategy with slower processing but lower fees.
    """
    
    def __init__(self):
        self.fee_percentage = 0.5  # 0.5% fee
        self.min_fee = 1.0
        self.max_fee = 25.0
        self.processing_days = 3  # 3 business days
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Validate bank transfer data."""
        required_fields = ["account_number", "routing_number", "account_holder_name", "bank_name"]
        
        for field in required_fields:
            if field not in payment_data:
                return False
        
        # Validate account number
        account_number = payment_data["account_number"]
        if not account_number.isdigit() or len(account_number) < 8:
            return False
        
        # Validate routing number
        routing_number = payment_data["routing_number"]
        if not routing_number.isdigit() or len(routing_number) != 9:
            return False
        
        return True
    
    def calculate_fee(self, amount: float, currency: Currency) -> float:
        """Calculate bank transfer fee."""
        percentage_fee = amount * (self.fee_percentage / 100)
        return max(self.min_fee, min(percentage_fee, self.max_fee))
    
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any]) -> PaymentResult:
        """Process bank transfer payment."""
        import time
        start_time = time.time()
        
        # Validate payment data
        if not self.validate_payment_data(payment_data):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Invalid bank account information",
                processing_time=time.time() - start_time
            )
        
        # Simulate bank verification
        time.sleep(0.5)
        
        # Calculate fee
        fee = self.calculate_fee(request.amount, request.currency)
        
        # Generate transaction ID
        transaction_id = f"BT_{int(datetime.now().timestamp() * 1000)}"
        
        # Bank transfers are typically initiated successfully but take time to complete
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            status=PaymentStatus.PROCESSING,
            message=f"Bank transfer initiated - will complete in {self.processing_days} business days",
            fee=fee,
            processing_time=time.time() - start_time
        )
    
    def get_supported_currencies(self) -> List[Currency]:
        return [Currency.USD, Currency.EUR, Currency.GBP]
    
    def get_strategy_name(self) -> str:
        return "Bank Transfer"


class CryptocurrencyStrategy(PaymentStrategy):
    """
    Cryptocurrency payment strategy supporting Bitcoin and Ethereum.
    """
    
    def __init__(self):
        self.network_fees = {
            Currency.BTC: 0.0001,  # Bitcoin network fee
            Currency.ETH: 0.002    # Ethereum gas fee
        }
        self.confirmation_blocks = {
            Currency.BTC: 6,  # Bitcoin confirmations
            Currency.ETH: 12  # Ethereum confirmations
        }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Validate cryptocurrency payment data."""
        required_fields = ["wallet_address", "private_key_signature"]
        
        for field in required_fields:
            if field not in payment_data:
                return False
        
        # Validate wallet address format (simplified)
        wallet_address = payment_data["wallet_address"]
        if len(wallet_address) < 26 or len(wallet_address) > 42:
            return False
        
        return True
    
    def calculate_fee(self, amount: float, currency: Currency) -> float:
        """Calculate cryptocurrency network fee."""
        if currency in self.network_fees:
            return self.network_fees[currency]
        return 0.001  # Default network fee
    
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any]) -> PaymentResult:
        """Process cryptocurrency payment."""
        import time
        start_time = time.time()
        
        # Validate payment data
        if not self.validate_payment_data(payment_data):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Invalid cryptocurrency wallet data",
                processing_time=time.time() - start_time
            )
        
        # Check if currency is supported
        if not self.is_currency_supported(request.currency):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"Currency {request.currency.value} not supported",
                processing_time=time.time() - start_time
            )
        
        # Simulate blockchain transaction
        time.sleep(1.0)  # Blockchain operations take longer
        
        # Calculate network fee
        fee = self.calculate_fee(request.amount, request.currency)
        
        # Generate transaction hash
        transaction_id = f"CRYPTO_{request.currency.value}_{int(datetime.now().timestamp() * 1000)}"
        
        # Simulate 92% success rate (blockchain can be unpredictable)
        if random.random() < 0.92:
            confirmations_needed = self.confirmation_blocks[request.currency]
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                status=PaymentStatus.PROCESSING,
                message=f"Cryptocurrency transaction broadcast - waiting for {confirmations_needed} confirmations",
                fee=fee,
                processing_time=time.time() - start_time
            )
        else:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Cryptocurrency transaction failed - network congestion",
                processing_time=time.time() - start_time
            )
    
    def get_supported_currencies(self) -> List[Currency]:
        return [Currency.BTC, Currency.ETH]
    
    def get_strategy_name(self) -> str:
        return "Cryptocurrency"


class PaymentProcessor:
    """
    Payment processor that uses different strategies based on payment method.
    """
    
    def __init__(self):
        self.strategies: Dict[str, PaymentStrategy] = {}
        self.transaction_history: List[Dict[str, Any]] = []
        self.default_strategy: Optional[PaymentStrategy] = None
    
    def register_strategy(self, name: str, strategy: PaymentStrategy) -> None:
        """Register a payment strategy."""
        self.strategies[name] = strategy
        print(f"💳 Registered payment strategy: {strategy.get_strategy_name()}")
    
    def set_default_strategy(self, strategy_name: str) -> bool:
        """Set the default payment strategy."""
        if strategy_name in self.strategies:
            self.default_strategy = self.strategies[strategy_name]
            print(f"🎯 Set default payment strategy: {strategy_name}")
            return True
        return False
    
    def get_available_strategies(self, currency: Currency) -> List[str]:
        """Get list of strategies that support the given currency."""
        available = []
        for name, strategy in self.strategies.items():
            if strategy.is_currency_supported(currency):
                available.append(name)
        return available
    
    def process_payment(self, request: PaymentRequest, 
                       payment_data: Dict[str, Any],
                       strategy_name: Optional[str] = None) -> PaymentResult:
        """Process payment using specified or default strategy."""
        
        # Determine which strategy to use
        if strategy_name and strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
        elif self.default_strategy:
            strategy = self.default_strategy
        else:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="No payment strategy available"
            )
        
        # Check currency support
        if not strategy.is_currency_supported(request.currency):
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"Currency {request.currency.value} not supported by {strategy.get_strategy_name()}"
            )
        
        # Process payment
        print(f"💰 Processing payment of {request.amount} {request.currency.value} using {strategy.get_strategy_name()}")
        result = strategy.process_payment(request, payment_data)
        
        # Record transaction
        transaction_record = {
            "request_id": request.request_id,
            "transaction_id": result.transaction_id,
            "strategy": strategy.get_strategy_name(),
            "amount": request.amount,
            "currency": request.currency.value,
            "customer_id": request.customer_id,
            "merchant_id": request.merchant_id,
            "order_id": request.order_id,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        self.transaction_history.append(transaction_record)
        
        return result
    
    def get_strategy_fees(self, amount: float, currency: Currency) -> Dict[str, float]:
        """Get fee comparison across all strategies that support the currency."""
        fees = {}
        for name, strategy in self.strategies.items():
            if strategy.is_currency_supported(currency):
                fee = strategy.calculate_fee(amount, currency)
                fees[strategy.get_strategy_name()] = fee
        return fees
    
    def get_transaction_history(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transaction history, optionally filtered by customer."""
        if customer_id:
            return [tx for tx in self.transaction_history if tx["customer_id"] == customer_id]
        return self.transaction_history.copy()
    
    def get_payment_statistics(self) -> Dict[str, Any]:
        """Get payment processing statistics."""
        if not self.transaction_history:
            return {"total_transactions": 0}
        
        total_transactions = len(self.transaction_history)
        successful_transactions = sum(1 for tx in self.transaction_history 
                                    if tx["result"]["success"])
        
        total_volume = sum(tx["amount"] for tx in self.transaction_history
                          if tx["result"]["success"])
        total_fees = sum(tx["result"]["fee"] for tx in self.transaction_history
                        if tx["result"]["success"])
        
        strategy_counts = {}
        for tx in self.transaction_history:
            strategy = tx["strategy"]
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "success_rate": (successful_transactions / total_transactions) * 100,
            "total_volume": total_volume,
            "total_fees_collected": total_fees,
            "strategy_usage": strategy_counts,
            "average_transaction_amount": total_volume / successful_transactions if successful_transactions > 0 else 0
        }


def main():
    """
    Demonstrate the Payment Processing Strategy system.
    """
    print("=== Payment Processing Strategy System Demo ===")
    
    # Create payment processor
    processor = PaymentProcessor()
    
    # Register payment strategies
    processor.register_strategy("credit_card", CreditCardStrategy())
    processor.register_strategy("paypal", PayPalStrategy())
    processor.register_strategy("bank_transfer", BankTransferStrategy())
    processor.register_strategy("cryptocurrency", CryptocurrencyStrategy())
    
    # Set default strategy
    processor.set_default_strategy("credit_card")
    
    print(f"\n💳 Payment processor initialized with {len(processor.strategies)} strategies")
    
    # Test different payment scenarios
    test_payments = [
        {
            "request": PaymentRequest(100.0, Currency.USD, "MERCH001", "CUST001", "ORDER001", "Product purchase"),
            "payment_data": {
                "card_number": "4532 1234 5678 9012",
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": "123",
                "holder_name": "John Doe"
            },
            "strategy": "credit_card"
        },
        {
            "request": PaymentRequest(250.0, Currency.EUR, "MERCH001", "CUST002", "ORDER002", "Service payment"),
            "payment_data": {
                "email": "jane@example.com",
                "access_token": "pp_access_token_abc123xyz"
            },
            "strategy": "paypal"
        },
        {
            "request": PaymentRequest(1500.0, Currency.USD, "MERCH002", "CUST003", "ORDER003", "Large purchase"),
            "payment_data": {
                "account_number": "123456789",
                "routing_number": "987654321",
                "account_holder_name": "Bob Wilson",
                "bank_name": "First National Bank"
            },
            "strategy": "bank_transfer"
        },
        {
            "request": PaymentRequest(0.05, Currency.BTC, "MERCH003", "CUST004", "ORDER004", "Crypto payment"),
            "payment_data": {
                "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "private_key_signature": "crypto_signature_xyz"
            },
            "strategy": "cryptocurrency"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_payments)} payment scenarios:")
    
    for i, payment_test in enumerate(test_payments, 1):
        print(f"\n--- Test {i}: {payment_test['strategy'].title()} Payment ---")
        
        request = payment_test["request"]
        print(f"Amount: {request.amount} {request.currency.value}")
        print(f"Order: {request.order_id}")
        
        result = processor.process_payment(
            request,
            payment_test["payment_data"],
            payment_test["strategy"]
        )
        
        print(f"Result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        if result.transaction_id:
            print(f"Transaction ID: {result.transaction_id}")
        print(f"Fee: ${result.fee:.4f}")
        print(f"Processing time: {result.processing_time:.3f}s")
    
    # Test fee comparison
    print(f"\n💰 Fee Comparison for $500 USD:")
    fees = processor.get_strategy_fees(500.0, Currency.USD)
    for strategy, fee in fees.items():
        percentage = (fee / 500.0) * 100
        print(f"  {strategy}: ${fee:.2f} ({percentage:.2f}%)")
    
    # Test currency support
    print(f"\n🌍 Currency Support:")
    for currency in Currency:
        available_strategies = processor.get_available_strategies(currency)
        print(f"  {currency.value}: {', '.join(available_strategies) if available_strategies else 'None'}")
    
    # Test invalid scenarios
    print(f"\n🚫 Testing Invalid Scenarios:")
    
    # Invalid credit card
    invalid_request = PaymentRequest(100.0, Currency.USD, "MERCH001", "CUST999", "ORDER999", "Invalid test")
    invalid_data = {
        "card_number": "1234",  # Invalid card number
        "expiry_month": "13",   # Invalid month
        "expiry_year": "2020",  # Expired
        "cvv": "12",           # Invalid CVV
        "holder_name": ""      # Empty name
    }
    
    print("Attempting payment with invalid credit card data:")
    result = processor.process_payment(invalid_request, invalid_data, "credit_card")
    print(f"Result: {result.message}")
    
    # Unsupported currency
    btc_request = PaymentRequest(100.0, Currency.BTC, "MERCH001", "CUST999", "ORDER998", "BTC test")
    credit_card_data = {
        "card_number": "4532 1234 5678 9012",
        "expiry_month": "12",
        "expiry_year": "2025",
        "cvv": "123",
        "holder_name": "John Doe"
    }
    
    print("\nAttempting Bitcoin payment with credit card strategy:")
    result = processor.process_payment(btc_request, credit_card_data, "credit_card")
    print(f"Result: {result.message}")
    
    # Display statistics
    print(f"\n📊 Payment Processing Statistics:")
    stats = processor.get_payment_statistics()
    
    print(f"  Total Transactions: {stats['total_transactions']}")
    print(f"  Successful Transactions: {stats['successful_transactions']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Total Volume: ${stats['total_volume']:.2f}")
    print(f"  Total Fees Collected: ${stats['total_fees_collected']:.4f}")
    print(f"  Average Transaction: ${stats['average_transaction_amount']:.2f}")
    
    print(f"\n📈 Strategy Usage:")
    for strategy, count in stats['strategy_usage'].items():
        percentage = (count / stats['total_transactions']) * 100
        print(f"  {strategy}: {count} transactions ({percentage:.1f}%)")
    
    # Test transaction history
    print(f"\n📜 Recent Transaction History (last 3):")
    recent_transactions = processor.get_transaction_history()[-3:]
    
    for tx in recent_transactions:
        print(f"  Transaction {tx['transaction_id']}:")
        print(f"    Strategy: {tx['strategy']}")
        print(f"    Amount: {tx['amount']} {tx['currency']}")
        print(f"    Status: {tx['result']['status']}")
        print(f"    Customer: {tx['customer_id']}")
    
    # Test strategy switching at runtime
    print(f"\n🔄 Testing Strategy Switching:")
    
    # Create a payment request
    flexible_request = PaymentRequest(75.0, Currency.USD, "MERCH001", "CUST005", "ORDER005", "Flexible payment")
    
    # Try different strategies for the same payment
    strategies_to_try = ["credit_card", "paypal"]
    
    for strategy_name in strategies_to_try:
        print(f"\nTrying with {strategy_name}:")
        
        # Use appropriate payment data for each strategy
        if strategy_name == "credit_card":
            data = {
                "card_number": "4532 1234 5678 9012",
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": "123",
                "holder_name": "Flexible Customer"
            }
        else:  # paypal
            data = {
                "email": "flexible@example.com",
                "access_token": "pp_flexible_token_123"
            }
        
        result = processor.process_payment(flexible_request, data, strategy_name)
        print(f"  Result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"  Fee: ${result.fee:.4f}")
        
        # Only process once successfully
        if result.success:
            break
    
    # Final statistics
    print(f"\n📊 Final Statistics:")
    final_stats = processor.get_payment_statistics()
    print(f"  Total Transactions Processed: {final_stats['total_transactions']}")
    print(f"  Overall Success Rate: {final_stats['success_rate']:.1f}%")
    print(f"  Total Revenue Processed: ${final_stats['total_volume']:.2f}")


if __name__ == "__main__":
    main()