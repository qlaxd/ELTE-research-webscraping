from loguru import logger
import pandas as pd
from typing import List, Dict, Any, Optional
import re


def normalize_text(text: str) -> str:
    """Normalizes text for comparison by lowercasing, removing non-alphanumeric characters, and extra whitespace."""
    if not isinstance(text, str):
        return ""
    # Aggressively remove anything that is not a word character or space
    text = re.sub(r'[\W_]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip().lower()

def find_matching_speech_index(analyzed_link: Dict[str, str], speeches_df: pd.DataFrame) -> Optional[int]:
    """
    Finds the index of the best matching speech in the DataFrame by comparing the full link text
    against the combined speaker and speaker_type info from the DataFrame.
    """
    # Use the full original link text for a more reliable match
    link_text_original = analyzed_link.get('text', '')
    link_text_full = normalize_text(link_text_original)
    if not link_text_full:
        logger.warning(f"Link has no text to match: {analyzed_link}")
        return None

    logger.debug(f"--- Searching for match for link: '{link_text_original}' (normalized: '{link_text_full}') ---")
    link_words = set(link_text_full.split())

    best_match_score = 0
    best_match_index = None

    for index, speech in speeches_df.iterrows():
        # Combine speaker_type and speaker name from the dataframe for a comprehensive source text
        speech_speaker_info_original = f"{speech.get('speaker_type', '')} {speech.get('speaker', '')}"
        speech_info_normalized = normalize_text(speech_speaker_info_original)
        
        if speech_info_normalized:
            speech_words = set(speech_info_normalized.split())
            
            # Calculate Jaccard similarity as a matching score
            intersection_score = len(link_words.intersection(speech_words))
            union_size = len(link_words.union(speech_words))
            jaccard_score = intersection_score / union_size if union_size > 0 else 0
            
            logger.debug(f"Comparing with row index {index}: '{speech_info_normalized}'. Jaccard score: {jaccard_score:.2f}")

            if jaccard_score > best_match_score:
                best_match_score = jaccard_score
                best_match_index = index

    # Set a threshold for matching
    MATCH_THRESHOLD = 0.5 
    if best_match_index is not None and best_match_score >= MATCH_THRESHOLD:
        matched_speech_info = normalize_text(f"{speeches_df.loc[best_match_index].get('speaker_type', '')} {speeches_df.loc[best_match_index].get('speaker', '')}")
        logger.info(f"Found best match for link '{link_text_full}' at index {best_match_index} ('{matched_speech_info}') with score {best_match_score:.2f}.")
        return best_match_index

    logger.warning(f"Could not find any suitable match for link text '{link_text_full}' (best score: {best_match_score:.2f}, threshold: {MATCH_THRESHOLD}).")
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