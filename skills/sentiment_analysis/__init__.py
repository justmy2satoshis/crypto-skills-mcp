"""
Sentiment Analysis Skills

Token-efficient procedural implementations for sentiment analysis tasks
(news scoring, social tracking, whale monitoring, etc).
"""

from .news_sentiment_scorer import NewsSentimentScorer, news_sentiment_scorer
from .social_sentiment_tracker import SocialSentimentTracker, social_sentiment_tracker
from .whale_activity_monitor import WhaleActivityMonitor, whale_activity_monitor
from .sentiment_fusion import SentimentFusion, sentiment_fusion

__all__ = [
    "NewsSentimentScorer",
    "news_sentiment_scorer",
    "SocialSentimentTracker",
    "social_sentiment_tracker",
    "WhaleActivityMonitor",
    "whale_activity_monitor",
    "SentimentFusion",
    "sentiment_fusion",
]
