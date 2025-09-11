import logging
from pathlib import Path
from typing import Dict, Optional

from bs4 import BeautifulSoup, Tag

from src.scraping.rules_loader import load_scraping_rules

logger = logging.getLogger(__name__)

class HTMLParser:
    """Parses HTML content to extract the main transcript area using year-specific rules."""

    def __init__(self, html_content: str, year: int, rules_path: Path):
        """
        Initializes the HTMLParser.

        Args:
            html_content: The raw HTML content of the session page.
            year: The year of the session, used to select the correct parsing rules.
            rules_path: The path to the scraping rules YAML file.
        """
        if not html_content:
            raise ValueError("HTML content cannot be empty.")
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.year = year
        try:
            self.rules = load_scraping_rules(rules_path, year)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Could not load scraping rules for year {year}: {e}")
            raise

    def extract_content_area(self) -> Optional[Tag]:
        """
        Extracts the main content area from the parsed HTML using the loaded rules.

        Returns:
            A BeautifulSoup Tag object representing the content area, or None if not found.
        """
        content_selector = self.rules.get('content_container')
        if not content_selector:
            logger.error(f"'content_container' selector not found in rules for year {self.year}.")
            return None

        logger.debug(f"Extracting content area with selector: '{content_selector}'")
        content_area = self.soup.select_one(content_selector)

        if not content_area:
            logger.warning(f"Could not find the content area using selector: '{content_selector}'")
            return None

        logger.info("Successfully extracted main content area.")
        return content_area
