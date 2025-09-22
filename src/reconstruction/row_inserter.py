import logging
import pandas as pd
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """Normalizes text for comparison by lowercasing, removing punctuation, and extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\w\s-]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip().lower()

def find_matching_speech_index(analyzed_link: Dict[str, str], speeches_df: pd.DataFrame) -> Optional[int]:
    """
    Finds the index of the best matching speech in the DataFrame based on analyzed link data.
    This implementation uses a more robust word-set matching strategy.

    Args:
        analyzed_link: A dictionary containing the analyzed link info, including 'speaker_name'.
        speeches_df: DataFrame of speeches to search through.

    Returns:
        The index of the first matching speech, or None if no match is found.
    """
    link_speaker_name = normalize_text(analyzed_link.get('speaker_name', ''))
    if not link_speaker_name:
        logger.warning(f"Link has no speaker name to match: {analyzed_link}")
        return None

    link_name_words = set(link_speaker_name.split())

    # --- Strategy 1: Word set comparison for speaker names ---
    # This is robust against name order differences (e.g., "Jan Kowalski" vs. "Kowalski Jan").
    for index, speech in speeches_df.iterrows():
        speech_speaker_name = normalize_text(speech.get('speaker', ''))
        if speech_speaker_name:
            speech_name_words = set(speech_speaker_name.split())
            if link_name_words == speech_name_words:
                logger.debug(f"Found word-set speaker match for '{link_speaker_name}' at index {index}.")
                return index

    # --- Strategy 2: Fallback to checking if link speaker name is a subset of the agenda_item ---
    for index, speech in speeches_df.iterrows():
        agenda_item_text = normalize_text(speech.get('agenda_item', ''))
        if agenda_item_text and link_name_words.issubset(set(agenda_item_text.split())):
            logger.debug(f"Found fallback subset match for '{link_speaker_name}' in agenda_item at index {index}.")
            return index

    logger.warning(f"Could not find any match for speaker '{link_speaker_name}'. Available speakers: {speeches_df['speaker'].unique().tolist()}")
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

        reconstructed_rows.append(new_rows[0])

        for i, link in enumerate(analyzed_links):
            match_index = find_matching_speech_index(link, remaining_speeches)
            
            if match_index is not None:
                reconstructed_rows.append(remaining_speeches.loc[match_index].to_dict())
                remaining_speeches.drop(match_index, inplace=True)
            else:
                logger.warning(f"Could not find a matching speech for link: {link}")

            if (i + 1) < len(new_rows):
                reconstructed_rows.append(new_rows[i + 1])

        if not remaining_speeches.empty:
            logger.warning(
                f"Found {len(remaining_speeches)} non-speaker speeches that were not matched to any link. "
                f"Appending them to the end to avoid data loss."
            )
            reconstructed_rows.extend(remaining_speeches.to_dict('records'))

        if not reconstructed_rows:
            logger.error("Reconstruction resulted in an empty list of rows. This should not happen.")
            return pd.DataFrame()

        final_df = pd.DataFrame(reconstructed_rows)
        logger.info(f"Reconstruction complete. New session has {len(final_df)} rows.")
        
        return final_df
