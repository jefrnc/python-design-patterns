"""
Observer Design Pattern - Real World Implementation

Real-world example: Stock Market Trading System
A comprehensive stock trading system where investors can subscribe to stock price
updates, news alerts, and trading signals from multiple sources.
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import random
import time


class AlertType(Enum):
    """Types of alerts in the trading system."""
    PRICE_CHANGE = "price_change"
    VOLUME_SPIKE = "volume_spike"
    NEWS_ALERT = "news_alert"
    TECHNICAL_SIGNAL = "technical_signal"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"


class StockData:
    """Stock market data container."""
    
    def __init__(self, symbol: str, price: float, volume: int, 
                 change_percent: float, timestamp: datetime = None):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.change_percent = change_percent
        self.timestamp = timestamp or datetime.now()
        self.previous_price: Optional[float] = None
        self.day_high: float = price
        self.day_low: float = price
    
    def update_price(self, new_price: float, new_volume: int) -> None:
        """Update stock price and calculate change."""
        self.previous_price = self.price
        self.price = new_price
        self.volume = new_volume
        self.timestamp = datetime.now()
        
        if self.previous_price:
            self.change_percent = ((new_price - self.previous_price) / self.previous_price) * 100
        
        # Update daily high/low
        if new_price > self.day_high:
            self.day_high = new_price
        if new_price < self.day_low:
            self.day_low = new_price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "change_percent": self.change_percent,
            "day_high": self.day_high,
            "day_low": self.day_low,
            "timestamp": self.timestamp.isoformat()
        }


class NewsItem:
    """News item for stock alerts."""
    
    def __init__(self, title: str, content: str, symbols: List[str],
                 sentiment: str = "neutral", urgency: str = "medium"):
        self.title = title
        self.content = content
        self.symbols = symbols
        self.sentiment = sentiment  # positive, negative, neutral
        self.urgency = urgency      # low, medium, high, critical
        self.timestamp = datetime.now()


class TechnicalSignal:
    """Technical analysis signal."""
    
    def __init__(self, symbol: str, signal_type: str, strength: float,
                 description: str, target_price: Optional[float] = None):
        self.symbol = symbol
        self.signal_type = signal_type  # buy, sell, hold
        self.strength = strength        # 0.0 to 1.0
        self.description = description
        self.target_price = target_price
        self.timestamp = datetime.now()


class Observer(ABC):
    """
    Abstract observer interface for market participants.
    """
    
    @abstractmethod
    def update(self, alert_type: AlertType, data: Any) -> None:
        """Receive updates from observed subjects."""
        pass
    
    @abstractmethod
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        pass


class Subject(ABC):
    """
    Abstract subject interface for market data sources.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._observer_preferences: Dict[str, Set[AlertType]] = {}
    
    def attach(self, observer: Observer, alert_types: Optional[List[AlertType]] = None) -> None:
        """Attach observer with optional alert type preferences."""
        if observer not in self._observers:
            self._observers.append(observer)
            
            # Set alert preferences (default to all types if none specified)
            observer_id = observer.get_observer_id()
            if alert_types:
                self._observer_preferences[observer_id] = set(alert_types)
            else:
                self._observer_preferences[observer_id] = set(AlertType)
            
            print(f"📊 Observer {observer_id} subscribed to {len(self._observer_preferences[observer_id])} alert types")
    
    def detach(self, observer: Observer) -> None:
        """Detach observer from notifications."""
        if observer in self._observers:
            self._observers.remove(observer)
            observer_id = observer.get_observer_id()
            if observer_id in self._observer_preferences:
                del self._observer_preferences[observer_id]
            print(f"📊 Observer {observer_id} unsubscribed")
    
    def notify(self, alert_type: AlertType, data: Any) -> None:
        """Notify all interested observers."""
        notification_count = 0
        
        for observer in self._observers:
            observer_id = observer.get_observer_id()
            if (observer_id in self._observer_preferences and 
                alert_type in self._observer_preferences[observer_id]):
                observer.update(alert_type, data)
                notification_count += 1
        
        print(f"📢 Notified {notification_count} observers about {alert_type.value}")


class StockPriceMonitor(Subject):
    """
    Stock price monitoring system that notifies observers of price changes.
    """
    
    def __init__(self):
        super().__init__()
        self._stocks: Dict[str, StockData] = {}
        self._price_thresholds: Dict[str, Dict[str, float]] = {}  # symbol -> {high, low}
    
    def add_stock(self, symbol: str, initial_price: float, initial_volume: int = 1000) -> None:
        """Add a stock to monitor."""
        self._stocks[symbol] = StockData(symbol, initial_price, initial_volume, 0.0)
        self._price_thresholds[symbol] = {"high": initial_price * 1.05, "low": initial_price * 0.95}
        print(f"📈 Added stock {symbol} at ${initial_price:.2f}")
    
    def update_stock_price(self, symbol: str, new_price: float, new_volume: int) -> None:
        """Update stock price and notify observers if significant change."""
        if symbol not in self._stocks:
            return
        
        stock = self._stocks[symbol]
        old_price = stock.price
        stock.update_price(new_price, new_volume)
        
        # Check for significant price changes (>2% change)
        if abs(stock.change_percent) >= 2.0:
            self.notify(AlertType.PRICE_CHANGE, stock)
        
        # Check for volume spikes (>50% above average)
        if new_volume > 1500:  # Simplified volume spike detection
            self.notify(AlertType.VOLUME_SPIKE, stock)
        
        # Check threshold alerts
        self._check_price_thresholds(symbol, new_price)
    
    def _check_price_thresholds(self, symbol: str, price: float) -> None:
        """Check if price has crossed threshold alerts."""
        thresholds = self._price_thresholds[symbol]
        
        if price >= thresholds["high"]:
            alert_data = {
                "symbol": symbol,
                "price": price,
                "threshold_type": "high",
                "threshold_value": thresholds["high"]
            }
            self.notify(AlertType.PRICE_CHANGE, alert_data)
            # Update threshold
            thresholds["high"] = price * 1.05
        
        elif price <= thresholds["low"]:
            alert_data = {
                "symbol": symbol,
                "price": price,
                "threshold_type": "low",
                "threshold_value": thresholds["low"]
            }
            self.notify(AlertType.PRICE_CHANGE, alert_data)
            # Update threshold
            thresholds["low"] = price * 0.95
    
    def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """Get current stock data."""
        return self._stocks.get(symbol)
    
    def get_all_stocks(self) -> Dict[str, StockData]:
        """Get all monitored stocks."""
        return self._stocks.copy()


class NewsService(Subject):
    """
    News service that provides market news and alerts.
    """
    
    def __init__(self):
        super().__init__()
        self._news_history: List[NewsItem] = []
    
    def publish_news(self, title: str, content: str, symbols: List[str],
                    sentiment: str = "neutral", urgency: str = "medium") -> None:
        """Publish news item and notify subscribers."""
        news_item = NewsItem(title, content, symbols, sentiment, urgency)
        self._news_history.append(news_item)
        
        self.notify(AlertType.NEWS_ALERT, news_item)
        print(f"📰 Published news: {title} (affects {len(symbols)} stocks)")
    
    def get_recent_news(self, count: int = 10) -> List[NewsItem]:
        """Get recent news items."""
        return self._news_history[-count:]


class TechnicalAnalyzer(Subject):
    """
    Technical analysis service that generates trading signals.
    """
    
    def __init__(self):
        super().__init__()
        self._signals_history: List[TechnicalSignal] = []
    
    def generate_signal(self, symbol: str, signal_type: str, strength: float,
                       description: str, target_price: Optional[float] = None) -> None:
        """Generate and broadcast a technical signal."""
        signal = TechnicalSignal(symbol, signal_type, strength, description, target_price)
        self._signals_history.append(signal)
        
        self.notify(AlertType.TECHNICAL_SIGNAL, signal)
        print(f"📊 Generated {signal_type} signal for {symbol} (strength: {strength:.2f})")
    
    def get_recent_signals(self, symbol: Optional[str] = None, count: int = 10) -> List[TechnicalSignal]:
        """Get recent technical signals, optionally filtered by symbol."""
        signals = self._signals_history
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        return signals[-count:]


class MarketScheduler(Subject):
    """
    Market scheduler that handles market open/close events.
    """
    
    def __init__(self):
        super().__init__()
        self._market_open = False
    
    def open_market(self) -> None:
        """Open the market and notify observers."""
        if not self._market_open:
            self._market_open = True
            market_data = {
                "status": "open",
                "timestamp": datetime.now(),
                "message": "Market is now open for trading"
            }
            self.notify(AlertType.MARKET_OPEN, market_data)
            print("🔔 Market opened")
    
    def close_market(self) -> None:
        """Close the market and notify observers."""
        if self._market_open:
            self._market_open = False
            market_data = {
                "status": "closed",
                "timestamp": datetime.now(),
                "message": "Market is now closed"
            }
            self.notify(AlertType.MARKET_CLOSE, market_data)
            print("🔔 Market closed")
    
    @property
    def is_market_open(self) -> bool:
        return self._market_open


class RetailInvestor(Observer):
    """
    Retail investor who receives basic market alerts.
    """
    
    def __init__(self, name: str, risk_tolerance: str = "medium"):
        self.name = name
        self.risk_tolerance = risk_tolerance  # low, medium, high
        self.portfolio: Dict[str, int] = {}  # symbol -> shares
        self.watchlist: Set[str] = set()
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_to_watchlist(self, symbol: str) -> None:
        """Add stock to watchlist."""
        self.watchlist.add(symbol)
        print(f"👤 {self.name} added {symbol} to watchlist")
    
    def buy_stock(self, symbol: str, shares: int) -> None:
        """Buy stock shares."""
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + shares
        print(f"👤 {self.name} bought {shares} shares of {symbol}")
    
    def update(self, alert_type: AlertType, data: Any) -> None:
        """Handle market updates based on investor preferences."""
        alert_record = {
            "timestamp": datetime.now(),
            "alert_type": alert_type.value,
            "data": data
        }
        self.alert_history.append(alert_record)
        
        if alert_type == AlertType.PRICE_CHANGE:
            self._handle_price_alert(data)
        elif alert_type == AlertType.NEWS_ALERT:
            self._handle_news_alert(data)
        elif alert_type == AlertType.TECHNICAL_SIGNAL:
            self._handle_technical_signal(data)
        elif alert_type in [AlertType.MARKET_OPEN, AlertType.MARKET_CLOSE]:
            self._handle_market_status(data)
    
    def _handle_price_alert(self, data: Any) -> None:
        """Handle price change alerts."""
        if hasattr(data, 'symbol'):  # StockData object
            symbol = data.symbol
            if symbol in self.watchlist or symbol in self.portfolio:
                print(f"👤 {self.name}: {symbol} price changed to ${data.price:.2f} ({data.change_percent:+.2f}%)")
        elif isinstance(data, dict) and 'symbol' in data:  # Threshold alert
            symbol = data['symbol']
            if symbol in self.watchlist or symbol in self.portfolio:
                print(f"👤 {self.name}: {symbol} crossed {data['threshold_type']} threshold at ${data['price']:.2f}")
    
    def _handle_news_alert(self, news_item: NewsItem) -> None:
        """Handle news alerts."""
        relevant_symbols = [s for s in news_item.symbols if s in self.watchlist or s in self.portfolio]
        if relevant_symbols:
            print(f"👤 {self.name}: News alert for {relevant_symbols}: {news_item.title}")
    
    def _handle_technical_signal(self, signal: TechnicalSignal) -> None:
        """Handle technical signals based on risk tolerance."""
        if signal.symbol in self.watchlist or signal.symbol in self.portfolio:
            if self.risk_tolerance == "high" or signal.strength >= 0.7:
                print(f"👤 {self.name}: Technical signal for {signal.symbol}: {signal.signal_type} (strength: {signal.strength:.2f})")
    
    def _handle_market_status(self, data: Dict[str, Any]) -> None:
        """Handle market open/close notifications."""
        print(f"👤 {self.name}: Market {data['status']} notification received")
    
    def get_observer_id(self) -> str:
        return f"RetailInvestor_{self.name}"
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        return {
            "name": self.name,
            "portfolio": self.portfolio,
            "watchlist": list(self.watchlist),
            "alerts_received": len(self.alert_history),
            "risk_tolerance": self.risk_tolerance
        }


class InstitutionalInvestor(Observer):
    """
    Institutional investor with more sophisticated alert handling.
    """
    
    def __init__(self, firm_name: str, assets_under_management: float):
        self.firm_name = firm_name
        self.aum = assets_under_management
        self.positions: Dict[str, Dict[str, Any]] = {}  # symbol -> {shares, avg_price, etc.}
        self.alert_filters: Dict[AlertType, Callable] = {}
        self.high_priority_alerts: List[Dict[str, Any]] = []
    
    def set_alert_filter(self, alert_type: AlertType, filter_func: Callable) -> None:
        """Set custom filter for specific alert types."""
        self.alert_filters[alert_type] = filter_func
    
    def add_position(self, symbol: str, shares: int, avg_price: float) -> None:
        """Add or update position."""
        self.positions[symbol] = {
            "shares": shares,
            "avg_price": avg_price,
            "market_value": 0.0,
            "unrealized_pnl": 0.0
        }
        print(f"🏢 {self.firm_name} updated position: {shares} shares of {symbol} at ${avg_price:.2f}")
    
    def update(self, alert_type: AlertType, data: Any) -> None:
        """Handle alerts with institutional-level sophistication."""
        # Apply custom filters if set
        if alert_type in self.alert_filters:
            if not self.alert_filters[alert_type](data):
                return  # Filtered out
        
        # Process alert based on type
        if alert_type == AlertType.PRICE_CHANGE:
            self._handle_institutional_price_alert(data)
        elif alert_type == AlertType.VOLUME_SPIKE:
            self._handle_volume_alert(data)
        elif alert_type == AlertType.NEWS_ALERT:
            self._handle_institutional_news_alert(data)
        elif alert_type == AlertType.TECHNICAL_SIGNAL:
            self._handle_institutional_technical_alert(data)
    
    def _handle_institutional_price_alert(self, data: Any) -> None:
        """Handle price alerts with position analysis."""
        if hasattr(data, 'symbol'):
            symbol = data.symbol
            if symbol in self.positions:
                position = self.positions[symbol]
                position["market_value"] = position["shares"] * data.price
                position["unrealized_pnl"] = (data.price - position["avg_price"]) * position["shares"]
                
                # Alert on significant P&L changes
                if abs(position["unrealized_pnl"]) > 100000:  # $100k threshold
                    alert = {
                        "timestamp": datetime.now(),
                        "type": "large_pnl_move",
                        "symbol": symbol,
                        "pnl": position["unrealized_pnl"],
                        "price": data.price
                    }
                    self.high_priority_alerts.append(alert)
                    print(f"🏢 {self.firm_name}: LARGE P&L MOVE - {symbol} P&L: ${position['unrealized_pnl']:,.2f}")
    
    def _handle_volume_alert(self, data: StockData) -> None:
        """Handle volume spike alerts."""
        if data.symbol in self.positions:
            print(f"🏢 {self.firm_name}: Volume spike in position {data.symbol} - {data.volume:,} shares")
    
    def _handle_institutional_news_alert(self, news_item: NewsItem) -> None:
        """Handle news with impact assessment."""
        relevant_positions = [s for s in news_item.symbols if s in self.positions]
        if relevant_positions:
            total_exposure = sum(self.positions[s]["market_value"] for s in relevant_positions)
            
            if news_item.urgency == "critical" or total_exposure > 1000000:  # $1M exposure
                alert = {
                    "timestamp": datetime.now(),
                    "type": "high_impact_news",
                    "title": news_item.title,
                    "affected_positions": relevant_positions,
                    "total_exposure": total_exposure
                }
                self.high_priority_alerts.append(alert)
                print(f"🏢 {self.firm_name}: HIGH IMPACT NEWS - {news_item.title} (Exposure: ${total_exposure:,.2f})")
    
    def _handle_institutional_technical_alert(self, signal: TechnicalSignal) -> None:
        """Handle technical signals with position-based decisions."""
        if signal.symbol in self.positions and signal.strength >= 0.8:
            position_size = self.positions[signal.symbol]["market_value"]
            print(f"🏢 {self.firm_name}: Strong technical signal for {signal.symbol} - {signal.signal_type} (Position: ${position_size:,.2f})")
    
    def get_observer_id(self) -> str:
        return f"Institutional_{self.firm_name}"
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Generate risk report."""
        total_value = sum(pos["market_value"] for pos in self.positions.values())
        total_pnl = sum(pos["unrealized_pnl"] for pos in self.positions.values())
        
        return {
            "firm_name": self.firm_name,
            "total_positions": len(self.positions),
            "total_market_value": total_value,
            "total_unrealized_pnl": total_pnl,
            "high_priority_alerts": len(self.high_priority_alerts),
            "largest_position": max(self.positions.items(), key=lambda x: x[1]["market_value"]) if self.positions else None
        }


def main():
    """
    Demonstrate the Stock Market Trading Observer System.
    """
    print("=== Stock Market Trading Observer System Demo ===")
    
    # Create market data sources
    price_monitor = StockPriceMonitor()
    news_service = NewsService()
    technical_analyzer = TechnicalAnalyzer()
    market_scheduler = MarketScheduler()
    
    # Add stocks to monitor
    stocks = [
        ("AAPL", 150.00),
        ("GOOGL", 2800.00),
        ("TSLA", 800.00),
        ("MSFT", 300.00),
        ("AMZN", 3400.00)
    ]
    
    for symbol, price in stocks:
        price_monitor.add_stock(symbol, price)
    
    print(f"\n📈 Initialized price monitoring for {len(stocks)} stocks")
    
    # Create investors
    retail1 = RetailInvestor("Alice Johnson", "medium")
    retail2 = RetailInvestor("Bob Smith", "high")
    institutional = InstitutionalInvestor("Quantum Capital", 500_000_000)
    
    print(f"\n👥 Created {3} market participants")
    
    # Set up watchlists and positions
    retail1.add_to_watchlist("AAPL")
    retail1.add_to_watchlist("MSFT")
    retail1.buy_stock("AAPL", 100)
    
    retail2.add_to_watchlist("TSLA")
    retail2.add_to_watchlist("GOOGL")
    retail2.buy_stock("TSLA", 50)
    
    institutional.add_position("AAPL", 10000, 145.00)
    institutional.add_position("GOOGL", 1000, 2750.00)
    institutional.add_position("MSFT", 5000, 295.00)
    
    # Subscribe to alerts with different preferences
    print(f"\n📊 Setting up subscriptions:")
    
    # Retail investors subscribe to basic alerts
    price_monitor.attach(retail1, [AlertType.PRICE_CHANGE])
    news_service.attach(retail1, [AlertType.NEWS_ALERT])
    market_scheduler.attach(retail1, [AlertType.MARKET_OPEN, AlertType.MARKET_CLOSE])
    
    price_monitor.attach(retail2, [AlertType.PRICE_CHANGE, AlertType.VOLUME_SPIKE])
    technical_analyzer.attach(retail2, [AlertType.TECHNICAL_SIGNAL])
    news_service.attach(retail2, [AlertType.NEWS_ALERT])
    
    # Institutional investor subscribes to all alerts
    price_monitor.attach(institutional)
    news_service.attach(institutional)
    technical_analyzer.attach(institutional)
    market_scheduler.attach(institutional)
    
    # Set institutional filters
    def significant_volume_filter(data):
        """Only alert on very high volume."""
        return hasattr(data, 'volume') and data.volume > 2000
    
    institutional.set_alert_filter(AlertType.VOLUME_SPIKE, significant_volume_filter)
    
    # Simulate market opening
    print(f"\n🔔 Market Events:")
    market_scheduler.open_market()
    
    # Simulate price movements
    print(f"\n📈 Price Movements:")
    
    price_changes = [
        ("AAPL", 152.50, 1200),    # +1.67% change
        ("TSLA", 820.00, 1800),    # +2.5% change, volume spike
        ("GOOGL", 2750.00, 800),   # -1.79% change
        ("MSFT", 307.50, 1100),    # +2.5% change
        ("AAPL", 155.00, 1500),    # Additional AAPL movement
    ]
    
    for symbol, new_price, volume in price_changes:
        print(f"\n--- {symbol} price update ---")
        price_monitor.update_stock_price(symbol, new_price, volume)
        time.sleep(0.5)  # Small delay to see notifications
    
    # Publish news
    print(f"\n📰 News Publications:")
    
    news_items = [
        {
            "title": "Apple Announces Record Quarterly Earnings",
            "content": "Apple Inc. reported record-breaking quarterly earnings...",
            "symbols": ["AAPL"],
            "sentiment": "positive",
            "urgency": "high"
        },
        {
            "title": "Federal Reserve Raises Interest Rates",
            "content": "The Federal Reserve announced a 0.25% interest rate increase...",
            "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
            "sentiment": "negative",
            "urgency": "critical"
        },
        {
            "title": "Tesla Recalls 50,000 Vehicles",
            "content": "Tesla announced a voluntary recall of 50,000 vehicles...",
            "symbols": ["TSLA"],
            "sentiment": "negative",
            "urgency": "medium"
        }
    ]
    
    for news in news_items:
        news_service.publish_news(**news)
        time.sleep(0.3)
    
    # Generate technical signals
    print(f"\n📊 Technical Analysis Signals:")
    
    signals = [
        ("AAPL", "buy", 0.85, "Strong bullish momentum with RSI oversold recovery", 160.00),
        ("TSLA", "sell", 0.75, "Bearish divergence on daily chart", 750.00),
        ("GOOGL", "hold", 0.60, "Consolidation pattern near support level", None),
        ("MSFT", "buy", 0.90, "Breakout above key resistance with high volume", 320.00)
    ]
    
    for symbol, signal_type, strength, description, target in signals:
        technical_analyzer.generate_signal(symbol, signal_type, strength, description, target)
        time.sleep(0.2)
    
    # Display portfolio summaries
    print(f"\n👥 Investor Summaries:")
    
    print(f"\nRetail Investor 1 (Alice):")
    summary1 = retail1.get_portfolio_summary()
    print(f"  Portfolio: {summary1['portfolio']}")
    print(f"  Watchlist: {summary1['watchlist']}")
    print(f"  Alerts received: {summary1['alerts_received']}")
    
    print(f"\nRetail Investor 2 (Bob):")
    summary2 = retail2.get_portfolio_summary()
    print(f"  Portfolio: {summary2['portfolio']}")
    print(f"  Watchlist: {summary2['watchlist']}")
    print(f"  Alerts received: {summary2['alerts_received']}")
    
    print(f"\nInstitutional Investor (Quantum Capital):")
    risk_report = institutional.get_risk_report()
    print(f"  Total positions: {risk_report['total_positions']}")
    print(f"  Total market value: ${risk_report['total_market_value']:,.2f}")
    print(f"  Total unrealized P&L: ${risk_report['total_unrealized_pnl']:,.2f}")
    print(f"  High priority alerts: {risk_report['high_priority_alerts']}")
    
    # Test unsubscribing
    print(f"\n📊 Testing Unsubscribe:")
    print("Alice unsubscribing from price alerts...")
    price_monitor.detach(retail1)
    
    # More price movement (Alice shouldn't get notified)
    print("Moving AAPL price again...")
    price_monitor.update_stock_price("AAPL", 160.00, 1600)
    
    # Market close
    print(f"\n🔔 Market Close:")
    market_scheduler.close_market()
    
    # Final statistics
    print(f"\n📊 Final Market Data:")
    all_stocks = price_monitor.get_all_stocks()
    for symbol, stock_data in all_stocks.items():
        print(f"  {symbol}: ${stock_data.price:.2f} ({stock_data.change_percent:+.2f}%) "
              f"Volume: {stock_data.volume:,}")
        print(f"    Daily Range: ${stock_data.day_low:.2f} - ${stock_data.day_high:.2f}")
    
    print(f"\n📈 Recent Technical Signals:")
    recent_signals = technical_analyzer.get_recent_signals(count=3)
    for signal in recent_signals:
        print(f"  {signal.symbol}: {signal.signal_type.upper()} (strength: {signal.strength:.2f})")
        print(f"    {signal.description}")
    
    print(f"\n📰 Recent News:")
    recent_news = news_service.get_recent_news(count=2)
    for news in recent_news:
        print(f"  {news.title} ({news.sentiment} sentiment)")
        print(f"    Affects: {', '.join(news.symbols)}")


if __name__ == "__main__":
    main()