import hashlib
from pathlib import Path
import pickle
import time
from typing import Any, Optional
from loguru import logger

class CacheManager:
    """Manages a file-based cache for storing web content to avoid redundant downloads."""

    def __init__(self, cache_dir: Path, cache_ttl_seconds: int = 86400):
        """
        Initializes the CacheManager.

        Args:
            cache_dir: The directory where cache files will be stored.
            cache_ttl_seconds: The Time-To-Live for cache entries in seconds (default: 1 day).
        """
        self.cache_dir = cache_dir
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, url: str) -> str:
        """
        Generates a unique, filesystem-safe cache key from a URL.

        Args:
            url: The URL to generate a key for.

        Returns:
            A SHA256 hash of the URL to be used as a filename.
        """
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def get_from_cache(self, url: str) -> Optional[Any]:
        """
        Retrieves content from the cache if it exists and has not expired.

        Args:
            url: The URL of the content to retrieve.

        Returns:
            The cached content, or None if it's not in the cache or has expired.
        """
        cache_key = self._generate_cache_key(url)
        cache_file = self.cache_dir / cache_key

        if not cache_file.exists():
            logger.debug(f"Cache miss for URL: {url}")
            return None

        try:
            with open(cache_file, 'rb') as f:
                cache_entry = pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            logger.warning(f"Could not read corrupted cache file {cache_file}. Removing it. Error: {e}")
            cache_file.unlink()
            return None

        # Check if the cache entry has expired
        age_seconds = time.time() - cache_entry['timestamp']
        if age_seconds > self.cache_ttl_seconds:
            logger.info(f"Cache expired for URL: {url}. Removing old cache file.")
            cache_file.unlink()
            return None

        logger.info(f"Cache hit for URL: {url}")
        return cache_entry['content']

    def save_to_cache(self, url: str, content: Any):
        """
        Saves content to the cache.

        Args:
            url: The URL of the content being cached.
            content: The content to save.
        """
        cache_key = self._generate_cache_key(url)
        cache_file = self.cache_dir / cache_key

        cache_entry = {
            'url': url,
            'timestamp': time.time(),
            'content': content
        }

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_entry, f)
            logger.info(f"Saved content for URL to cache: {url}")
        except IOError as e:
            logger.error(f"Could not write to cache file {cache_file}: {e}")

    def clear_expired_cache(self):
        """Iterates through the cache directory and removes all expired files."""
        logger.info("Clearing expired cache files...")
        cleared_count = 0
        for cache_file in self.cache_dir.iterdir():
            if not cache_file.is_file():
                continue
            try:
                with open(cache_file, 'rb') as f:
                    timestamp = pickle.load(f).get('timestamp', 0)
                if (time.time() - timestamp) > self.cache_ttl_seconds:
                    cache_file.unlink()
                    cleared_count += 1
                    logger.debug(f"Removed expired cache file: {cache_file.name}")
            except (pickle.UnpicklingError, EOFError, KeyError):
                logger.warning(f"Removing corrupted or invalid cache file: {cache_file.name}")
                cache_file.unlink()
        logger.info(f"Cleared {cleared_count} expired cache files.")

    def clear_all_cache(self):
        """Removes all files from the cache directory."""
        logger.warning("Clearing all cache files...")
        cleared_count = 0
        for item in self.cache_dir.iterdir():
            if item.is_file():
                item.unlink()
                cleared_count += 1
        logger.info(f"Cleared {cleared_count} cache files.")
