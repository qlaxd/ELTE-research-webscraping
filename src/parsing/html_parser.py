from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup, Tag
from loguru import logger

from src.scraping.rules_loader import load_scraping_rules

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
        The input is now expected to be the relevant HTML fragment from the CSV.
        Therefore, the whole parsed soup is considered the content area.

        Returns:
            The BeautifulSoup Tag object representing the content area.
        """
        logger.debug("Using the entire provided HTML string as the content area.")
        return self.soup
