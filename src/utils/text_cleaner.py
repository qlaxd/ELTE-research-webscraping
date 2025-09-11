import re
import unicodedata

class TextCleaner:
    """A utility class for cleaning and normalizing text content."""

    # Regex to find HTML tags
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    # Regex to find bracketed info, often at the start of transcripts, e.g., (godz. 9:02) or (przerwa)
    BRACKET_INFO_PATTERN = re.compile(r'^\s*\([^)]*\)\s*')
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
    def remove_session_brackets(text: str) -> str:
        """
        Removes bracketed information that typically appears at the beginning of a transcript.
        This is designed to be non-greedy and only affect the start of the text.
        """
        if not text:
            return ""
        # This will remove a single occurrence of a bracketed phrase at the start of the string.
        return TextCleaner.BRACKET_INFO_PATTERN.sub('', text)

    @staticmethod
    def clean_text(
        text: str,
        remove_html: bool = True,
        remove_brackets: bool = True,
        normalize_chars: bool = True
    ) -> str:
        """
        Applies a full cleaning pipeline to the input text.

        Args:
            text: The string to clean.
            remove_html: Whether to remove HTML tags and entities.
            remove_brackets: Whether to remove initial bracketed session info.
            normalize_chars: Whether to normalize unicode characters.

        Returns:
            The cleaned and normalized text.
        """
        if not text:
            return ""

        if remove_html:
            text = TextCleaner.remove_html_tags(text)
        
        if remove_brackets:
            text = TextCleaner.remove_session_brackets(text)

        if normalize_chars:
            text = TextCleaner.normalize_polish_chars(text)

        # Replace multiple whitespace characters with a single space and strip leading/trailing whitespace
        text = TextCleaner.WHITESPACE_PATTERN.sub(' ', text).strip()

        return text
