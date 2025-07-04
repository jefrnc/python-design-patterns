"""
Bridge Design Pattern - Real World Implementation

A real-world example demonstrating the Bridge pattern through a 
multimedia content delivery system that separates the abstraction 
of content delivery from the implementation of different streaming platforms.

This example shows how to:
- Decouple abstraction from implementation
- Support multiple streaming platforms (YouTube, Twitch, Netflix)
- Handle different content types (Video, Audio, Live Stream)
- Manage platform-specific configurations and features
- Provide unified interface while maintaining platform flexibility
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging


class ContentType(Enum):
    """Types of content that can be streamed."""
    VIDEO = "video"
    AUDIO = "audio"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    WEBINAR = "webinar"


class StreamQuality(Enum):
    """Available streaming quality options."""
    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4K"


@dataclass
class StreamMetrics:
    """Metrics for stream performance monitoring."""
    viewers: int = 0
    bandwidth_mbps: float = 0.0
    latency_ms: int = 0
    dropped_frames: int = 0
    buffer_health: float = 100.0  # Percentage


@dataclass
class ContentMetadata:
    """Metadata for content being streamed."""
    title: str
    duration_minutes: int
    file_size_mb: float
    thumbnail_url: str
    tags: List[str]
    age_rating: str = "PG"
    language: str = "en"


# Implementation Interface (Bridge)
class StreamingPlatform(ABC):
    """
    Abstract interface for streaming platform implementations.
    This is the implementor in the Bridge pattern.
    """
    
    @abstractmethod
    def initialize_stream(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Initialize a new stream on the platform."""
        pass
    
    @abstractmethod
    def start_streaming(self, content_id: str, quality: StreamQuality) -> bool:
        """Start streaming content."""
        pass
    
    @abstractmethod
    def stop_streaming(self, content_id: str) -> bool:
        """Stop streaming content."""
        pass
    
    @abstractmethod
    def get_stream_metrics(self, content_id: str) -> StreamMetrics:
        """Get current streaming metrics."""
        pass
    
    @abstractmethod
    def update_stream_settings(self, content_id: str, settings: Dict[str, Any]) -> bool:
        """Update stream settings during broadcast."""
        pass
    
    @abstractmethod
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get platform-specific capabilities and limitations."""
        pass


# Concrete Implementations
class YouTubePlatform(StreamingPlatform):
    """YouTube streaming platform implementation."""
    
    def __init__(self, api_key: str, channel_id: str):
        self.api_key = api_key
        self.channel_id = channel_id
        self.active_streams: Dict[str, Dict] = {}
        self.platform_name = "YouTube"
        
    def initialize_stream(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Initialize YouTube stream with specific requirements."""
        try:
            # YouTube-specific initialization
            stream_config = {
                "title": metadata.title,
                "description": f"Duration: {metadata.duration_minutes} minutes",
                "category": "Entertainment",
                "privacy": "public",
                "thumbnail": metadata.thumbnail_url,
                "tags": metadata.tags,
                "monetization_enabled": True,
                "chat_enabled": True,
                "dvr_enabled": True
            }
            
            self.active_streams[content_id] = {
                "config": stream_config,
                "status": "initialized",
                "stream_key": f"yt_stream_{content_id}",
                "metrics": StreamMetrics()
            }
            
            logging.info(f"YouTube stream {content_id} initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize YouTube stream {content_id}: {e}")
            return False
    
    def start_streaming(self, content_id: str, quality: StreamQuality) -> bool:
        """Start YouTube live stream."""
        if content_id not in self.active_streams:
            return False
        
        try:
            stream = self.active_streams[content_id]
            
            # YouTube-specific streaming logic
            rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream['stream_key']}"
            
            # Configure quality settings
            quality_settings = {
                StreamQuality.LOW: {"bitrate": 1000, "fps": 30},
                StreamQuality.MEDIUM: {"bitrate": 2500, "fps": 30},
                StreamQuality.HIGH: {"bitrate": 4500, "fps": 60},
                StreamQuality.ULTRA: {"bitrate": 8000, "fps": 60}
            }
            
            settings = quality_settings[quality]
            stream["quality"] = quality
            stream["bitrate"] = settings["bitrate"]
            stream["fps"] = settings["fps"]
            stream["status"] = "streaming"
            
            # Simulate starting stream
            logging.info(f"YouTube stream {content_id} started at {quality.value}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start YouTube stream {content_id}: {e}")
            return False
    
    def stop_streaming(self, content_id: str) -> bool:
        """Stop YouTube stream."""
        if content_id in self.active_streams:
            self.active_streams[content_id]["status"] = "stopped"
            logging.info(f"YouTube stream {content_id} stopped")
            return True
        return False
    
    def get_stream_metrics(self, content_id: str) -> StreamMetrics:
        """Get YouTube stream metrics."""
        if content_id in self.active_streams:
            # Simulate real-time metrics
            return StreamMetrics(
                viewers=1250,
                bandwidth_mbps=4.5,
                latency_ms=2000,  # YouTube has higher latency
                dropped_frames=5,
                buffer_health=95.0
            )
        return StreamMetrics()
    
    def update_stream_settings(self, content_id: str, settings: Dict[str, Any]) -> bool:
        """Update YouTube stream settings."""
        if content_id in self.active_streams:
            stream = self.active_streams[content_id]
            
            # YouTube allows limited live updates
            updatable_settings = ["title", "description", "chat_enabled"]
            for key, value in settings.items():
                if key in updatable_settings:
                    stream["config"][key] = value
            
            logging.info(f"YouTube stream {content_id} settings updated")
            return True
        return False
    
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get YouTube platform capabilities."""
        return {
            "max_bitrate": 51000,  # kbps
            "max_resolution": "4K",
            "supports_dvr": True,
            "supports_chat": True,
            "supports_monetization": True,
            "max_stream_duration": None,  # Unlimited
            "content_id_validation": True,
            "analytics_available": True,
            "supported_formats": ["H.264", "VP9"],
            "latency_type": "standard"  # 15-30 seconds
        }


class TwitchPlatform(StreamingPlatform):
    """Twitch streaming platform implementation."""
    
    def __init__(self, client_id: str, oauth_token: str):
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.active_streams: Dict[str, Dict] = {}
        self.platform_name = "Twitch"
        
    def initialize_stream(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Initialize Twitch stream."""
        try:
            # Twitch-specific initialization
            stream_config = {
                "title": metadata.title,
                "game_category": "Just Chatting",  # Default category
                "language": metadata.language,
                "tags": metadata.tags[:10],  # Twitch limits tags
                "mature_content": metadata.age_rating != "G",
                "subscriber_only_chat": False,
                "follower_only_chat": False,
                "slow_mode": False
            }
            
            self.active_streams[content_id] = {
                "config": stream_config,
                "status": "initialized",
                "stream_key": f"live_{self.client_id}_{content_id}",
                "metrics": StreamMetrics()
            }
            
            logging.info(f"Twitch stream {content_id} initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Twitch stream {content_id}: {e}")
            return False
    
    def start_streaming(self, content_id: str, quality: StreamQuality) -> bool:
        """Start Twitch live stream."""
        if content_id not in self.active_streams:
            return False
        
        try:
            stream = self.active_streams[content_id]
            
            # Twitch RTMP configuration
            ingest_server = "rtmp://live.twitch.tv/app/"
            
            # Twitch quality recommendations
            quality_settings = {
                StreamQuality.LOW: {"bitrate": 800, "fps": 30},
                StreamQuality.MEDIUM: {"bitrate": 2000, "fps": 30},
                StreamQuality.HIGH: {"bitrate": 3500, "fps": 60},
                StreamQuality.ULTRA: {"bitrate": 6000, "fps": 60}  # Partner only
            }
            
            settings = quality_settings[quality]
            stream["quality"] = quality
            stream["bitrate"] = settings["bitrate"]
            stream["fps"] = settings["fps"]
            stream["status"] = "streaming"
            stream["ingest_server"] = ingest_server
            
            logging.info(f"Twitch stream {content_id} started at {quality.value}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start Twitch stream {content_id}: {e}")
            return False
    
    def stop_streaming(self, content_id: str) -> bool:
        """Stop Twitch stream."""
        if content_id in self.active_streams:
            self.active_streams[content_id]["status"] = "stopped"
            logging.info(f"Twitch stream {content_id} stopped")
            return True
        return False
    
    def get_stream_metrics(self, content_id: str) -> StreamMetrics:
        """Get Twitch stream metrics."""
        if content_id in self.active_streams:
            return StreamMetrics(
                viewers=450,
                bandwidth_mbps=3.5,
                latency_ms=3000,  # Low latency mode available
                dropped_frames=2,
                buffer_health=98.0
            )
        return StreamMetrics()
    
    def update_stream_settings(self, content_id: str, settings: Dict[str, Any]) -> bool:
        """Update Twitch stream settings."""
        if content_id in self.active_streams:
            stream = self.active_streams[content_id]
            
            # Twitch allows many live updates
            updatable_settings = [
                "title", "game_category", "tags", "subscriber_only_chat", 
                "follower_only_chat", "slow_mode"
            ]
            
            for key, value in settings.items():
                if key in updatable_settings:
                    stream["config"][key] = value
            
            logging.info(f"Twitch stream {content_id} settings updated")
            return True
        return False
    
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get Twitch platform capabilities."""
        return {
            "max_bitrate": 6000,  # kbps (8000 for partners)
            "max_resolution": "1080p",  # 4K for partners
            "supports_dvr": True,
            "supports_chat": True,
            "supports_monetization": True,
            "max_stream_duration": None,  # Unlimited
            "content_id_validation": False,
            "analytics_available": True,
            "supported_formats": ["H.264"],
            "latency_type": "low",  # 2-5 seconds possible
            "interactive_features": ["polls", "predictions", "channel_points"]
        }


class NetflixPlatform(StreamingPlatform):
    """Netflix streaming platform implementation (for content providers)."""
    
    def __init__(self, partner_id: str, content_license: str):
        self.partner_id = partner_id
        self.content_license = content_license
        self.active_streams: Dict[str, Dict] = {}
        self.platform_name = "Netflix"
        
    def initialize_stream(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Initialize Netflix content stream."""
        try:
            # Netflix has strict content requirements
            stream_config = {
                "title": metadata.title,
                "duration": metadata.duration_minutes,
                "content_rating": metadata.age_rating,
                "audio_languages": [metadata.language],
                "subtitle_languages": ["en", "es", "fr"],
                "hdr_available": True,
                "dolby_atmos": True,
                "content_type": "premium",
                "global_availability": True,
                "download_enabled": True
            }
            
            self.active_streams[content_id] = {
                "config": stream_config,
                "status": "initialized",
                "encoding_profiles": ["H.264", "H.265", "AV1"],
                "metrics": StreamMetrics()
            }
            
            logging.info(f"Netflix content {content_id} initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Netflix content {content_id}: {e}")
            return False
    
    def start_streaming(self, content_id: str, quality: StreamQuality) -> bool:
        """Start Netflix content delivery."""
        if content_id not in self.active_streams:
            return False
        
        try:
            stream = self.active_streams[content_id]
            
            # Netflix adaptive streaming
            quality_profiles = {
                StreamQuality.LOW: {"bitrate": 500, "resolution": "480p"},
                StreamQuality.MEDIUM: {"bitrate": 1500, "resolution": "720p"},
                StreamQuality.HIGH: {"bitrate": 5000, "resolution": "1080p"},
                StreamQuality.ULTRA: {"bitrate": 15000, "resolution": "4K"}
            }
            
            profile = quality_profiles[quality]
            stream["quality"] = quality
            stream["bitrate"] = profile["bitrate"]
            stream["resolution"] = profile["resolution"]
            stream["status"] = "streaming"
            stream["adaptive_streaming"] = True
            
            logging.info(f"Netflix content {content_id} streaming at {quality.value}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start Netflix content {content_id}: {e}")
            return False
    
    def stop_streaming(self, content_id: str) -> bool:
        """Stop Netflix content delivery."""
        if content_id in self.active_streams:
            self.active_streams[content_id]["status"] = "stopped"
            logging.info(f"Netflix content {content_id} stopped")
            return True
        return False
    
    def get_stream_metrics(self, content_id: str) -> StreamMetrics:
        """Get Netflix streaming metrics."""
        if content_id in self.active_streams:
            return StreamMetrics(
                viewers=50000,  # Much higher scale
                bandwidth_mbps=15.0,
                latency_ms=100,  # Very low latency CDN
                dropped_frames=0,
                buffer_health=99.9
            )
        return StreamMetrics()
    
    def update_stream_settings(self, content_id: str, settings: Dict[str, Any]) -> bool:
        """Update Netflix content settings."""
        if content_id in self.active_streams:
            stream = self.active_streams[content_id]
            
            # Netflix has limited live updates
            updatable_settings = ["subtitle_languages", "audio_languages", "global_availability"]
            
            for key, value in settings.items():
                if key in updatable_settings:
                    stream["config"][key] = value
            
            logging.info(f"Netflix content {content_id} settings updated")
            return True
        return False
    
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get Netflix platform capabilities."""
        return {
            "max_bitrate": 15000,  # kbps
            "max_resolution": "4K",
            "supports_dvr": True,  # Built-in
            "supports_chat": False,
            "supports_monetization": False,  # Subscription model
            "max_stream_duration": None,
            "content_id_validation": True,
            "analytics_available": True,
            "supported_formats": ["H.264", "H.265", "AV1"],
            "latency_type": "optimized",
            "global_cdn": True,
            "adaptive_streaming": True,
            "offline_download": True
        }


# Abstraction Layer
class ContentDelivery(ABC):
    """
    Abstract content delivery system.
    This is the abstraction in the Bridge pattern.
    """
    
    def __init__(self, platform: StreamingPlatform):
        self.platform = platform
        self.content_registry: Dict[str, ContentMetadata] = {}
        
    def register_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Register content for streaming."""
        self.content_registry[content_id] = metadata
        return self.platform.initialize_stream(content_id, metadata)
    
    @abstractmethod
    def deliver_content(self, content_id: str, quality: StreamQuality) -> bool:
        """Deliver content using the platform."""
        pass
    
    def stop_delivery(self, content_id: str) -> bool:
        """Stop content delivery."""
        return self.platform.stop_streaming(content_id)
    
    def get_delivery_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive delivery status."""
        metrics = self.platform.get_stream_metrics(content_id)
        capabilities = self.platform.get_platform_capabilities()
        
        return {
            "content_id": content_id,
            "platform": self.platform.platform_name,
            "metrics": metrics,
            "capabilities": capabilities,
            "content_info": self.content_registry.get(content_id)
        }


# Refined Abstractions
class LiveStreamDelivery(ContentDelivery):
    """Live streaming content delivery implementation."""
    
    def __init__(self, platform: StreamingPlatform):
        super().__init__(platform)
        self.live_settings = {
            "auto_quality": True,
            "chat_moderation": True,
            "recording_enabled": True
        }
    
    def deliver_content(self, content_id: str, quality: StreamQuality) -> bool:
        """Start live streaming."""
        if content_id not in self.content_registry:
            logging.error(f"Content {content_id} not registered")
            return False
        
        # Configure live streaming specific settings
        live_config = {
            "stream_type": "live",
            "buffer_size": "minimal",
            "latency_optimization": True
        }
        
        success = self.platform.update_stream_settings(content_id, live_config)
        if success:
            return self.platform.start_streaming(content_id, quality)
        
        return False
    
    def enable_interactive_features(self, content_id: str, features: List[str]) -> bool:
        """Enable interactive features for live streams."""
        interactive_settings = {feature: True for feature in features}
        return self.platform.update_stream_settings(content_id, interactive_settings)
    
    def moderate_chat(self, content_id: str, moderation_level: str) -> bool:
        """Configure chat moderation."""
        moderation_config = {
            "chat_moderation_level": moderation_level,
            "auto_timeout_enabled": True,
            "banned_words_filter": True
        }
        return self.platform.update_stream_settings(content_id, moderation_config)


class OnDemandDelivery(ContentDelivery):
    """On-demand content delivery implementation."""
    
    def __init__(self, platform: StreamingPlatform):
        super().__init__(platform)
        self.encoding_settings = {
            "multiple_quality_levels": True,
            "adaptive_streaming": True,
            "preload_optimization": True
        }
    
    def deliver_content(self, content_id: str, quality: StreamQuality) -> bool:
        """Start on-demand content streaming."""
        if content_id not in self.content_registry:
            logging.error(f"Content {content_id} not registered")
            return False
        
        # Configure on-demand specific settings
        vod_config = {
            "stream_type": "vod",
            "buffer_size": "optimal",
            "seek_optimization": True,
            "thumbnail_generation": True
        }
        
        success = self.platform.update_stream_settings(content_id, vod_config)
        if success:
            return self.platform.start_streaming(content_id, quality)
        
        return False
    
    def generate_preview_clips(self, content_id: str, clip_positions: List[int]) -> bool:
        """Generate preview clips at specified positions."""
        preview_config = {
            "preview_clips_enabled": True,
            "clip_positions": clip_positions,
            "clip_duration": 10  # seconds
        }
        return self.platform.update_stream_settings(content_id, preview_config)
    
    def enable_download(self, content_id: str, download_quality: List[StreamQuality]) -> bool:
        """Enable offline download for supported platforms."""
        download_config = {
            "download_enabled": True,
            "download_qualities": [q.value for q in download_quality],
            "download_expiry": 30  # days
        }
        return self.platform.update_stream_settings(content_id, download_config)


class PodcastDelivery(ContentDelivery):
    """Podcast content delivery implementation."""
    
    def __init__(self, platform: StreamingPlatform):
        super().__init__(platform)
        self.audio_settings = {
            "audio_only": True,
            "transcript_generation": True,
            "chapter_markers": True
        }
    
    def deliver_content(self, content_id: str, quality: StreamQuality) -> bool:
        """Start podcast streaming (audio-focused)."""
        if content_id not in self.content_registry:
            logging.error(f"Content {content_id} not registered")
            return False
        
        # Configure podcast specific settings
        podcast_config = {
            "content_type": "audio",
            "video_disabled": True,
            "audio_bitrate_priority": True,
            "background_playback": True
        }
        
        success = self.platform.update_stream_settings(content_id, podcast_config)
        if success:
            # For podcasts, quality mainly affects audio bitrate
            return self.platform.start_streaming(content_id, quality)
        
        return False
    
    def add_chapter_markers(self, content_id: str, chapters: List[Dict]) -> bool:
        """Add chapter markers to podcast."""
        chapter_config = {
            "chapters_enabled": True,
            "chapter_data": chapters
        }
        return self.platform.update_stream_settings(content_id, chapter_config)


# Client Code Example
def demonstrate_bridge_pattern():
    """Demonstrate the Bridge pattern with content delivery systems."""
    
    print("=== Content Delivery System - Bridge Pattern Demo ===\n")
    
    # Create different platform implementations
    youtube = YouTubePlatform("yt_api_key_123", "channel_456")
    twitch = TwitchPlatform("twitch_client_789", "oauth_token_abc")
    netflix = NetflixPlatform("partner_001", "license_premium")
    
    # Create content metadata
    live_content = ContentMetadata(
        title="Live Gaming Session",
        duration_minutes=120,
        file_size_mb=0,  # Live stream
        thumbnail_url="https://example.com/gaming_thumb.jpg",
        tags=["gaming", "live", "interactive"],
        age_rating="T",
        language="en"
    )
    
    movie_content = ContentMetadata(
        title="Awesome Movie",
        duration_minutes=95,
        file_size_mb=4500,
        thumbnail_url="https://example.com/movie_thumb.jpg",
        tags=["drama", "action", "4k"],
        age_rating="PG-13",
        language="en"
    )
    
    podcast_content = ContentMetadata(
        title="Tech Talk Podcast Episode 42",
        duration_minutes=45,
        file_size_mb=85,
        thumbnail_url="https://example.com/podcast_thumb.jpg",
        tags=["technology", "interview", "education"],
        age_rating="G",
        language="en"
    )
    
    # Demonstrate live streaming on different platforms
    print("1. Live Streaming Examples:")
    print("-" * 30)
    
    # YouTube live stream
    youtube_live = LiveStreamDelivery(youtube)
    youtube_live.register_content("live_001", live_content)
    youtube_live.deliver_content("live_001", StreamQuality.HIGH)
    youtube_live.enable_interactive_features("live_001", ["chat", "super_chat", "polls"])
    
    status = youtube_live.get_delivery_status("live_001")
    print(f"YouTube Live Stream Status:")
    print(f"  Viewers: {status['metrics'].viewers}")
    print(f"  Platform: {status['platform']}")
    print(f"  Supports Chat: {status['capabilities']['supports_chat']}")
    print()
    
    # Twitch live stream
    twitch_live = LiveStreamDelivery(twitch)
    twitch_live.register_content("live_002", live_content)
    twitch_live.deliver_content("live_002", StreamQuality.HIGH)
    twitch_live.moderate_chat("live_002", "strict")
    
    status = twitch_live.get_delivery_status("live_002")
    print(f"Twitch Live Stream Status:")
    print(f"  Viewers: {status['metrics'].viewers}")
    print(f"  Platform: {status['platform']}")
    print(f"  Latency Type: {status['capabilities']['latency_type']}")
    print()
    
    # Demonstrate on-demand content
    print("2. On-Demand Content Examples:")
    print("-" * 35)
    
    # Netflix movie
    netflix_vod = OnDemandDelivery(netflix)
    netflix_vod.register_content("movie_001", movie_content)
    netflix_vod.deliver_content("movie_001", StreamQuality.ULTRA)
    netflix_vod.enable_download("movie_001", [StreamQuality.HIGH, StreamQuality.ULTRA])
    
    status = netflix_vod.get_delivery_status("movie_001")
    print(f"Netflix Movie Status:")
    print(f"  Viewers: {status['metrics'].viewers}")
    print(f"  Platform: {status['platform']}")
    print(f"  Max Resolution: {status['capabilities']['max_resolution']}")
    print(f"  Offline Download: {status['capabilities']['offline_download']}")
    print()
    
    # Demonstrate podcast delivery
    print("3. Podcast Delivery Examples:")
    print("-" * 30)
    
    # Podcast on multiple platforms
    for platform_name, platform in [("YouTube", youtube), ("Twitch", twitch)]:
        podcast_delivery = PodcastDelivery(platform)
        content_id = f"podcast_{platform_name.lower()}"
        
        podcast_delivery.register_content(content_id, podcast_content)
        podcast_delivery.deliver_content(content_id, StreamQuality.MEDIUM)
        
        chapters = [
            {"title": "Introduction", "start_time": 0},
            {"title": "Main Topic", "start_time": 300},
            {"title": "Q&A Session", "start_time": 1800},
            {"title": "Conclusion", "start_time": 2400}
        ]
        podcast_delivery.add_chapter_markers(content_id, chapters)
        
        status = podcast_delivery.get_delivery_status(content_id)
        print(f"{platform_name} Podcast Status:")
        print(f"  Platform: {status['platform']}")
        print(f"  Content Type: Audio-focused")
        print()
    
    # Demonstrate platform switching
    print("4. Platform Flexibility Example:")
    print("-" * 35)
    
    # Same content delivery logic with different platforms
    platforms = [
        ("YouTube", youtube),
        ("Twitch", twitch),
        ("Netflix", netflix)
    ]
    
    for platform_name, platform in platforms:
        delivery = OnDemandDelivery(platform)
        content_id = f"content_{platform_name.lower()}"
        
        delivery.register_content(content_id, movie_content)
        success = delivery.deliver_content(content_id, StreamQuality.HIGH)
        
        if success:
            capabilities = platform.get_platform_capabilities()
            print(f"{platform_name}:")
            print(f"  Max Bitrate: {capabilities['max_bitrate']} kbps")
            print(f"  Max Resolution: {capabilities['max_resolution']}")
            print(f"  Monetization: {capabilities['supports_monetization']}")
        
        delivery.stop_delivery(content_id)
    
    print("\n=== Bridge Pattern Benefits Demonstrated ===")
    print("✓ Abstraction separated from implementation")
    print("✓ Platform-specific features accessible")
    print("✓ Easy to add new platforms")
    print("✓ Content delivery logic reusable across platforms")
    print("✓ Runtime platform switching possible")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the demonstration
    demonstrate_bridge_pattern()