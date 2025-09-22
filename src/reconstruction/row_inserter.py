from loguru import logger
import pandas as pd
from typing import List, Dict, Any, Optional
import re


def normalize_text(text: str) -> str:
    """Normalizes text for comparison by lowercasing, removing non-alphanumeric characters, and extra whitespace."""
    if not isinstance(text, str):
        return ""
    # Aggressively remove punctuation and extra whitespace, then lowercase
    text = re.sub(r'[\W_]+', ' ', text)
    return text.strip().lower()

def find_matching_speech_index(analyzed_link: Dict[str, str], speeches_df: pd.DataFrame) -> Optional[int]:
    """
    Finds the index of the matching speech by attempting several strategies in order:
    1. For modern links, match the href against the source URL.
    2. For older links, fall back to content-based matching using normalized text
       against the 'agenda_item' or 'speaker' + 'speaker_type' columns.
    """
    link_href = analyzed_link.get('href', '')
    link_text_normalized = normalize_text(analyzed_link.get('text', ''))

    if not link_href and not link_text_normalized:
        logger.warning(f"Link has no href or text to match: {analyzed_link}")
        return None

    logger.debug(f"Attempting to match link: {analyzed_link.get('text')}")

    # --- Strategy 1: Modern Link href Match (fast and reliable) ---
    if 'wypowiedz.xsp' in link_href:
        matching_rows = speeches_df[speeches_df['source'].str.contains(link_href, case=False, na=False)]
        if not matching_rows.empty:
            match_index = matching_rows.index[0]
            logger.info(f"Found match for modern href '{link_href}' at index {match_index}.")
            return match_index

    # --- Strategy 2: Content-based matching for older links ---
    
    # Create a normalized text column from 'agenda_item' for comparison
    # This is often the most reliable source for older entries
    speeches_df['norm_agenda_item'] = speeches_df['agenda_item'].apply(normalize_text)
    
    # Create a combined normalized column from speaker and speaker_type
    speeches_df['norm_speaker_info'] = (speeches_df['speaker_type'].fillna('') + ' ' + speeches_df['speaker'].fillna('')).apply(normalize_text)

    # 2a: Try to find an exact match in agenda_item
    exact_agenda_match = speeches_df[speeches_df['norm_agenda_item'] == link_text_normalized]
    if not exact_agenda_match.empty:
        match_index = exact_agenda_match.index[0]
        logger.info(f"Found exact content match in 'agenda_item' for '{link_text_normalized}' at index {match_index}.")
        return match_index

    # 2b: Try to find an exact match in speaker_info
    exact_speaker_match = speeches_df[speeches_df['norm_speaker_info'] == link_text_normalized]
    if not exact_speaker_match.empty:
        match_index = exact_speaker_match.index[0]
        logger.info(f"Found exact content match in 'speaker_info' for '{link_text_normalized}' at index {match_index}.")
        return match_index
        
    # 2c: Fallback to substring contains check (less strict)
    substring_agenda_match = speeches_df[speeches_df['norm_agenda_item'].str.contains(link_text_normalized, na=False)]
    if not substring_agenda_match.empty:
        match_index = substring_agenda_match.index[0]
        logger.info(f"Found substring content match in 'agenda_item' for '{link_text_normalized}' at index {match_index}.")
        return match_index

    logger.warning(f"Could not find any suitable match for link: {analyzed_link.get('text')}")
    return None

class RowInserter:
    """Handles the logic of inserting new rows into a session DataFrame in the correct order."""

    @staticmethod
    def insert_rows(session_df: pd.DataFrame, new_rows: List[Dict[str, Any]], analyzed_links: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Inserts new speaker segments into the session DataFrame at their correct positions.
        """
        if not new_rows:
            logger.warning("No new speaker rows to insert.")
            return session_df

        logger.info(f"Inserting {len(new_rows) - 1} speaker segments among {len(session_df)} non-speaker rows.")

        if session_df.empty:
            logger.info("No other speeches in this session. Returning only the speaker's segments.")
            return pd.DataFrame(new_rows)

        reconstructed_rows: List[Dict[str, Any]] = []
        remaining_speeches = session_df.copy()

        # The first segment of the speaker's speech always comes first
        reconstructed_rows.append(new_rows[0])

        # Iterate through the links to place the existing speeches and subsequent speaker segments
        for i, link in enumerate(analyzed_links):
            match_index = find_matching_speech_index(link, remaining_speeches)
            
            if match_index is not None:
                # Append the matched speech
                reconstructed_rows.append(remaining_speeches.loc[match_index].to_dict())
                # Remove the matched speech so it's not considered again
                remaining_speeches.drop(match_index, inplace=True)
            else:
                # This is a critical issue if a link doesn't have a corresponding speech
                logger.warning(f"Could not find a matching speech for link: {link}")

            # Append the next speaker segment that follows this link
            if (i + 1) < len(new_rows):
                reconstructed_rows.append(new_rows[i + 1])

        # If any non-speaker speeches were not matched, append them to the end to avoid data loss
        if not remaining_speeches.empty:
            logger.warning(
                f"Found {len(remaining_speeches)} non-speaker speeches that were not matched to any link. "
                f"Appending them to the end to avoid data loss."
            )
            reconstructed_rows.extend(remaining_speeches.to_dict('records'))

        if not reconstructed_rows:
            logger.error("Reconstruction resulted in an empty list of rows. This should not happen.")
            return pd.DataFrame()

        # Convert the list of dictionaries back to a DataFrame
        final_df = pd.DataFrame(reconstructed_rows)
        logger.info(f"Reconstruction complete. New session has {len(final_df)} rows.")
        
        return final_df