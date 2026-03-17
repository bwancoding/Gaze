"""
News fetchers for RSS, Reddit, Hacker News, and future sources.

All fetchers implement the BaseFetcher interface for consistency.
To add a new source type, create a new module and subclass BaseFetcher.
"""

from app.services.fetchers.base import BaseFetcher

__all__ = ["BaseFetcher"]
