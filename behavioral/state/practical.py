"""
State Design Pattern - Real World Implementation

Real-world example: E-commerce Order Processing System
An order processing system that changes behavior based on the current state
of an order (pending, confirmed, shipped, delivered, cancelled, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import time


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentMethod(Enum):
    """Payment method enumeration."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class OrderItem:
    """Individual item in an order."""
    
    def __init__(self, product_id: str, name: str, price: float, quantity: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
    
    @property
    def total_price(self) -> float:
        return self.price * self.quantity
    
    def __str__(self) -> str:
        return f"{self.name} x{self.quantity} @ ${self.price:.2f} each"


class Customer:
    """Customer information."""
    
    def __init__(self, customer_id: str, name: str, email: str, address: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.address = address
        self.phone = phone


class Order:
    """
    Order context that changes behavior based on its state.
    """
    
    def __init__(self, order_id: str, customer: Customer):
        self.order_id = order_id
        self.customer = customer
        self.items: List[OrderItem] = []
        self.order_date = datetime.now()
        self.payment_method: Optional[PaymentMethod] = None
        self.tracking_number: Optional[str] = None
        self.delivery_date: Optional[datetime] = None
        self.status_history: List[Dict[str, Any]] = []
        
        # Initialize with pending state
        self._state: Optional['OrderState'] = None
        self.transition_to(PendingState())
    
    def transition_to(self, state: 'OrderState') -> None:
        """Transition to a new state."""
        old_state = self._state.__class__.__name__ if self._state else "None"
        new_state = state.__class__.__name__
        
        print(f"Order #{self.order_id}: Transitioning from {old_state} to {new_state}")
        
        self._state = state
        self._state.order = self
        
        # Record state change in history
        self.status_history.append({
            "timestamp": datetime.now(),
            "from_state": old_state,
            "to_state": new_state,
            "status": self.get_status()
        })
    
    def add_item(self, item: OrderItem) -> str:
        """Add item to order - delegates to current state."""
        return self._state.add_item(item)
    
    def remove_item(self, product_id: str) -> str:
        """Remove item from order - delegates to current state."""
        return self._state.remove_item(product_id)
    
    def confirm_order(self) -> str:
        """Confirm the order - delegates to current state."""
        return self._state.confirm()
    
    def pay(self, payment_method: PaymentMethod) -> str:
        """Process payment - delegates to current state."""
        return self._state.pay(payment_method)
    
    def ship(self, tracking_number: str) -> str:
        """Ship the order - delegates to current state."""
        return self._state.ship(tracking_number)
    
    def deliver(self) -> str:
        """Mark order as delivered - delegates to current state."""
        return self._state.deliver()
    
    def cancel(self, reason: str) -> str:
        """Cancel the order - delegates to current state."""
        return self._state.cancel(reason)
    
    def return_order(self, reason: str) -> str:
        """Return the order - delegates to current state."""
        return self._state.return_order(reason)
    
    def get_status(self) -> OrderStatus:
        """Get current order status."""
        return self._state.get_status()
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions in current state."""
        return self._state.get_available_actions()
    
    @property
    def total_amount(self) -> float:
        """Calculate total order amount."""
        return sum(item.total_price for item in self.items)
    
    def get_order_summary(self) -> Dict[str, Any]:
        """Get comprehensive order summary."""
        return {
            "order_id": self.order_id,
            "customer": {
                "name": self.customer.name,
                "email": self.customer.email,
                "address": self.customer.address
            },
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total": item.total_price
                }
                for item in self.items
            ],
            "total_amount": self.total_amount,
            "status": self.get_status().value,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "tracking_number": self.tracking_number,
            "order_date": self.order_date.isoformat(),
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "available_actions": self.get_available_actions()
        }


class OrderState(ABC):
    """
    Abstract base class for order states.
    """
    
    def __init__(self):
        self._order: Optional[Order] = None
    
    @property
    def order(self) -> Order:
        return self._order
    
    @order.setter
    def order(self, order: Order) -> None:
        self._order = order
    
    @abstractmethod
    def get_status(self) -> OrderStatus:
        pass
    
    @abstractmethod
    def get_available_actions(self) -> List[str]:
        pass
    
    def add_item(self, item: OrderItem) -> str:
        return f"Cannot add items in {self.__class__.__name__} state"
    
    def remove_item(self, product_id: str) -> str:
        return f"Cannot remove items in {self.__class__.__name__} state"
    
    def confirm(self) -> str:
        return f"Cannot confirm order in {self.__class__.__name__} state"
    
    def pay(self, payment_method: PaymentMethod) -> str:
        return f"Cannot process payment in {self.__class__.__name__} state"
    
    def ship(self, tracking_number: str) -> str:
        return f"Cannot ship order in {self.__class__.__name__} state"
    
    def deliver(self) -> str:
        return f"Cannot deliver order in {self.__class__.__name__} state"
    
    def cancel(self, reason: str) -> str:
        return f"Cannot cancel order in {self.__class__.__name__} state"
    
    def return_order(self, reason: str) -> str:
        return f"Cannot return order in {self.__class__.__name__} state"


class PendingState(OrderState):
    """
    State when order is pending - items can be added/removed.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.PENDING
    
    def get_available_actions(self) -> List[str]:
        return ["add_item", "remove_item", "confirm", "cancel"]
    
    def add_item(self, item: OrderItem) -> str:
        self.order.items.append(item)
        return f"Added {item.name} to order #{self.order.order_id}"
    
    def remove_item(self, product_id: str) -> str:
        for i, item in enumerate(self.order.items):
            if item.product_id == product_id:
                removed_item = self.order.items.pop(i)
                return f"Removed {removed_item.name} from order #{self.order.order_id}"
        return f"Item {product_id} not found in order"
    
    def confirm(self) -> str:
        if not self.order.items:
            return "Cannot confirm empty order"
        
        self.order.transition_to(ConfirmedState())
        return f"Order #{self.order.order_id} confirmed with {len(self.order.items)} items"
    
    def cancel(self, reason: str) -> str:
        self.order.transition_to(CancelledState())
        return f"Order #{self.order.order_id} cancelled: {reason}"


class ConfirmedState(OrderState):
    """
    State when order is confirmed - payment can be processed.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.CONFIRMED
    
    def get_available_actions(self) -> List[str]:
        return ["pay", "cancel"]
    
    def pay(self, payment_method: PaymentMethod) -> str:
        self.order.payment_method = payment_method
        self.order.transition_to(ProcessingState())
        return f"Payment processed for order #{self.order.order_id} using {payment_method.value}"
    
    def cancel(self, reason: str) -> str:
        self.order.transition_to(CancelledState())
        return f"Order #{self.order.order_id} cancelled: {reason}"


class ProcessingState(OrderState):
    """
    State when order is being processed - preparing for shipment.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.PROCESSING
    
    def get_available_actions(self) -> List[str]:
        return ["ship", "cancel"]
    
    def ship(self, tracking_number: str) -> str:
        self.order.tracking_number = tracking_number
        self.order.transition_to(ShippedState())
        return f"Order #{self.order.order_id} shipped with tracking number: {tracking_number}"
    
    def cancel(self, reason: str) -> str:
        # In processing state, cancellation requires refund
        self.order.transition_to(CancelledState())
        return f"Order #{self.order.order_id} cancelled (refund will be processed): {reason}"


class ShippedState(OrderState):
    """
    State when order is shipped - in transit to customer.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.SHIPPED
    
    def get_available_actions(self) -> List[str]:
        return ["deliver"]
    
    def deliver(self) -> str:
        self.order.delivery_date = datetime.now()
        self.order.transition_to(DeliveredState())
        return f"Order #{self.order.order_id} delivered to {self.order.customer.address}"


class DeliveredState(OrderState):
    """
    State when order is delivered - customer can return if needed.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.DELIVERED
    
    def get_available_actions(self) -> List[str]:
        return ["return_order"]
    
    def return_order(self, reason: str) -> str:
        self.order.transition_to(ReturnedState())
        return f"Order #{self.order.order_id} returned: {reason}"


class CancelledState(OrderState):
    """
    State when order is cancelled - no further actions allowed.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.CANCELLED
    
    def get_available_actions(self) -> List[str]:
        return []  # No actions available in cancelled state


class ReturnedState(OrderState):
    """
    State when order is returned - no further actions allowed.
    """
    
    def get_status(self) -> OrderStatus:
        return OrderStatus.RETURNED
    
    def get_available_actions(self) -> List[str]:
        return []  # No actions available in returned state


class OrderManagementSystem:
    """
    Order management system that handles multiple orders.
    """
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.order_counter = 1000
    
    def create_order(self, customer: Customer) -> Order:
        """Create a new order."""
        order_id = f"ORD-{self.order_counter}"
        self.order_counter += 1
        
        order = Order(order_id, customer)
        self.orders[order_id] = order
        
        print(f"📦 Created new order #{order_id} for {customer.name}")
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with specific status."""
        return [order for order in self.orders.values() 
                if order.get_status() == status]
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a specific customer."""
        return [order for order in self.orders.values() 
                if order.customer.customer_id == customer_id]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        status_counts = {}
        total_revenue = 0
        
        for order in self.orders.values():
            status = order.get_status()
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
            
            if status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED, OrderStatus.PROCESSING]:
                total_revenue += order.total_amount
        
        return {
            "total_orders": len(self.orders),
            "status_breakdown": status_counts,
            "total_revenue": total_revenue,
            "average_order_value": total_revenue / len(self.orders) if self.orders else 0
        }


def main():
    """
    Demonstrate the E-commerce Order Processing State Machine.
    """
    print("=== E-commerce Order Processing State Machine Demo ===")
    
    # Create order management system
    oms = OrderManagementSystem()
    
    # Create customers
    customer1 = Customer("CUST001", "John Doe", "john@example.com", 
                        "123 Main St, Anytown, ST 12345", "+1-555-0123")
    customer2 = Customer("CUST002", "Jane Smith", "jane@example.com",
                        "456 Oak Ave, Somewhere, ST 67890", "+1-555-0456")
    
    # Create orders
    order1 = oms.create_order(customer1)
    order2 = oms.create_order(customer2)
    
    print(f"\n📱 System initialized with {len(oms.orders)} orders")
    
    # Test Order 1 - Complete workflow
    print(f"\n🛒 Testing Order 1 - Complete Workflow:")
    print(f"Order #{order1.order_id} current status: {order1.get_status().value}")
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Add items to order
    item1 = OrderItem("PROD001", "Wireless Headphones", 99.99, 1)
    item2 = OrderItem("PROD002", "Phone Case", 19.99, 2)
    item3 = OrderItem("PROD003", "Screen Protector", 9.99, 1)
    
    print(f"\n📦 Adding items to order:")
    print(order1.add_item(item1))
    print(order1.add_item(item2))
    print(order1.add_item(item3))
    
    print(f"\nOrder total: ${order1.total_amount:.2f}")
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Remove an item
    print(f"\n🗑️  Removing an item:")
    print(order1.remove_item("PROD002"))
    print(f"New order total: ${order1.total_amount:.2f}")
    
    # Confirm order
    print(f"\n✅ Confirming order:")
    print(order1.confirm_order())
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Process payment
    print(f"\n💳 Processing payment:")
    print(order1.pay(PaymentMethod.CREDIT_CARD))
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Ship order
    print(f"\n🚚 Shipping order:")
    print(order1.ship("TRK123456789"))
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Deliver order
    print(f"\n📦 Delivering order:")
    print(order1.deliver())
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Test Order 2 - Cancellation workflow
    print(f"\n🛒 Testing Order 2 - Cancellation Workflow:")
    
    # Add items and confirm
    order2.add_item(OrderItem("PROD004", "Laptop", 999.99, 1))
    order2.confirm_order()
    order2.pay(PaymentMethod.PAYPAL)
    
    print(f"Order #{order2.order_id} status: {order2.get_status().value}")
    
    # Cancel during processing
    print(f"\n❌ Cancelling order during processing:")
    print(order2.cancel("Customer changed mind"))
    print(f"Available actions: {order2.get_available_actions()}")
    
    # Test invalid operations
    print(f"\n🚫 Testing Invalid Operations:")
    
    # Try to add item to delivered order
    print("Trying to add item to delivered order:")
    result = order1.add_item(OrderItem("PROD005", "Extra Item", 5.99, 1))
    print(f"  Result: {result}")
    
    # Try to ship cancelled order
    print("Trying to ship cancelled order:")
    result = order2.ship("TRK987654321")
    print(f"  Result: {result}")
    
    # Try to cancel delivered order
    print("Trying to cancel delivered order:")
    result = order1.cancel("Changed mind")
    print(f"  Result: {result}")
    
    # Test return workflow
    print(f"\n🔄 Testing Return Workflow:")
    print("Returning delivered order:")
    result = order1.return_order("Product defective")
    print(f"  Result: {result}")
    print(f"Available actions: {order1.get_available_actions()}")
    
    # Display order summaries
    print(f"\n📋 Order Summaries:")
    
    print(f"\nOrder 1 Summary:")
    summary1 = order1.get_order_summary()
    print(f"  Order ID: {summary1['order_id']}")
    print(f"  Customer: {summary1['customer']['name']}")
    print(f"  Total: ${summary1['total_amount']:.2f}")
    print(f"  Status: {summary1['status']}")
    print(f"  Items: {len(summary1['items'])}")
    
    print(f"\nOrder 2 Summary:")
    summary2 = order2.get_order_summary()
    print(f"  Order ID: {summary2['order_id']}")
    print(f"  Customer: {summary2['customer']['name']}")
    print(f"  Total: ${summary2['total_amount']:.2f}")
    print(f"  Status: {summary2['status']}")
    print(f"  Items: {len(summary2['items'])}")
    
    # Display state history
    print(f"\n📈 Order 1 State History:")
    for i, history_entry in enumerate(order1.status_history):
        timestamp = history_entry['timestamp'].strftime('%H:%M:%S')
        print(f"  {i+1}. {timestamp}: {history_entry['from_state']} → {history_entry['to_state']}")
    
    # Display system statistics
    print(f"\n📊 System Statistics:")
    stats = oms.get_system_statistics()
    print(f"  Total Orders: {stats['total_orders']}")
    print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
    print(f"  Average Order Value: ${stats['average_order_value']:.2f}")
    print("  Status Breakdown:")
    for status, count in stats['status_breakdown'].items():
        print(f"    {status}: {count}")
    
    # Test bulk operations
    print(f"\n📊 Testing Bulk Operations:")
    
    # Create additional orders for testing
    customer3 = Customer("CUST003", "Bob Wilson", "bob@example.com",
                        "789 Pine St, Elsewhere, ST 11111", "+1-555-0789")
    
    # Create multiple orders in different states
    for i in range(3):
        order = oms.create_order(customer3)
        order.add_item(OrderItem(f"PROD{100+i}", f"Product {i+1}", 50.0 + i*10, 1))
        order.confirm_order()
        
        if i == 0:
            order.pay(PaymentMethod.DEBIT_CARD)
            order.ship(f"TRK{1000+i}")
        elif i == 1:
            order.pay(PaymentMethod.BANK_TRANSFER)
    
    # Display orders by status
    print(f"\nOrders by status:")
    for status in OrderStatus:
        orders = oms.get_orders_by_status(status)
        if orders:
            print(f"  {status.value}: {len(orders)} orders")
            for order in orders:
                print(f"    - Order #{order.order_id} (${order.total_amount:.2f})")
    
    # Final system statistics
    print(f"\n📊 Final System Statistics:")
    final_stats = oms.get_system_statistics()
    print(f"  Total Orders: {final_stats['total_orders']}")
    print(f"  Total Revenue: ${final_stats['total_revenue']:.2f}")
    print("  Status Distribution:")
    for status, count in final_stats['status_breakdown'].items():
        percentage = (count / final_stats['total_orders']) * 100
        print(f"    {status}: {count} ({percentage:.1f}%)")


if __name__ == "__main__":
    main()