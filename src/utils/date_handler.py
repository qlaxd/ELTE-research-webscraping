from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DateHandler:
    """A utility class for handling date parsing, formatting, and validation."""

    DATE_FORMAT = "%Y.%m.%d"

    @staticmethod
    def parse_polish_date(date_str: str) -> Optional[datetime]:
        """
        Parses a date string in 'YYYY.MM.DD' format into a datetime object.

        Args:
            date_str: The date string to parse.

        Returns:
            A datetime object or None if parsing fails.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, DateHandler.DATE_FORMAT)
        except ValueError:
            logger.warning(f"Date string '{date_str}' does not match format 'YYYY.MM.DD'.")
            return None

    @staticmethod
    def generate_session_id(date: datetime) -> str:
        """
        Generates a unique session identifier from a datetime object.

        Args:
            date: The datetime object for the session.

        Returns:
            A string identifier in the format 'session_YYYYMMDD'.
        """
        return f"session_{date.strftime('%Y%m%d')}"

    @staticmethod
    def validate_date_range(start_date_str: str, end_date_str: str, min_year: int = 1991, max_year: int = 2011) -> bool:
        """
        Validates that the start date is before the end date and within the project's year range.

        Args:
            start_date_str: The start date string ('YYYY.MM.DD').
            end_date_str: The end date string ('YYYY.MM.DD').
            min_year: The minimum allowed year.
            max_year: The maximum allowed year.

        Returns:
            True if the date range is valid, False otherwise.
        """
        start_date = DateHandler.parse_polish_date(start_date_str)
        end_date = DateHandler.parse_polish_date(end_date_str)

        if not start_date or not end_date:
            logger.error("Invalid date format provided for range validation.")
            return False

        if not (min_year <= start_date.year <= max_year and min_year <= end_date.year <= max_year):
            logger.error(f"Dates are outside the allowed year range ({min_year}-{max_year}).")
            return False

        if start_date > end_date:
            logger.error("Start date cannot be after end date.")
            return False

        return True

    @staticmethod
    def format_date_for_url(date: datetime) -> str:
        """
        Formats a datetime object into the string format required for URLs ('YYYY.MM.DD').
        Note: The actual URL structure might be more complex and vary by year.
        This is a baseline implementation.

        Args:
            date: The datetime object to format.

        Returns:
            A formatted date string.
        """
        return date.strftime(DateHandler.DATE_FORMAT)
