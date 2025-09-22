from typing import Dict, List
from bs4 import Tag
from loguru import logger

from src.utils.text_cleaner import TextCleaner

class SpeechExtractor:
    """Extracts speech segments from a parsed HTML content area."""

    def __init__(self, content_area: Tag, rules: Dict[str, str]):
        """
        Initializes the SpeechExtractor.

        Args:
            content_area: A BeautifulSoup Tag object representing the main content area.
            rules: A dictionary of scraping rules for the specific year.
        """
        if not content_area or not isinstance(content_area, Tag):
            raise ValueError("A valid BeautifulSoup Tag for 'content_area' must be provided.")
        self.content_area = content_area
        self.rules = rules
        self.speech_link_selector = self.rules.get('speech_link')
        if not self.speech_link_selector:
            raise ValueError("'speech_link' selector not found in rules.")

    def extract_segments(self) -> List[str]:
        """
        Extracts the Speaker's (Marszałek) speech segments from the content.

        The logic identifies segments as the text that appears between the hyperlinks
        of other speakers' speeches.

        Returns:
            A list of cleaned speech segments.
        """
        logger.info("Starting extraction of speech segments...")
        segments = []
        current_segment_parts = []

        # Find all delimiter links first using the robust selector
        delimiter_links = {link for link in self.content_area.select(self.speech_link_selector)}
        
        # Iterate through all descendants of the content area
        for element in self.content_area.descendants:
            # If the element is one of the delimiter hyperlinks, it marks the end of a segment.
            if element in delimiter_links:
                # When a delimiter is found, the accumulated text forms a segment
                if current_segment_parts:
                    full_segment = ' '.join(current_segment_parts).strip()
                    cleaned_segment = TextCleaner.clean_text(full_segment)
                    if cleaned_segment:
                        segments.append(cleaned_segment)
                        logger.debug(f"Extracted segment: {cleaned_segment[:100]}...")
                    current_segment_parts = [] # Reset for the next segment
            
            # If it's just text, add it to the current segment
            elif isinstance(element, str):
                text = element.strip()
                if text:
                    current_segment_parts.append(text)

        # Add the last segment if any text was accumulated after the final link
        if current_segment_parts:
            full_segment = ' '.join(current_segment_parts).strip()
            cleaned_segment = TextCleaner.clean_text(full_segment)
            if cleaned_segment:
                segments.append(cleaned_segment)
                logger.debug(f"Extracted final segment: {cleaned_segment[:100]}...")

        logger.info(f"Extraction complete. Found {len(segments)} speech segments.")
        self.validate_segments(segments)
        return segments

    def extract_hyperlinks(self) -> List[Dict[str, str]]:
        """
        Extracts all hyperlinks that act as delimiters.

        Returns:
            A list of dictionaries, where each dictionary contains the link's text and href.
        """
        links = []
        found_links = self.content_area.select(self.speech_link_selector)
        for link_tag in found_links:
            link_text = TextCleaner.clean_text(link_tag.get_text())
            link_href = link_tag.get('href')
            if link_text and link_href:
                links.append({'text': link_text, 'href': link_href})
        
        logger.info(f"Found {len(links)} hyperlinks in the content area.")
        return links

    def validate_segments(self, segments: List[str]):
        """
        Validates the extracted segments against the original text to ensure no significant
        data loss occurred during parsing.

        Args:
            segments: The list of extracted speech segments.
        """
        # Get the total text from the original content area, excluding script/style tags
        original_text = self.content_area.get_text(separator=' ', strip=True)
        cleaned_original_text = TextCleaner.clean_text(original_text)
        original_length = len(cleaned_original_text)

        segments_text = ' '.join(segments)
        segments_length = len(segments_text)

        # Allow for some minor discrepancy that might result from cleaning and joining
        discrepancy = abs(original_length - segments_length)
        discrepancy_ratio = discrepancy / original_length if original_length > 0 else 0

        logger.info(f"Validation: Original text length (cleaned): {original_length}")
        logger.info(f"Validation: Total segments length: {segments_length}")
        logger.info(f"Validation: Discrepancy ratio: {discrepancy_ratio:.2%}")

        # Log a warning if the discrepancy is more than a threshold (e.g., 5%)
        if discrepancy_ratio > 0.05:
            logger.warning(
                f"Significant discrepancy ({discrepancy_ratio:.2%}) between original text and extracted segments."
            )
        else:
            logger.info("Segment validation passed. No significant data loss detected.")
