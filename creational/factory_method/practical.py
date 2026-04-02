"""
Factory Method Design Pattern - Real World Implementation

A real-world example demonstrating the Factory Method pattern through a 
notification system that creates different types of notification handlers
based on the delivery method (email, SMS, push notification, webhook).

This example shows how to:
- Create notification handlers without specifying their exact classes
- Support different notification providers (Gmail, Outlook, Twilio, etc.)
- Handle various notification formats and requirements
- Manage configuration and authentication for different providers
- Provide extensibility for new notification types
- Handle delivery tracking and error management
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import json
import re
import hashlib
import time


class NotificationType(Enum):
    """Types of notifications supported by the system."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"


class DeliveryStatus(Enum):
    """Status of notification delivery."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


class Priority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationConfig:
    """Configuration for notification providers."""
    provider_name: str
    api_key: str
    endpoint: Optional[str] = None
    additional_config: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_attempts: int = 3


@dataclass
class Recipient:
    """Notification recipient information."""
    identifier: str  # email, phone number, user ID, etc.
    name: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"


@dataclass
class NotificationContent:
    """Content of the notification."""
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryResult:
    """Result of notification delivery attempt."""
    success: bool
    status: DeliveryStatus
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    delivery_time: Optional[datetime] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)


# Abstract Product
class NotificationHandler(ABC):
    """
    Abstract notification handler interface.
    This is the Product in the Factory Method pattern.
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.delivery_history: List[DeliveryResult] = []
        self.rate_limit_tracker: Dict[str, List[datetime]] = {}
    
    @abstractmethod
    def send_notification(self, recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send notification to recipient."""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: Recipient) -> bool:
        """Validate recipient information for this notification type."""
        pass
    
    @abstractmethod
    def format_content(self, content: NotificationContent, recipient: Recipient) -> Dict[str, Any]:
        """Format content for this notification type."""
        pass
    
    def is_rate_limited(self) -> bool:
        """Check if we're hitting rate limits."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        recent_requests = [
            timestamp for timestamp in self.rate_limit_tracker.get(self.config.provider_name, [])
            if timestamp > minute_ago
        ]
        
        self.rate_limit_tracker[self.config.provider_name] = recent_requests
        return len(recent_requests) >= self.config.rate_limit
    
    def record_request(self):
        """Record a request for rate limiting."""
        if self.config.provider_name not in self.rate_limit_tracker:
            self.rate_limit_tracker[self.config.provider_name] = []
        
        self.rate_limit_tracker[self.config.provider_name].append(datetime.now())
    
    def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get delivery statistics for this handler."""
        total_deliveries = len(self.delivery_history)
        successful_deliveries = sum(1 for result in self.delivery_history if result.success)
        
        return {
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'success_rate': successful_deliveries / total_deliveries if total_deliveries > 0 else 0,
            'provider': self.config.provider_name,
            'rate_limit': self.config.rate_limit
        }


# Concrete Products
class EmailNotificationHandler(NotificationHandler):
    """Email notification handler supporting multiple providers."""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
        self.smtp_config = config.additional_config.get('smtp', {})
        
    def send_notification(self, recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send email notification."""
        start_time = time.time()
        
        try:
            # Check rate limiting
            if self.is_rate_limited():
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Rate limit exceeded"
                )
            
            # Validate recipient
            if not self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Invalid email address"
                )
            
            # Format content
            formatted_content = self.format_content(content, recipient)
            
            # Simulate email sending based on provider
            if self.config.provider_name.lower() == "gmail":
                result = self._send_via_gmail(recipient, formatted_content, priority)
            elif self.config.provider_name.lower() == "outlook":
                result = self._send_via_outlook(recipient, formatted_content, priority)
            elif self.config.provider_name.lower() == "sendgrid":
                result = self._send_via_sendgrid(recipient, formatted_content, priority)
            else:
                result = self._send_via_smtp(recipient, formatted_content, priority)
            
            # Record request for rate limiting
            self.record_request()
            
            # Set delivery time
            result.delivery_time = datetime.now()
            
            # Store in history
            self.delivery_history.append(result)
            
            logging.info(f"Email sent to {recipient.identifier} via {self.config.provider_name}: {result.success}")
            return result
            
        except Exception as e:
            error_result = DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message=str(e),
                delivery_time=datetime.now()
            )
            self.delivery_history.append(error_result)
            logging.error(f"Failed to send email to {recipient.identifier}: {e}")
            return error_result
    
    def validate_recipient(self, recipient: Recipient) -> bool:
        """Validate email address format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, recipient.identifier) is not None
    
    def format_content(self, content: NotificationContent, recipient: Recipient) -> Dict[str, Any]:
        """Format content for email."""
        # Personalize content
        personalized_subject = content.subject.replace("{name}", recipient.name or "User")
        personalized_body = content.body.replace("{name}", recipient.name or "User")
        
        formatted_content = {
            'to': recipient.identifier,
            'subject': personalized_subject,
            'text_body': personalized_body,
            'html_body': content.html_body,
            'attachments': content.attachments,
            'metadata': content.metadata
        }
        
        # Add recipient preferences
        if recipient.preferences:
            formatted_content['preferences'] = recipient.preferences
        
        return formatted_content
    
    def _send_via_gmail(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Gmail API."""
        # Simulate Gmail-specific logic
        time.sleep(0.1)  # Simulate network delay
        
        message_id = f"gmail_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:8]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'gmail', 'api_version': 'v1'}
        )
    
    def _send_via_outlook(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Outlook/Exchange."""
        time.sleep(0.12)  # Simulate network delay
        
        message_id = f"outlook_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:8]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'outlook', 'tenant_id': 'demo_tenant'}
        )
    
    def _send_via_sendgrid(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via SendGrid."""
        time.sleep(0.08)  # Simulate network delay
        
        message_id = f"sg_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:8]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'sendgrid', 'message_id': message_id}
        )
    
    def _send_via_smtp(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via SMTP."""
        time.sleep(0.15)  # Simulate network delay
        
        message_id = f"smtp_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:8]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'smtp', 'server': self.smtp_config.get('server', 'localhost')}
        )


class SMSNotificationHandler(NotificationHandler):
    """SMS notification handler supporting multiple providers."""
    
    def send_notification(self, recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send SMS notification."""
        try:
            # Check rate limiting
            if self.is_rate_limited():
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Rate limit exceeded"
                )
            
            # Validate recipient
            if not self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Invalid phone number"
                )
            
            # Format content
            formatted_content = self.format_content(content, recipient)
            
            # Simulate SMS sending based on provider
            if self.config.provider_name.lower() == "twilio":
                result = self._send_via_twilio(recipient, formatted_content, priority)
            elif self.config.provider_name.lower() == "nexmo":
                result = self._send_via_nexmo(recipient, formatted_content, priority)
            else:
                result = self._send_via_generic_sms(recipient, formatted_content, priority)
            
            # Record request for rate limiting
            self.record_request()
            
            # Set delivery time
            result.delivery_time = datetime.now()
            
            # Store in history
            self.delivery_history.append(result)
            
            logging.info(f"SMS sent to {recipient.identifier} via {self.config.provider_name}: {result.success}")
            return result
            
        except Exception as e:
            error_result = DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message=str(e),
                delivery_time=datetime.now()
            )
            self.delivery_history.append(error_result)
            logging.error(f"Failed to send SMS to {recipient.identifier}: {e}")
            return error_result
    
    def validate_recipient(self, recipient: Recipient) -> bool:
        """Validate phone number format."""
        # Simple phone number validation
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(phone_pattern, recipient.identifier) is not None
    
    def format_content(self, content: NotificationContent, recipient: Recipient) -> Dict[str, Any]:
        """Format content for SMS."""
        # SMS has character limits, so we need to truncate
        max_length = 160
        sms_body = content.body[:max_length]
        if len(content.body) > max_length:
            sms_body = content.body[:max_length-3] + "..."
        
        # Personalize content
        personalized_body = sms_body.replace("{name}", recipient.name or "User")
        
        return {
            'to': recipient.identifier,
            'message': personalized_body,
            'metadata': content.metadata
        }
    
    def _send_via_twilio(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Twilio."""
        time.sleep(0.2)  # Simulate network delay
        
        message_id = f"twilio_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:10]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'twilio', 'account_sid': 'demo_sid'}
        )
    
    def _send_via_nexmo(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Nexmo."""
        time.sleep(0.18)  # Simulate network delay
        
        message_id = f"nexmo_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:10]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'nexmo', 'api_key': 'demo_key'}
        )
    
    def _send_via_generic_sms(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via generic SMS provider."""
        time.sleep(0.25)  # Simulate network delay
        
        message_id = f"sms_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:10]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'generic_sms'}
        )


class PushNotificationHandler(NotificationHandler):
    """Push notification handler for mobile devices."""
    
    def send_notification(self, recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send push notification."""
        try:
            # Check rate limiting
            if self.is_rate_limited():
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Rate limit exceeded"
                )
            
            # Validate recipient
            if not self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Invalid device token"
                )
            
            # Format content
            formatted_content = self.format_content(content, recipient)
            
            # Simulate push notification sending
            if self.config.provider_name.lower() == "fcm":
                result = self._send_via_fcm(recipient, formatted_content, priority)
            elif self.config.provider_name.lower() == "apns":
                result = self._send_via_apns(recipient, formatted_content, priority)
            else:
                result = self._send_via_generic_push(recipient, formatted_content, priority)
            
            # Record request for rate limiting
            self.record_request()
            
            # Set delivery time
            result.delivery_time = datetime.now()
            
            # Store in history
            self.delivery_history.append(result)
            
            logging.info(f"Push notification sent to {recipient.identifier} via {self.config.provider_name}: {result.success}")
            return result
            
        except Exception as e:
            error_result = DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message=str(e),
                delivery_time=datetime.now()
            )
            self.delivery_history.append(error_result)
            logging.error(f"Failed to send push notification to {recipient.identifier}: {e}")
            return error_result
    
    def validate_recipient(self, recipient: Recipient) -> bool:
        """Validate device token format."""
        # Simple token validation (should be a long string)
        return len(recipient.identifier) >= 32 and recipient.identifier.isalnum()
    
    def format_content(self, content: NotificationContent, recipient: Recipient) -> Dict[str, Any]:
        """Format content for push notification."""
        # Personalize content
        personalized_title = content.subject.replace("{name}", recipient.name or "User")
        personalized_body = content.body.replace("{name}", recipient.name or "User")
        
        return {
            'token': recipient.identifier,
            'notification': {
                'title': personalized_title,
                'body': personalized_body,
                'icon': content.metadata.get('icon', 'default_icon'),
                'click_action': content.metadata.get('click_action')
            },
            'data': content.metadata,
            'priority': content.metadata.get('priority', 'normal')
        }
    
    def _send_via_fcm(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Firebase Cloud Messaging."""
        time.sleep(0.1)  # Simulate network delay
        
        message_id = f"fcm_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:12]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'fcm', 'project_id': 'demo_project'}
        )
    
    def _send_via_apns(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via Apple Push Notification Service."""
        time.sleep(0.12)  # Simulate network delay
        
        message_id = f"apns_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:12]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'apns', 'bundle_id': 'com.demo.app'}
        )
    
    def _send_via_generic_push(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending via generic push service."""
        time.sleep(0.15)  # Simulate network delay
        
        message_id = f"push_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:12]}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SENT,
            message_id=message_id,
            provider_response={'provider': 'generic_push'}
        )


class WebhookNotificationHandler(NotificationHandler):
    """Webhook notification handler for HTTP callbacks."""
    
    def send_notification(self, recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send webhook notification."""
        try:
            # Check rate limiting
            if self.is_rate_limited():
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Rate limit exceeded"
                )
            
            # Validate recipient
            if not self.validate_recipient(recipient):
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message="Invalid webhook URL"
                )
            
            # Format content
            formatted_content = self.format_content(content, recipient)
            
            # Simulate webhook sending
            result = self._send_webhook(recipient, formatted_content, priority)
            
            # Record request for rate limiting
            self.record_request()
            
            # Set delivery time
            result.delivery_time = datetime.now()
            
            # Store in history
            self.delivery_history.append(result)
            
            logging.info(f"Webhook sent to {recipient.identifier}: {result.success}")
            return result
            
        except Exception as e:
            error_result = DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message=str(e),
                delivery_time=datetime.now()
            )
            self.delivery_history.append(error_result)
            logging.error(f"Failed to send webhook to {recipient.identifier}: {e}")
            return error_result
    
    def validate_recipient(self, recipient: Recipient) -> bool:
        """Validate webhook URL format."""
        url_pattern = r'^https?://.+'
        return re.match(url_pattern, recipient.identifier) is not None
    
    def format_content(self, content: NotificationContent, recipient: Recipient) -> Dict[str, Any]:
        """Format content for webhook."""
        return {
            'webhook_url': recipient.identifier,
            'payload': {
                'subject': content.subject,
                'body': content.body,
                'timestamp': datetime.now().isoformat(),
                'priority': 'normal',
                'metadata': content.metadata
            },
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'NotificationSystem/1.0'
            }
        }
    
    def _send_webhook(self, recipient: Recipient, content: Dict[str, Any], priority: Priority) -> DeliveryResult:
        """Simulate sending webhook."""
        time.sleep(0.3)  # Simulate HTTP request delay
        
        # Simulate different response codes
        import random
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            message_id = f"webhook_{hashlib.md5(recipient.identifier.encode()).hexdigest()[:10]}"
            return DeliveryResult(
                success=True,
                status=DeliveryStatus.DELIVERED,
                message_id=message_id,
                provider_response={'status_code': 200, 'response': 'OK'}
            )
        else:
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message="Webhook endpoint returned error",
                provider_response={'status_code': 500, 'response': 'Internal Server Error'}
            )


# Abstract Creator
class NotificationFactory(ABC):
    """
    Abstract factory for creating notification handlers.
    This is the Creator in the Factory Method pattern.
    """
    
    @abstractmethod
    def create_notification_handler(self, config: NotificationConfig) -> NotificationHandler:
        """Factory method to create notification handler."""
        pass
    
    def send_notification(self, config: NotificationConfig, recipient: Recipient, 
                         content: NotificationContent, priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send notification using the appropriate handler."""
        handler = self.create_notification_handler(config)
        return handler.send_notification(recipient, content, priority)


# Concrete Creators
class EmailNotificationFactory(NotificationFactory):
    """Factory for creating email notification handlers."""
    
    def create_notification_handler(self, config: NotificationConfig) -> NotificationHandler:
        """Create email notification handler."""
        return EmailNotificationHandler(config)


class SMSNotificationFactory(NotificationFactory):
    """Factory for creating SMS notification handlers."""
    
    def create_notification_handler(self, config: NotificationConfig) -> NotificationHandler:
        """Create SMS notification handler."""
        return SMSNotificationHandler(config)


class PushNotificationFactory(NotificationFactory):
    """Factory for creating push notification handlers."""
    
    def create_notification_handler(self, config: NotificationConfig) -> NotificationHandler:
        """Create push notification handler."""
        return PushNotificationHandler(config)


class WebhookNotificationFactory(NotificationFactory):
    """Factory for creating webhook notification handlers."""
    
    def create_notification_handler(self, config: NotificationConfig) -> NotificationHandler:
        """Create webhook notification handler."""
        return WebhookNotificationHandler(config)


# Notification Service (Client)
class NotificationService:
    """
    Service that manages multiple notification factories and providers.
    Demonstrates the client's use of the Factory Method pattern.
    """
    
    def __init__(self):
        self.factories: Dict[NotificationType, NotificationFactory] = {
            NotificationType.EMAIL: EmailNotificationFactory(),
            NotificationType.SMS: SMSNotificationFactory(),
            NotificationType.PUSH: PushNotificationFactory(),
            NotificationType.WEBHOOK: WebhookNotificationFactory()
        }
        self.configurations: Dict[str, NotificationConfig] = {}
        self.delivery_history: List[DeliveryResult] = []
    
    def register_provider(self, notification_type: NotificationType, config: NotificationConfig):
        """Register a notification provider configuration."""
        config_key = f"{notification_type.value}_{config.provider_name}"
        self.configurations[config_key] = config
        logging.info(f"Registered {notification_type.value} provider: {config.provider_name}")
    
    def send_notification(self, notification_type: NotificationType, provider_name: str,
                         recipient: Recipient, content: NotificationContent, 
                         priority: Priority = Priority.NORMAL) -> DeliveryResult:
        """Send notification using specified type and provider."""
        try:
            # Get configuration
            config_key = f"{notification_type.value}_{provider_name}"
            if config_key not in self.configurations:
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message=f"Provider {provider_name} not configured for {notification_type.value}"
                )
            
            config = self.configurations[config_key]
            
            # Get factory
            if notification_type not in self.factories:
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED,
                    error_message=f"Unsupported notification type: {notification_type.value}"
                )
            
            factory = self.factories[notification_type]
            
            # Send notification
            result = factory.send_notification(config, recipient, content, priority)
            
            # Store in history
            self.delivery_history.append(result)
            
            return result
            
        except Exception as e:
            error_result = DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )
            self.delivery_history.append(error_result)
            return error_result
    
    def send_multi_channel_notification(self, channels: List[Tuple[NotificationType, str]], 
                                       recipient: Recipient, content: NotificationContent,
                                       priority: Priority = Priority.NORMAL) -> Dict[str, DeliveryResult]:
        """Send notification across multiple channels."""
        results = {}
        
        for notification_type, provider_name in channels:
            channel_key = f"{notification_type.value}_{provider_name}"
            result = self.send_notification(notification_type, provider_name, recipient, content, priority)
            results[channel_key] = result
        
        return results
    
    def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive delivery statistics."""
        total_deliveries = len(self.delivery_history)
        successful_deliveries = sum(1 for result in self.delivery_history if result.success)
        
        # Statistics by status
        status_counts = {}
        for result in self.delivery_history:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Provider performance
        provider_stats = {}
        for result in self.delivery_history:
            provider = result.provider_response.get('provider', 'unknown')
            if provider not in provider_stats:
                provider_stats[provider] = {'total': 0, 'successful': 0}
            
            provider_stats[provider]['total'] += 1
            if result.success:
                provider_stats[provider]['successful'] += 1
        
        # Calculate success rates
        for provider, stats in provider_stats.items():
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'overall_success_rate': successful_deliveries / total_deliveries if total_deliveries > 0 else 0,
            'status_breakdown': status_counts,
            'provider_performance': provider_stats,
            'registered_providers': len(self.configurations),
            'supported_types': [nt.value for nt in self.factories.keys()]
        }
    
    def get_provider_recommendations(self, notification_type: NotificationType) -> List[str]:
        """Get recommended providers for a notification type."""
        # Simple recommendation based on historical performance
        type_configs = [
            config for key, config in self.configurations.items() 
            if key.startswith(notification_type.value)
        ]
        
        if not type_configs:
            return []
        
        # Get performance data
        provider_performance = {}
        for result in self.delivery_history:
            provider = result.provider_response.get('provider', 'unknown')
            if provider not in provider_performance:
                provider_performance[provider] = []
            provider_performance[provider].append(result.success)
        
        # Calculate success rates and sort
        provider_scores = []
        for config in type_configs:
            provider_name = config.provider_name
            if provider_name in provider_performance:
                success_rate = sum(provider_performance[provider_name]) / len(provider_performance[provider_name])
                provider_scores.append((provider_name, success_rate))
            else:
                provider_scores.append((provider_name, 1.0))  # New provider gets benefit of doubt
        
        # Sort by success rate
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [provider for provider, _ in provider_scores]


# Demonstration Function
def demonstrate_factory_method_pattern():
    """Demonstrate the Factory Method pattern with notification system."""
    
    print("=== Notification System - Factory Method Pattern Demo ===\n")
    
    # Create notification service
    notification_service = NotificationService()
    
    print("1. Provider Registration:")
    print("-" * 25)
    
    # Register email providers
    gmail_config = NotificationConfig(
        provider_name="gmail",
        api_key="gmail_api_key_123",
        endpoint="https://gmail.googleapis.com/gmail/v1/",
        additional_config={"oauth_scope": "gmail.send"}
    )
    notification_service.register_provider(NotificationType.EMAIL, gmail_config)
    
    sendgrid_config = NotificationConfig(
        provider_name="sendgrid",
        api_key="sendgrid_api_key_456",
        endpoint="https://api.sendgrid.com/v3/",
        rate_limit=300
    )
    notification_service.register_provider(NotificationType.EMAIL, sendgrid_config)
    
    # Register SMS providers
    twilio_config = NotificationConfig(
        provider_name="twilio",
        api_key="twilio_api_key_789",
        endpoint="https://api.twilio.com/2010-04-01/",
        additional_config={"account_sid": "AC123456789"}
    )
    notification_service.register_provider(NotificationType.SMS, twilio_config)
    
    # Register push notification providers
    fcm_config = NotificationConfig(
        provider_name="fcm",
        api_key="fcm_server_key_abc",
        endpoint="https://fcm.googleapis.com/fcm/send"
    )
    notification_service.register_provider(NotificationType.PUSH, fcm_config)
    
    # Register webhook provider
    webhook_config = NotificationConfig(
        provider_name="generic_webhook",
        api_key="webhook_secret_def",
        timeout=15
    )
    notification_service.register_provider(NotificationType.WEBHOOK, webhook_config)
    
    print("✓ Registered providers for all notification types")
    print(f"Total providers: {len(notification_service.configurations)}")
    print()
    
    # Create recipients
    print("2. Recipient Setup:")
    print("-" * 20)
    
    email_recipient = Recipient(
        identifier="user@example.com",
        name="John Doe",
        preferences={"format": "html", "frequency": "immediate"}
    )
    
    sms_recipient = Recipient(
        identifier="+1234567890",
        name="Jane Smith",
        preferences={"format": "short"}
    )
    
    push_recipient = Recipient(
        identifier="fcm_device_token_1234567890abcdef",
        name="Mobile User",
        preferences={"sound": "default", "vibrate": True}
    )
    
    webhook_recipient = Recipient(
        identifier="https://api.example.com/webhooks/notifications",
        name="System Integration"
    )
    
    print("✓ Created recipients for different notification types")
    print()
    
    # Create notification content
    print("3. Notification Content:")
    print("-" * 25)
    
    welcome_content = NotificationContent(
        subject="Welcome to Our Service!",
        body="Hello {name}, welcome to our amazing service. We're excited to have you on board!",
        html_body="<h1>Welcome {name}!</h1><p>We're excited to have you on board!</p>",
        metadata={"campaign": "welcome", "user_segment": "new_users"}
    )
    
    alert_content = NotificationContent(
        subject="Important Alert",
        body="Hi {name}, this is an important system alert that requires your attention.",
        metadata={"alert_type": "system", "severity": "high"}
    )
    
    print("✓ Created notification content templates")
    print()
    
    # Demonstrate different notification types
    print("4. Sending Notifications via Different Providers:")
    print("-" * 50)
    
    # Email notifications
    print("Email Notifications:")
    gmail_result = notification_service.send_notification(
        NotificationType.EMAIL, "gmail", email_recipient, welcome_content, Priority.NORMAL
    )
    print(f"  Gmail: {'✓' if gmail_result.success else '✗'} - {gmail_result.message_id or gmail_result.error_message}")
    
    sendgrid_result = notification_service.send_notification(
        NotificationType.EMAIL, "sendgrid", email_recipient, alert_content, Priority.HIGH
    )
    print(f"  SendGrid: {'✓' if sendgrid_result.success else '✗'} - {sendgrid_result.message_id or sendgrid_result.error_message}")
    
    # SMS notifications
    print("\nSMS Notifications:")
    sms_result = notification_service.send_notification(
        NotificationType.SMS, "twilio", sms_recipient, alert_content, Priority.URGENT
    )
    print(f"  Twilio: {'✓' if sms_result.success else '✗'} - {sms_result.message_id or sms_result.error_message}")
    
    # Push notifications
    print("\nPush Notifications:")
    push_result = notification_service.send_notification(
        NotificationType.PUSH, "fcm", push_recipient, welcome_content, Priority.NORMAL
    )
    print(f"  FCM: {'✓' if push_result.success else '✗'} - {push_result.message_id or push_result.error_message}")
    
    # Webhook notifications
    print("\nWebhook Notifications:")
    webhook_result = notification_service.send_notification(
        NotificationType.WEBHOOK, "generic_webhook", webhook_recipient, alert_content, Priority.HIGH
    )
    print(f"  Webhook: {'✓' if webhook_result.success else '✗'} - {webhook_result.message_id or webhook_result.error_message}")
    print()
    
    # Multi-channel notification
    print("5. Multi-Channel Notification:")
    print("-" * 30)
    
    multi_channel_recipient = Recipient(
        identifier="multi@example.com",
        name="Multi Channel User"
    )
    
    channels = [
        (NotificationType.EMAIL, "gmail"),
        (NotificationType.PUSH, "fcm")
    ]
    
    multi_results = notification_service.send_multi_channel_notification(
        channels, multi_channel_recipient, alert_content, Priority.HIGH
    )
    
    print("Multi-channel delivery results:")
    for channel, result in multi_results.items():
        print(f"  {channel}: {'✓' if result.success else '✗'}")
    print()
    
    # Provider recommendations
    print("6. Provider Recommendations:")
    print("-" * 30)
    
    email_recommendations = notification_service.get_provider_recommendations(NotificationType.EMAIL)
    print(f"Recommended Email providers: {email_recommendations}")
    
    sms_recommendations = notification_service.get_provider_recommendations(NotificationType.SMS)
    print(f"Recommended SMS providers: {sms_recommendations}")
    print()
    
    # Statistics
    print("7. Delivery Statistics:")
    print("-" * 25)
    
    stats = notification_service.get_delivery_statistics()
    print(f"Total deliveries: {stats['total_deliveries']}")
    print(f"Successful deliveries: {stats['successful_deliveries']}")
    print(f"Overall success rate: {stats['overall_success_rate']:.1%}")
    print(f"Supported notification types: {stats['supported_types']}")
    
    print("\nProvider Performance:")
    for provider, perf in stats['provider_performance'].items():
        print(f"  {provider}: {perf['successful']}/{perf['total']} ({perf['success_rate']:.1%})")
    
    print("\nStatus Breakdown:")
    for status, count in stats['status_breakdown'].items():
        print(f"  {status}: {count}")
    print()
    
    print("=== Factory Method Pattern Benefits Demonstrated ===")
    print("✓ Easy addition of new notification types and providers")
    print("✓ Polymorphic creation of notification handlers")
    print("✓ Provider-specific configuration and behavior")
    print("✓ Consistent interface across different notification methods")
    print("✓ Flexible multi-provider support")
    print("✓ Extensible architecture for future notification channels")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the demonstration
    demonstrate_factory_method_pattern()