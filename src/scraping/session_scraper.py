from typing import Optional
from loguru import logger

from src.scraping.cache_manager import CacheManager
from src.scraping.playwright_client import PlaywrightClient

class SessionScraper:
    """Scrapes and caches parliamentary session pages."""

    def __init__(self, playwright_client: PlaywrightClient, cache_manager: CacheManager):
        """
        Initializes the SessionScraper.

        Args:
            playwright_client: An instance of PlaywrightClient for making HTTP requests.
            cache_manager: An instance of CacheManager for caching content.
        """
        self.web_client = playwright_client
        self.cache_manager = cache_manager

    def fetch_session_html(self, session_url: str) -> Optional[str]:
        """
        Fetches the HTML content for a given session URL, utilizing a cache.
        """
        if not session_url:
            logger.warning("Session URL is empty, cannot fetch.")
            return None

        # 1. Try to get the content from the cache
        cached_html = self.cache_manager.get_from_cache(session_url)
        if cached_html:
            return cached_html

        # 2. If not in cache, fetch from the web
        logger.info(f"Content for {session_url} not in cache, fetching from web.")
        
        fetched_html = self.web_client.fetch(session_url)

        # 3. If fetching was successful, save the content to the cache
        if fetched_html:
            self.cache_manager.save_to_cache(session_url, fetched_html)
            return fetched_html
        
        logger.error(f"Failed to fetch session HTML for URL: {session_url}")
        return None
