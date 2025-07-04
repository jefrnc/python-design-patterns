"""
Chain of Responsibility Design Pattern - Real World Implementation

Real-world example: Customer Support Ticket System
A customer support system where tickets are escalated through different support levels
based on complexity and priority.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import time


class TicketPriority(Enum):
    """Priority levels for support tickets."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TicketCategory(Enum):
    """Categories for support tickets."""
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"


class SupportTicket:
    """
    Support ticket with customer information and issue details.
    """
    
    def __init__(self, ticket_id: str, customer_name: str, email: str,
                 category: TicketCategory, priority: TicketPriority,
                 subject: str, description: str):
        self.ticket_id = ticket_id
        self.customer_name = customer_name
        self.email = email
        self.category = category
        self.priority = priority
        self.subject = subject
        self.description = description
        self.created_at = datetime.now()
        self.assigned_to: Optional[str] = None
        self.status = "Open"
        self.resolution_time: Optional[float] = None
        self.escalation_history: List[str] = []
    
    def __str__(self) -> str:
        return f"Ticket #{self.ticket_id}: {self.subject} ({self.priority.name} priority)"


class SupportHandler(ABC):
    """
    Abstract base class for support handlers in the chain.
    """
    
    def __init__(self, name: str):
        self._name = name
        self._next_handler: Optional['SupportHandler'] = None
        self._handled_tickets: List[str] = []
        self._max_capacity = 5
    
    @property
    def name(self) -> str:
        return self._name
    
    def set_next(self, handler: 'SupportHandler') -> 'SupportHandler':
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler
    
    def handle_ticket(self, ticket: SupportTicket) -> bool:
        """
        Handle the support ticket or pass it to the next handler.
        """
        if self._can_handle(ticket) and len(self._handled_tickets) < self._max_capacity:
            return self._process_ticket(ticket)
        elif self._next_handler:
            print(f"{self._name}: Cannot handle ticket, escalating to next level")
            ticket.escalation_history.append(f"Escalated from {self._name}")
            return self._next_handler.handle_ticket(ticket)
        else:
            print(f"{self._name}: No handler available for this ticket")
            return False
    
    @abstractmethod
    def _can_handle(self, ticket: SupportTicket) -> bool:
        """Determine if this handler can process the ticket."""
        pass
    
    @abstractmethod
    def _process_ticket(self, ticket: SupportTicket) -> bool:
        """Process the ticket."""
        pass
    
    def get_workload(self) -> int:
        """Get current workload."""
        return len(self._handled_tickets)
    
    def complete_ticket(self, ticket_id: str) -> bool:
        """Mark a ticket as completed."""
        if ticket_id in self._handled_tickets:
            self._handled_tickets.remove(ticket_id)
            print(f"{self._name}: Completed ticket #{ticket_id}")
            return True
        return False


class Level1Support(SupportHandler):
    """
    Level 1 support handles basic inquiries and low priority tickets.
    """
    
    def __init__(self):
        super().__init__("Level 1 Support")
        self._max_capacity = 10
    
    def _can_handle(self, ticket: SupportTicket) -> bool:
        """Level 1 handles low priority and general inquiries."""
        return (ticket.priority in [TicketPriority.LOW, TicketPriority.MEDIUM] and
                ticket.category in [TicketCategory.GENERAL, TicketCategory.BILLING])
    
    def _process_ticket(self, ticket: SupportTicket) -> bool:
        """Process low-complexity tickets."""
        print(f"{self._name}: Processing {ticket}")
        ticket.assigned_to = self._name
        ticket.status = "In Progress"
        self._handled_tickets.append(ticket.ticket_id)
        
        # Simulate processing time
        time.sleep(0.1)
        
        if ticket.category == TicketCategory.GENERAL:
            ticket.status = "Resolved"
            ticket.resolution_time = 0.5  # 30 minutes average
            print(f"{self._name}: Resolved general inquiry for {ticket.customer_name}")
        elif ticket.category == TicketCategory.BILLING:
            ticket.status = "Resolved"
            ticket.resolution_time = 1.0  # 1 hour average
            print(f"{self._name}: Resolved billing issue for {ticket.customer_name}")
        
        return True


class Level2Support(SupportHandler):
    """
    Level 2 support handles technical issues and medium-high priority tickets.
    """
    
    def __init__(self):
        super().__init__("Level 2 Technical Support")
        self._max_capacity = 7
    
    def _can_handle(self, ticket: SupportTicket) -> bool:
        """Level 2 handles technical issues and medium-high priority tickets."""
        return (ticket.priority in [TicketPriority.MEDIUM, TicketPriority.HIGH] and
                ticket.category in [TicketCategory.TECHNICAL, TicketCategory.BUG_REPORT])
    
    def _process_ticket(self, ticket: SupportTicket) -> bool:
        """Process technical tickets."""
        print(f"{self._name}: Processing {ticket}")
        ticket.assigned_to = self._name
        ticket.status = "Under Investigation"
        self._handled_tickets.append(ticket.ticket_id)
        
        # Simulate processing time
        time.sleep(0.15)
        
        if ticket.category == TicketCategory.TECHNICAL:
            ticket.status = "Resolved"
            ticket.resolution_time = 2.0  # 2 hours average
            print(f"{self._name}: Resolved technical issue for {ticket.customer_name}")
        elif ticket.category == TicketCategory.BUG_REPORT:
            ticket.status = "Bug Confirmed"
            ticket.resolution_time = 4.0  # 4 hours average
            print(f"{self._name}: Confirmed and logged bug report from {ticket.customer_name}")
        
        return True


class Level3Support(SupportHandler):
    """
    Level 3 support handles critical issues and complex technical problems.
    """
    
    def __init__(self):
        super().__init__("Level 3 Senior Support")
        self._max_capacity = 3
    
    def _can_handle(self, ticket: SupportTicket) -> bool:
        """Level 3 handles high and critical priority tickets."""
        return ticket.priority in [TicketPriority.HIGH, TicketPriority.CRITICAL]
    
    def _process_ticket(self, ticket: SupportTicket) -> bool:
        """Process complex and critical tickets."""
        print(f"{self._name}: Processing {ticket}")
        ticket.assigned_to = self._name
        ticket.status = "Escalated to Senior Team"
        self._handled_tickets.append(ticket.ticket_id)
        
        # Simulate processing time
        time.sleep(0.2)
        
        if ticket.priority == TicketPriority.CRITICAL:
            ticket.status = "Critical - Priority Response"
            ticket.resolution_time = 0.25  # 15 minutes for critical
            print(f"{self._name}: CRITICAL issue resolved immediately for {ticket.customer_name}")
        else:
            ticket.status = "Resolved by Senior Team"
            ticket.resolution_time = 6.0  # 6 hours average
            print(f"{self._name}: Complex issue resolved for {ticket.customer_name}")
        
        return True


class ManagementEscalation(SupportHandler):
    """
    Final escalation to management for unresolved issues.
    """
    
    def __init__(self):
        super().__init__("Management Escalation")
        self._max_capacity = 2
    
    def _can_handle(self, ticket: SupportTicket) -> bool:
        """Management handles any ticket that reaches this level."""
        return True
    
    def _process_ticket(self, ticket: SupportTicket) -> bool:
        """Management processes any escalated ticket."""
        print(f"{self._name}: MANAGEMENT ESCALATION - Processing {ticket}")
        ticket.assigned_to = "Management Team"
        ticket.status = "Management Review"
        self._handled_tickets.append(ticket.ticket_id)
        
        # Simulate processing time
        time.sleep(0.3)
        
        # Management always finds a resolution
        ticket.status = "Resolved by Management"
        ticket.resolution_time = 24.0  # 24 hours - involves multiple stakeholders
        print(f"{self._name}: Issue escalated to management and resolved for {ticket.customer_name}")
        
        return True


class SupportSystem:
    """
    Customer support system that manages the chain of responsibility.
    """
    
    def __init__(self):
        # Create support chain
        self._level1 = Level1Support()
        self._level2 = Level2Support()
        self._level3 = Level3Support()
        self._management = ManagementEscalation()
        
        # Build the chain
        self._level1.set_next(self._level2).set_next(self._level3).set_next(self._management)
        
        self._ticket_counter = 1000
        self._processed_tickets: List[SupportTicket] = []
    
    def submit_ticket(self, customer_name: str, email: str,
                     category: TicketCategory, priority: TicketPriority,
                     subject: str, description: str) -> SupportTicket:
        """Submit a new support ticket."""
        ticket_id = str(self._ticket_counter)
        self._ticket_counter += 1
        
        ticket = SupportTicket(
            ticket_id=ticket_id,
            customer_name=customer_name,
            email=email,
            category=category,
            priority=priority,
            subject=subject,
            description=description
        )
        
        print(f"\n🎫 New ticket submitted: {ticket}")
        success = self._level1.handle_ticket(ticket)
        
        if success:
            self._processed_tickets.append(ticket)
            print(f"✅ Ticket #{ticket_id} successfully processed")
        else:
            print(f"❌ Ticket #{ticket_id} could not be processed")
        
        return ticket
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "level1_workload": self._level1.get_workload(),
            "level2_workload": self._level2.get_workload(),
            "level3_workload": self._level3.get_workload(),
            "management_workload": self._management.get_workload(),
            "total_processed": len(self._processed_tickets),
            "average_resolution_time": self._calculate_average_resolution_time()
        }
    
    def _calculate_average_resolution_time(self) -> float:
        """Calculate average resolution time for processed tickets."""
        if not self._processed_tickets:
            return 0.0
        
        total_time = sum(
            ticket.resolution_time for ticket in self._processed_tickets
            if ticket.resolution_time is not None
        )
        return total_time / len(self._processed_tickets)
    
    def get_escalation_report(self) -> List[Dict[str, Any]]:
        """Generate escalation report."""
        report = []
        for ticket in self._processed_tickets:
            if ticket.escalation_history:
                report.append({
                    "ticket_id": ticket.ticket_id,
                    "customer": ticket.customer_name,
                    "priority": ticket.priority.name,
                    "escalations": len(ticket.escalation_history),
                    "final_handler": ticket.assigned_to,
                    "resolution_time": ticket.resolution_time
                })
        return report


def main():
    """
    Demonstrate the Customer Support Chain of Responsibility system.
    """
    print("=== Customer Support Chain of Responsibility Demo ===")
    
    # Create support system
    support_system = SupportSystem()
    
    # Test different types of tickets
    test_tickets = [
        {
            "customer": "John Doe",
            "email": "john@example.com",
            "category": TicketCategory.GENERAL,
            "priority": TicketPriority.LOW,
            "subject": "How to reset password",
            "description": "I forgot my password and need help resetting it"
        },
        {
            "customer": "Jane Smith",
            "email": "jane@example.com",
            "category": TicketCategory.BILLING,
            "priority": TicketPriority.MEDIUM,
            "subject": "Billing discrepancy",
            "description": "My bill shows charges I don't recognize"
        },
        {
            "customer": "Bob Johnson",
            "email": "bob@example.com",
            "category": TicketCategory.TECHNICAL,
            "priority": TicketPriority.HIGH,
            "subject": "Application crashes on startup",
            "description": "The app crashes every time I try to launch it"
        },
        {
            "customer": "Alice Wilson",
            "email": "alice@example.com",
            "category": TicketCategory.BUG_REPORT,
            "priority": TicketPriority.HIGH,
            "subject": "Data corruption bug",
            "description": "User data gets corrupted when saving large files"
        },
        {
            "customer": "Critical Corp",
            "email": "emergency@critical.com",
            "category": TicketCategory.TECHNICAL,
            "priority": TicketPriority.CRITICAL,
            "subject": "URGENT: System down",
            "description": "Our entire system is down, affecting thousands of users"
        },
        {
            "customer": "Feature Fan",
            "email": "feature@fan.com",
            "category": TicketCategory.FEATURE_REQUEST,
            "priority": TicketPriority.MEDIUM,
            "subject": "New feature request",
            "description": "Would like to see dark mode support"
        }
    ]
    
    # Submit all tickets
    print("\n📝 Submitting support tickets...")
    tickets = []
    for ticket_data in test_tickets:
        ticket = support_system.submit_ticket(
            customer_name=ticket_data["customer"],
            email=ticket_data["email"],
            category=ticket_data["category"],
            priority=ticket_data["priority"],
            subject=ticket_data["subject"],
            description=ticket_data["description"]
        )
        tickets.append(ticket)
    
    # Display system status
    print("\n📊 System Status:")
    status = support_system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Display escalation report
    print("\n📈 Escalation Report:")
    escalation_report = support_system.get_escalation_report()
    if escalation_report:
        for report in escalation_report:
            print(f"  Ticket #{report['ticket_id']} ({report['customer']}):")
            print(f"    Priority: {report['priority']}")
            print(f"    Escalations: {report['escalations']}")
            print(f"    Final Handler: {report['final_handler']}")
            print(f"    Resolution Time: {report['resolution_time']} hours")
    else:
        print("  No escalations occurred - all tickets handled at first level!")
    
    # Simulate system overload
    print("\n🔥 Simulating System Overload...")
    
    # Create many low-priority tickets to overload Level 1
    for i in range(12):  # Level 1 capacity is 10
        support_system.submit_ticket(
            customer_name=f"Customer {i+1}",
            email=f"customer{i+1}@example.com",
            category=TicketCategory.GENERAL,
            priority=TicketPriority.LOW,
            subject=f"General inquiry #{i+1}",
            description="Simple question about the product"
        )
    
    print("\n📊 System Status After Overload:")
    status = support_system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Demonstrate ticket completion and capacity recovery
    print("\n✅ Completing some tickets to free up capacity...")
    
    # Simulate completing some Level 1 tickets
    level1_handler = support_system._level1
    if level1_handler._handled_tickets:
        for i in range(3):  # Complete 3 tickets
            if level1_handler._handled_tickets:
                ticket_id = level1_handler._handled_tickets[0]
                level1_handler.complete_ticket(ticket_id)
    
    # Now submit another ticket - should be handled by Level 1 again
    print("\n🎫 Submitting new ticket after capacity freed up...")
    support_system.submit_ticket(
        customer_name="New Customer",
        email="new@example.com",
        category=TicketCategory.GENERAL,
        priority=TicketPriority.LOW,
        subject="New inquiry",
        description="Question after capacity was freed up"
    )
    
    print("\n📊 Final System Status:")
    status = support_system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()