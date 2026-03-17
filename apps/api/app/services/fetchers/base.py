"""
Base data source adapter interface.

All data source fetchers should inherit from BaseFetcher.
This provides a consistent interface for adding new sources
(e.g., Twitter/X, Telegram, YouTube, etc.) without modifying
the core pipeline.

Usage:
    class MyNewFetcher(BaseFetcher):
        source_type = "my_source"

        async def fetch(self, source: Dict) -> List[TrendingArticle]:
            # Fetch and return articles
            ...

        async def fetch_all(self, sources: List[Dict]) -> List[TrendingArticle]:
            # Fetch from all sources of this type
            ...
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from app.models.trending import TrendingArticle


class BaseFetcher(ABC):
    """
    Abstract base class for all data source fetchers.

    Subclasses must implement:
    - source_type: str identifier for this source type
    - fetch(): fetch articles from a single source
    - fetch_all(): fetch from multiple sources
    """

    source_type: str = "base"

    @abstractmethod
    async def fetch(self, source: Dict) -> List[TrendingArticle]:
        """
        Fetch articles from a single source config.

        Args:
            source: Dict with at minimum 'id', 'name', 'url'

        Returns:
            List of TrendingArticle instances (not yet committed to DB)
        """
        ...

    @abstractmethod
    async def fetch_all(self, sources: List[Dict]) -> List[TrendingArticle]:
        """
        Fetch articles from all sources of this type.

        Args:
            sources: List of source config dicts

        Returns:
            Combined list of TrendingArticle instances
        """
        ...

    async def close(self):
        """Cleanup resources (HTTP sessions, connections, etc.)"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} type={self.source_type}>"
