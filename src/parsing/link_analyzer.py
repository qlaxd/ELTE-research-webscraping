import re
from typing import List, Dict
from loguru import logger

class LinkAnalyzer:
    """Analyzes hyperlinks to extract structured data like speaker names and titles."""

    # Regex to capture a title (e.g., "Poseł", "Minister", "Sekretarz Stanu") and a name.
    # This pattern looks for a title followed by a name, which may contain spaces and hyphens.
    # It assumes the name is the last part of the string.
    SPEAKER_PATTERN = re.compile(
        r"^\s*"                           # Optional leading whitespace
        r"([\w\s\.\-]+?)"               # Non-greedy capture for the title (group 1)
        r"\s+"                             # Separator
        r"([A-ZĄĆĘŁŃÓŚŹŻ][\w\s\-ĄĆĘŁŃÓŚŹŻ]+)" # Capture for the name (group 2), assumes name starts with capital
        r"[\s\.]*$"                            # Optional trailing whitespace or period
    , re.IGNORECASE)

    def __init__(self, links: List[Dict[str, str]]):
        """
        Initializes the LinkAnalyzer.

        Args:
            links: A list of link dictionaries, each with 'text' and 'href' keys,
                   as produced by SpeechExtractor.
        """
        self.links = links

    def _extract_speaker_from_link_text(self, link_text: str) -> Dict[str, str]:
        """
        Parses a link's text to extract the speaker's title and name.

        Args:
            link_text: The text of the hyperlink.

        Returns:
            A dictionary containing the speaker's 'name' and 'title'.
        """
        logger.debug(f"Attempting to parse speaker details from link text: '{link_text}'")
        match = self.SPEAKER_PATTERN.match(link_text)
        if match:
            title = match.group(1).strip()
            name = match.group(2).strip()
            logger.debug(f"Regex matched. Group 1 (Title): '{title}', Group 2 (Name): '{name}'")
            return {'name': name, 'title': title}
        else:
            # If the regex doesn't match, we can assume the whole text is the name
            # or handle it as an unknown format.
            logger.warning(f"Could not parse speaker details from link text: '{link_text}'")
            return {'name': link_text, 'title': 'Unknown'}

    def analyze_links(self) -> List[Dict[str, str]]:
        """
        Analyzes all links and enriches them with parsed speaker information.

        Returns:
            A list of dictionaries, where each dictionary is the original link info
            updated with 'speaker_name' and 'speaker_title' keys.
        """
        logger.info(f"Analyzing {len(self.links)} links...")
        analyzed_links = []
        for link in self.links:
            speaker_info = self._extract_speaker_from_link_text(link['text'])
            analyzed_link = {
                **link, # Original href and text
                'speaker_name': speaker_info['name'],
                'speaker_title': speaker_info['title']
            }
            analyzed_links.append(analyzed_link)
        
        return analyzed_links
