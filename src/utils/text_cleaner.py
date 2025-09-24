import re
import unicodedata

class TextCleaner:
    """A utility class for cleaning and normalizing text content."""

    # Regex to find HTML tags
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    # Regex to find and remove all bracketed content, like (Oklaski) or (Początek posiedzenia...)
    BRACKET_INFO_PATTERN = re.compile(r'\s*\([^)]*\)\s*')
    # Regex to find and remove stray metadata, e.g., 'POS: 1 DZIEN: 1'
    METADATA_PATTERN = re.compile(r'\b([A-Z0-9]+:\s*.*?)(?=\s[A-Z0-9]+:|$)')
    # Regex for multiple whitespace characters
    WHITESPACE_PATTERN = re.compile(r'\s+')

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Removes HTML tags and entities from a string."""
        if not text:
            return ""
        # Replace common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        # Remove all HTML tags
        text = TextCleaner.HTML_TAG_PATTERN.sub('', text)
        return text

    @staticmethod
    def normalize_polish_chars(text: str) -> str:
        """Normalizes unicode characters to a consistent form (NFC)."""
        if not text:
            return ""
        return unicodedata.normalize('NFC', text)

    @staticmethod
    def clean_text(
        text: str,
        remove_html: bool = True,
        normalize_chars: bool = True
    ) -> str:
        """
        Applies a full cleaning pipeline to the input text.

        Args:
            text: The string to clean.
            remove_html: Whether to remove HTML tags and entities.
            normalize_chars: Whether to normalize unicode characters.

        Returns:
            The cleaned and normalized text.
        """
        if not text:
            return ""

        if remove_html:
            text = TextCleaner.remove_html_tags(text)
        
        # Remove all bracketed content (e.g., applause, session times)
        text = TextCleaner.BRACKET_INFO_PATTERN.sub(' ', text)

        # Remove stray metadata patterns
        text = TextCleaner.METADATA_PATTERN.sub('', text)

        if normalize_chars:
            text = TextCleaner.normalize_polish_chars(text)

        # Replace multiple whitespace characters with a single space and strip leading/trailing whitespace
        text = TextCleaner.WHITESPACE_PATTERN.sub(' ', text).strip()

        return text
