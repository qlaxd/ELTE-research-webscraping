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
        Extracts the main content area from the parsed HTML using a list of potential selectors.
        This method tries several selectors in order to handle different page layouts across years.

        Returns:
            A BeautifulSoup Tag object representing the content area, or None if not found.
        """
        # A list of selectors to try in order. More specific ones come first.
        potential_selectors = [
            'div.stenogram',        # For layouts with a specific div class
            'body > blockquote:nth-of-type(2)', # For modern layouts with two blockquotes in body
            'body > div > blockquote',          # For older layouts where content is in a div
            'body > blockquote'               # General fallback for pages with only one blockquote
        ]

        for selector in potential_selectors:
            logger.debug(f"Attempting to extract content area with selector: '{selector}'")
            content_area = self.soup.select_one(selector)
            if content_area:
                # Basic sanity check to ensure the selected blockquote is not just navigation
                if content_area.find('a', href=lambda href: href and 'Navigate&To=Prev' in href):
                    logger.debug(f"Selector '{selector}' found a navigation blockquote, skipping.")
                    continue
                logger.info(f"Successfully extracted main content area using selector: '{selector}'")
                return content_area
        
        logger.warning(f"Could not find the content area using any of the potential selectors: {potential_selectors}") 
        return None
