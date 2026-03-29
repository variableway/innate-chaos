"""News model for storing news items."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from app.database import Base


class News(Base):
    """News model for storing news items."""
    
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    url = Column(String(1000), nullable=True)
    
    # Scoring
    policy_score = Column(Float, default=0.0)  # 0.0 to 1.0
    sentiment = Column(Float, nullable=True)   # -1.0 to 1.0
    
    # Categorization
    category = Column(String(50), nullable=True)  # geopolitics, regulation, etc.
    keywords = Column(String(500), nullable=True)  # comma-separated
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_news_time', 'created_at'),
        Index('idx_news_source_time', 'source', 'created_at'),
    )
    
    def __repr__(self):
        return f"<News(source='{self.source}', score={self.policy_score}, time='{self.created_at}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "url": self.url,
            "policy_score": self.policy_score,
            "sentiment": self.sentiment,
            "category": self.category,
            "keywords": self.keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
