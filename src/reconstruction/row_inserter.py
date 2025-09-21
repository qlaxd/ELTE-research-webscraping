import logging
import pandas as pd
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RowInserter:
    """Handles the logic of inserting new rows into a session DataFrame in the correct order."""

    @staticmethod
    def insert_rows(session_df: pd.DataFrame, new_rows: List[Dict[str, Any]], links: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Inserts new speaker segments into the session DataFrame at their correct positions.

        The order is determined by the sequence of hyperlinks found in the original transcript.
        A speaker's segment is placed before the speech that its subsequent link points to.

        Args:
            session_df: The original DataFrame for the session, containing only non-speaker rows.
            new_rows: A list of dictionaries, each representing a new speaker segment row.
            links: The list of hyperlinks extracted from the transcript, which dictate the order.

        Returns:
            A new DataFrame with all rows (original and new) sorted in the correct order.
        """
        logger.info(f"Inserting {len(new_rows)} speaker segments among {len(session_df)} non-speaker rows.")

        # 1. Create a lookup map from the unique part of the URL to the row itself.
        # The hrefs in links can be relative, so we create a map that is easy to search.
        speech_map = {row['source']: row for _, row in session_df.iterrows()}
        
        placed_sources = set()
        reconstructed_rows = []

        # 2. Start with the first speaker segment (the text before the first link).
        if new_rows:
            reconstructed_rows.append(new_rows[0])

        # 3. Iterate through the links to interleave the original speeches and speaker segments.
        for i, link in enumerate(links):
            link_href = link['href']
            
            # Find the corresponding non-speaker speech in our map.
            # The link['href'] is often a relative path, so we check if it's contained in the full 'source' URL.
            matched_source = next((source for source in speech_map if link_href in source), None)

            if matched_source:
                reconstructed_rows.append(speech_map[matched_source])
                placed_sources.add(matched_source)
            else:
                logger.warning(f"Could not find a matching speech in the original dataframe for link: {link_href}")

            # Append the speaker segment that followed this link.
            if (i + 1) < len(new_rows):
                reconstructed_rows.append(new_rows[i + 1])

        # 4. Append any non-speaker speeches that were not found via the links.
        # This handles cases where the HTML might have speeches not correctly linked.
        unplaced_speeches = session_df[~session_df['source'].isin(placed_sources)]
        if not unplaced_speeches.empty:
            logger.warning(f"Found {len(unplaced_speeches)} non-speaker speeches that were not matched to any link. Appending them to the end.")
            reconstructed_rows.extend(unplaced_speeches.to_dict('records'))

        if not reconstructed_rows:
            logger.error("Reconstruction resulted in an empty list of rows.")
            return pd.DataFrame()

        # 5. Create the final DataFrame.
        final_df = pd.DataFrame(reconstructed_rows)
        logger.info(f"Reconstruction complete. New session has {len(final_df)} rows.")

        return final_df
