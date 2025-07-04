"""
Adapter Design Pattern - Real World Implementation

Real-world example: Payment Gateway Integration
An e-commerce system that needs to integrate multiple payment gateways
with different APIs into a unified payment interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import random


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class PaymentResult:
    """Unified payment result structure."""
    transaction_id: str
    status: PaymentStatus
    amount: float
    currency: str
    message: str
    gateway_reference: Optional[str] = None
    fees: float = 0.0
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "status": self.status.value,
            "amount": self.amount,
            "currency": self.currency,
            "message": self.message,
            "gateway_reference": self.gateway_reference,
            "fees": self.fees,
            "processing_time": self.processing_time
        }


@dataclass
class Customer:
    """Customer information."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }


@dataclass
class PaymentRequest:
    """Unified payment request structure."""
    amount: float
    currency: str
    customer: Customer
    description: str
    order_id: str
    payment_method: str = "card"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PaymentGateway(ABC):
    """
    Unified payment gateway interface that all adapters must implement.
    This is the Target interface in the Adapter pattern.
    """
    
    @abstractmethod
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process a payment request."""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> PaymentResult:
        """Refund a payment."""
        pass
    
    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        """Get payment status."""
        pass
    
    @abstractmethod
    def get_gateway_name(self) -> str:
        """Get gateway name."""
        pass


# Legacy/Third-party payment systems with incompatible interfaces

class StripeAPI:
    """
    Simulated Stripe API - Third-party service with its own interface.
    This is an Adaptee in the Adapter pattern.
    """
    
    def __init__(self):
        self.api_key = "sk_test_stripe_key"
        self.transactions = {}
    
    def create_charge(self, amount_cents: int, currency: str, customer_email: str, 
                     description: str, source: str = "tok_visa") -> Dict[str, Any]:
        """Create a charge using Stripe's API format."""
        charge_id = f"ch_{random.randint(100000, 999999)}"
        
        # Simulate Stripe's response format
        charge = {
            "id": charge_id,
            "object": "charge",
            "amount": amount_cents,
            "currency": currency,
            "description": description,
            "paid": random.choice([True, False]),  # Random success/failure
            "status": "succeeded" if random.choice([True, False]) else "failed",
            "customer": customer_email,
            "source": source,
            "fee": int(amount_cents * 0.029 + 30),  # Stripe's fee structure
            "created": 1609459200  # Unix timestamp
        }
        
        self.transactions[charge_id] = charge
        return charge
    
    def retrieve_charge(self, charge_id: str) -> Dict[str, Any]:
        """Retrieve a charge by ID."""
        return self.transactions.get(charge_id, {})
    
    def create_refund(self, charge_id: str, amount_cents: Optional[int] = None) -> Dict[str, Any]:
        """Create a refund for a charge."""
        charge = self.transactions.get(charge_id)
        if not charge:
            return {"error": "Charge not found"}
        
        refund_id = f"re_{random.randint(100000, 999999)}"
        refund_amount = amount_cents or charge["amount"]
        
        refund = {
            "id": refund_id,
            "object": "refund",
            "amount": refund_amount,
            "charge": charge_id,
            "currency": charge["currency"],
            "status": "succeeded",
            "created": 1609459200
        }
        
        return refund


class PayPalAPI:
    """
    Simulated PayPal API - Another third-party service with different interface.
    This is another Adaptee in the Adapter pattern.
    """
    
    def __init__(self):
        self.client_id = "paypal_client_id"
        self.client_secret = "paypal_client_secret"
        self.payments = {}
    
    def execute_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payment using PayPal's API format."""
        payment_id = f"PAY-{random.randint(100000000, 999999999)}"
        
        # PayPal's response format
        response = {
            "id": payment_id,
            "intent": "sale",
            "state": random.choice(["approved", "failed"]),  # Random success/failure
            "payer": {
                "payment_method": "paypal",
                "payer_info": {
                    "email": payment_data.get("payer_email"),
                    "first_name": payment_data.get("payer_name", "").split()[0],
                    "last_name": payment_data.get("payer_name", "").split()[-1] if " " in payment_data.get("payer_name", "") else ""
                }
            },
            "transactions": [{
                "amount": {
                    "total": str(payment_data.get("amount", 0)),
                    "currency": payment_data.get("currency", "USD")
                },
                "description": payment_data.get("description", ""),
                "item_list": {},
                "related_resources": [{
                    "sale": {
                        "id": f"SALE-{random.randint(100000000, 999999999)}",
                        "state": "completed" if random.choice([True, False]) else "failed",
                        "amount": {
                            "total": str(payment_data.get("amount", 0)),
                            "currency": payment_data.get("currency", "USD")
                        },
                        "transaction_fee": {
                            "value": str(float(payment_data.get("amount", 0)) * 0.035),
                            "currency": payment_data.get("currency", "USD")
                        }
                    }
                }]
            }],
            "create_time": "2021-01-01T00:00:00Z"
        }
        
        self.payments[payment_id] = response
        return response
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details by ID."""
        return self.payments.get(payment_id, {})
    
    def refund_sale(self, sale_id: str, refund_amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a sale."""
        refund_id = f"REFUND-{random.randint(100000000, 999999999)}"
        
        refund = {
            "id": refund_id,
            "state": "completed",
            "amount": {
                "total": str(refund_amount or 0),
                "currency": "USD"
            },
            "sale_id": sale_id,
            "create_time": "2021-01-01T00:00:00Z"
        }
        
        return refund


class SquareAPI:
    """
    Simulated Square API - Another payment service with different interface.
    """
    
    def __init__(self):
        self.application_id = "square_app_id"
        self.access_token = "square_access_token"
        self.payments = {}
    
    def create_payment(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment using Square's API format."""
        payment_id = f"sq_{random.randint(100000000, 999999999)}"
        
        # Square's response format
        payment = {
            "payment": {
                "id": payment_id,
                "status": random.choice(["COMPLETED", "FAILED"]),  # Random success/failure
                "amount_money": request_body.get("amount_money", {}),
                "source_type": "CARD",
                "card_details": {
                    "status": "CAPTURED",
                    "card": {
                        "card_brand": "VISA",
                        "last_4": "1111"
                    },
                    "entry_method": "KEYED"
                },
                "order_id": request_body.get("order_id"),
                "processing_fee": [{
                    "amount_money": {
                        "amount": int(request_body.get("amount_money", {}).get("amount", 0) * 0.026),
                        "currency": request_body.get("amount_money", {}).get("currency", "USD")
                    },
                    "type": "INITIAL"
                }],
                "created_at": "2021-01-01T00:00:00.000Z"
            }
        }
        
        self.payments[payment_id] = payment
        return payment
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Get payment by ID."""
        return self.payments.get(payment_id, {})
    
    def refund_payment(self, payment_id: str, refund_request: Dict[str, Any]) -> Dict[str, Any]:
        """Refund a payment."""
        refund_id = f"refund_{random.randint(100000000, 999999999)}"
        
        refund = {
            "refund": {
                "id": refund_id,
                "status": "COMPLETED",
                "amount_money": refund_request.get("amount_money", {}),
                "payment_id": payment_id,
                "created_at": "2021-01-01T00:00:00.000Z"
            }
        }
        
        return refund


# Adapter implementations

class StripeAdapter(PaymentGateway):
    """
    Adapter that makes Stripe API compatible with our unified payment interface.
    """
    
    def __init__(self, stripe_api: StripeAPI):
        self.stripe_api = stripe_api
    
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process payment using Stripe API."""
        try:
            # Convert our format to Stripe's format
            amount_cents = int(request.amount * 100)  # Stripe uses cents
            
            # Call Stripe API
            charge = self.stripe_api.create_charge(
                amount_cents=amount_cents,
                currency=request.currency,
                customer_email=request.customer.email,
                description=request.description
            )
            
            # Convert Stripe's response to our format
            status = PaymentStatus.SUCCESS if charge.get("paid") else PaymentStatus.FAILED
            
            return PaymentResult(
                transaction_id=charge["id"],
                status=status,
                amount=request.amount,
                currency=request.currency,
                message=f"Stripe charge {charge['status']}",
                gateway_reference=charge["id"],
                fees=charge["fee"] / 100.0,  # Convert cents to dollars
                processing_time=0.5
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                message=f"Stripe error: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> PaymentResult:
        """Refund payment using Stripe API."""
        try:
            amount_cents = int(amount * 100) if amount else None
            refund = self.stripe_api.create_refund(transaction_id, amount_cents)
            
            if "error" in refund:
                status = PaymentStatus.FAILED
                message = refund["error"]
            else:
                status = PaymentStatus.REFUNDED
                message = "Refund successful"
            
            return PaymentResult(
                transaction_id=refund.get("id", ""),
                status=status,
                amount=refund.get("amount", 0) / 100.0,
                currency=refund.get("currency", "USD"),
                message=message,
                gateway_reference=refund.get("id")
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"Stripe refund error: {str(e)}"
            )
    
    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        """Get payment status using Stripe API."""
        try:
            charge = self.stripe_api.retrieve_charge(transaction_id)
            
            if not charge:
                status = PaymentStatus.FAILED
                message = "Charge not found"
            else:
                status = PaymentStatus.SUCCESS if charge.get("paid") else PaymentStatus.FAILED
                message = f"Charge status: {charge.get('status')}"
            
            return PaymentResult(
                transaction_id=transaction_id,
                status=status,
                amount=charge.get("amount", 0) / 100.0,
                currency=charge.get("currency", "USD"),
                message=message,
                gateway_reference=charge.get("id")
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"Stripe status error: {str(e)}"
            )
    
    def get_gateway_name(self) -> str:
        """Get gateway name."""
        return "Stripe"


class PayPalAdapter(PaymentGateway):
    """
    Adapter that makes PayPal API compatible with our unified payment interface.
    """
    
    def __init__(self, paypal_api: PayPalAPI):
        self.paypal_api = paypal_api
    
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process payment using PayPal API."""
        try:
            # Convert our format to PayPal's format
            payment_data = {
                "amount": request.amount,
                "currency": request.currency,
                "payer_email": request.customer.email,
                "payer_name": request.customer.name,
                "description": request.description
            }
            
            # Call PayPal API
            payment = self.paypal_api.execute_payment(payment_data)
            
            # Convert PayPal's response to our format
            status = PaymentStatus.SUCCESS if payment.get("state") == "approved" else PaymentStatus.FAILED
            
            # Extract fee from transaction
            fee = 0.0
            transactions = payment.get("transactions", [])
            if transactions and transactions[0].get("related_resources"):
                sale = transactions[0]["related_resources"][0].get("sale", {})
                fee_info = sale.get("transaction_fee", {})
                fee = float(fee_info.get("value", 0))
            
            return PaymentResult(
                transaction_id=payment["id"],
                status=status,
                amount=request.amount,
                currency=request.currency,
                message=f"PayPal payment {payment['state']}",
                gateway_reference=payment["id"],
                fees=fee,
                processing_time=1.0
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                message=f"PayPal error: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> PaymentResult:
        """Refund payment using PayPal API."""
        try:
            # For demo purposes, extract sale ID from payment
            sale_id = f"SALE-{random.randint(100000000, 999999999)}"
            
            refund = self.paypal_api.refund_sale(sale_id, amount)
            
            status = PaymentStatus.REFUNDED if refund.get("state") == "completed" else PaymentStatus.FAILED
            
            return PaymentResult(
                transaction_id=refund["id"],
                status=status,
                amount=float(refund["amount"]["total"]),
                currency=refund["amount"]["currency"],
                message="PayPal refund completed",
                gateway_reference=refund["id"]
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"PayPal refund error: {str(e)}"
            )
    
    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        """Get payment status using PayPal API."""
        try:
            payment = self.paypal_api.get_payment_details(transaction_id)
            
            if not payment:
                status = PaymentStatus.FAILED
                message = "Payment not found"
                amount = 0
                currency = "USD"
            else:
                status = PaymentStatus.SUCCESS if payment.get("state") == "approved" else PaymentStatus.FAILED
                message = f"PayPal payment {payment.get('state')}"
                
                transactions = payment.get("transactions", [])
                if transactions:
                    amount = float(transactions[0]["amount"]["total"])
                    currency = transactions[0]["amount"]["currency"]
                else:
                    amount = 0
                    currency = "USD"
            
            return PaymentResult(
                transaction_id=transaction_id,
                status=status,
                amount=amount,
                currency=currency,
                message=message,
                gateway_reference=payment.get("id")
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"PayPal status error: {str(e)}"
            )
    
    def get_gateway_name(self) -> str:
        """Get gateway name."""
        return "PayPal"


class SquareAdapter(PaymentGateway):
    """
    Adapter that makes Square API compatible with our unified payment interface.
    """
    
    def __init__(self, square_api: SquareAPI):
        self.square_api = square_api
    
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process payment using Square API."""
        try:
            # Convert our format to Square's format
            request_body = {
                "amount_money": {
                    "amount": int(request.amount * 100),  # Square uses cents
                    "currency": request.currency
                },
                "order_id": request.order_id,
                "source_id": "cnon:card-nonce-ok"  # Simulated card nonce
            }
            
            # Call Square API
            response = self.square_api.create_payment(request_body)
            payment = response.get("payment", {})
            
            # Convert Square's response to our format
            status = PaymentStatus.SUCCESS if payment.get("status") == "COMPLETED" else PaymentStatus.FAILED
            
            # Extract fee
            fee = 0.0
            processing_fees = payment.get("processing_fee", [])
            if processing_fees:
                fee = processing_fees[0]["amount_money"]["amount"] / 100.0
            
            return PaymentResult(
                transaction_id=payment["id"],
                status=status,
                amount=request.amount,
                currency=request.currency,
                message=f"Square payment {payment['status']}",
                gateway_reference=payment["id"],
                fees=fee,
                processing_time=0.8
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                message=f"Square error: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> PaymentResult:
        """Refund payment using Square API."""
        try:
            refund_request = {
                "amount_money": {
                    "amount": int((amount or 0) * 100),
                    "currency": "USD"
                },
                "payment_id": transaction_id
            }
            
            refund_response = self.square_api.refund_payment(transaction_id, refund_request)
            refund = refund_response.get("refund", {})
            
            status = PaymentStatus.REFUNDED if refund.get("status") == "COMPLETED" else PaymentStatus.FAILED
            
            return PaymentResult(
                transaction_id=refund["id"],
                status=status,
                amount=refund["amount_money"]["amount"] / 100.0,
                currency=refund["amount_money"]["currency"],
                message="Square refund completed",
                gateway_reference=refund["id"]
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"Square refund error: {str(e)}"
            )
    
    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        """Get payment status using Square API."""
        try:
            response = self.square_api.get_payment(transaction_id)
            payment = response.get("payment", {})
            
            if not payment:
                status = PaymentStatus.FAILED
                message = "Payment not found"
                amount = 0
                currency = "USD"
            else:
                status = PaymentStatus.SUCCESS if payment.get("status") == "COMPLETED" else PaymentStatus.FAILED
                message = f"Square payment {payment.get('status')}"
                amount = payment.get("amount_money", {}).get("amount", 0) / 100.0
                currency = payment.get("amount_money", {}).get("currency", "USD")
            
            return PaymentResult(
                transaction_id=transaction_id,
                status=status,
                amount=amount,
                currency=currency,
                message=message,
                gateway_reference=payment.get("id")
            )
            
        except Exception as e:
            return PaymentResult(
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                message=f"Square status error: {str(e)}"
            )
    
    def get_gateway_name(self) -> str:
        """Get gateway name."""
        return "Square"


class PaymentProcessor:
    """
    Payment processor that manages multiple payment gateways.
    """
    
    def __init__(self):
        self.gateways: Dict[str, PaymentGateway] = {}
        self.default_gateway: Optional[str] = None
        self.transaction_log: List[Dict[str, Any]] = []
    
    def add_gateway(self, name: str, gateway: PaymentGateway, is_default: bool = False) -> None:
        """Add a payment gateway."""
        self.gateways[name] = gateway
        if is_default or not self.default_gateway:
            self.default_gateway = name
    
    def process_payment(self, request: PaymentRequest, gateway_name: Optional[str] = None) -> PaymentResult:
        """Process payment using specified or default gateway."""
        gateway_name = gateway_name or self.default_gateway
        
        if not gateway_name or gateway_name not in self.gateways:
            return PaymentResult(
                transaction_id="",
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                message="Invalid gateway specified"
            )
        
        gateway = self.gateways[gateway_name]
        result = gateway.process_payment(request)
        
        # Log transaction
        self.transaction_log.append({
            "gateway": gateway_name,
            "request": request.__dict__,
            "result": result.to_dict(),
            "timestamp": "2021-01-01T00:00:00Z"
        })
        
        return result
    
    def get_available_gateways(self) -> List[str]:
        """Get list of available gateway names."""
        return list(self.gateways.keys())
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Get transaction history."""
        return self.transaction_log.copy()


def main():
    """
    Real-world client code demonstrating payment gateway integration.
    """
    print("=== Payment Gateway Adapter Demo ===")
    
    # Create payment processor
    processor = PaymentProcessor()
    
    # Add different payment gateways using adapters
    stripe_api = StripeAPI()
    paypal_api = PayPalAPI()
    square_api = SquareAPI()
    
    processor.add_gateway("stripe", StripeAdapter(stripe_api))
    processor.add_gateway("paypal", PayPalAdapter(paypal_api))
    processor.add_gateway("square", SquareAdapter(square_api), is_default=True)
    
    print(f"Available gateways: {processor.get_available_gateways()}")
    
    # Create sample customers and payment requests
    customer1 = Customer("CUST001", "John Doe", "john.doe@example.com", "+1234567890")
    customer2 = Customer("CUST002", "Jane Smith", "jane.smith@example.com", "+1987654321")
    
    payment_requests = [
        PaymentRequest(99.99, "USD", customer1, "Premium subscription", "ORDER001"),
        PaymentRequest(29.95, "USD", customer2, "Monthly plan", "ORDER002"),
        PaymentRequest(199.00, "USD", customer1, "Annual subscription", "ORDER003")
    ]
    
    # Process payments using different gateways
    print("\n--- Processing Payments ---")
    
    payment_results = []
    gateways = ["stripe", "paypal", "square"]
    
    for i, request in enumerate(payment_requests):
        gateway = gateways[i % len(gateways)]
        print(f"\nProcessing payment {i+1} using {gateway}:")
        print(f"  Customer: {request.customer.name}")
        print(f"  Amount: {request.amount} {request.currency}")
        print(f"  Description: {request.description}")
        
        result = processor.process_payment(request, gateway)
        payment_results.append(result)
        
        print(f"  Result: {result.status.value}")
        print(f"  Transaction ID: {result.transaction_id}")
        print(f"  Message: {result.message}")
        print(f"  Fees: ${result.fees:.2f}")
        print(f"  Processing time: {result.processing_time}s")
    
    # Test refunds
    print("\n--- Testing Refunds ---")
    
    for i, result in enumerate(payment_results):
        if result.status == PaymentStatus.SUCCESS:
            gateway_name = gateways[i % len(gateways)]
            gateway = processor.gateways[gateway_name]
            
            print(f"\nRefunding transaction {result.transaction_id} from {gateway_name}:")
            refund_result = gateway.refund_payment(result.transaction_id, result.amount / 2)
            
            print(f"  Refund status: {refund_result.status.value}")
            print(f"  Refund amount: ${refund_result.amount:.2f}")
            print(f"  Message: {refund_result.message}")
    
    # Test payment status queries
    print("\n--- Checking Payment Status ---")
    
    for i, result in enumerate(payment_results):
        gateway_name = gateways[i % len(gateways)]
        gateway = processor.gateways[gateway_name]
        
        print(f"\nChecking status for {result.transaction_id} from {gateway_name}:")
        status_result = gateway.get_payment_status(result.transaction_id)
        
        print(f"  Status: {status_result.status.value}")
        print(f"  Amount: ${status_result.amount:.2f}")
        print(f"  Message: {status_result.message}")
    
    # Show unified interface benefits
    print("\n--- Unified Interface Benefits ---")
    
    def process_payments_uniformly(requests: List[PaymentRequest], 
                                 gateways: List[PaymentGateway]) -> List[PaymentResult]:
        """Process payments using any gateway with the same interface."""
        results = []
        for i, request in enumerate(requests):
            gateway = gateways[i % len(gateways)]
            result = gateway.process_payment(request)
            results.append(result)
        return results
    
    # All gateways can be used interchangeably
    all_gateways = list(processor.gateways.values())
    test_requests = payment_requests[:2]  # Use first 2 requests
    
    uniform_results = process_payments_uniformly(test_requests, all_gateways)
    
    print("Processed payments using uniform interface:")
    for i, result in enumerate(uniform_results):
        print(f"  Payment {i+1}: {result.status.value} - {result.message}")
    
    # Show transaction history
    print("\n--- Transaction History ---")
    history = processor.get_transaction_history()
    
    for i, transaction in enumerate(history):
        print(f"\nTransaction {i+1}:")
        print(f"  Gateway: {transaction['gateway']}")
        print(f"  Amount: ${transaction['request']['amount']:.2f}")
        print(f"  Status: {transaction['result']['status']}")
        print(f"  Customer: {transaction['request']['customer']['name']}")
    
    # Demonstrate adapter pattern benefits
    print("\n--- Adapter Pattern Benefits ---")
    print("Benefits demonstrated:")
    print("1. Unified interface for different payment gateways")
    print("2. Easy integration of new payment providers")
    print("3. Consistent error handling across all gateways")
    print("4. Simplified client code - no need to know gateway specifics")
    print("5. Gateway switching without code changes")
    print("6. Standardized transaction logging and monitoring")
    
    # Show gateway-specific features accessible through adapters
    print("\n--- Gateway Information ---")
    for name, gateway in processor.gateways.items():
        print(f"{gateway.get_gateway_name()}: Available as '{name}'")


if __name__ == "__main__":
    main()