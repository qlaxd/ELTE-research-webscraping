from loguru import logger
import pandas as pd
from typing import List, Dict, Any, Optional
import re


def find_matching_speech_index(analyzed_link: Dict[str, str], speeches_df: pd.DataFrame) -> Optional[int]:
    """
    Finds the index of the matching speech in the DataFrame by searching for the link's
    href value within the 'source' column of the DataFrame.
    """
    link_href = analyzed_link.get('href')
    if not link_href:
        logger.warning(f"Link has no href to match: {analyzed_link}")
        return None

    # The href is usually a relative path, e.g., /Debata6.nsf/main/13E17D4D
    # We need to find the row where the 'source' column (a full URL) contains this path.
    logger.debug(f"Searching for match for href: '{link_href}'")

    # Use vectorized string operations for efficiency
    matching_rows = speeches_df[speeches_df['source'].str.contains(link_href, case=False, na=False)]

    if not matching_rows.empty:
        # If multiple rows match (e.g., duplicates in source data), take the first one
        match_index = matching_rows.index[0]
        logger.info(f"Found match for href '{link_href}' at index {match_index}.")
        return match_index

    logger.warning(f"Could not find any speech matching the href: '{link_href}'.")
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