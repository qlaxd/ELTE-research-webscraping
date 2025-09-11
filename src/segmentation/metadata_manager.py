import logging
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

class MetadataManager:
    """Manages the creation and assignment of metadata for new speech segments."""

    def __init__(self, original_speaker_row: pd.Series, segments: List[str]):
        """
        Initializes the MetadataManager.

        Args:
            original_speaker_row: The pandas Series representing the original,
                                  concatenated speech of the Speaker (chair=1).
            segments: A list of text strings, where each string is a new speech segment.
        """
        self.original_row = original_speaker_row
        self.segments = segments

    def create_new_rows(self) -> List[Dict[str, Any]]:
        """
        Creates a list of new data rows for the speaker's segmented speeches.

        Each new row is a dictionary based on the original speaker's row, but with
        the 'text' field replaced by the new segment.

        Returns:
            A list of dictionaries, each representing a new row to be added to the DataFrame.
        """
        logger.info(f"Creating {len(self.segments)} new rows from original speaker row.")
        new_rows = []
        base_metadata = self.original_row.to_dict()

        for segment_text in self.segments:
            new_row = base_metadata.copy()
            new_row['text'] = segment_text
            # place_agenda will be recalculated later for the whole session
            new_row['place_agenda'] = -1 # Placeholder value
            # agenda_item will be assigned in the next step
            new_row['agenda_item'] = None # Placeholder value
            new_rows.append(new_row)
        
        logger.info("Successfully created new rows for segmented speeches.")
        return new_rows

    @staticmethod
    def assign_agenda_items(new_rows: List[Dict[str, Any]], session_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Assigns the correct 'agenda_item' to each new speaker segment.

        According to the task, the speaker's segment should take the agenda_item
        of the speech that follows it.

        Args:
            new_rows: The list of newly created speaker rows (as dictionaries).
            session_df: The original DataFrame of the session, used to find the next speech.

        Returns:
            The list of new rows with the 'agenda_item' field correctly populated.
        """
        logger.info("Assigning agenda items to new segments...")
        original_indices = session_df.index

        for i, new_row in enumerate(new_rows):
            # Find the position where the new row would be inserted.
            # This logic assumes the new rows are to be inserted at the position of the original speaker row.
            # A more sophisticated approach in the reconstruction phase will handle the exact ordering.
            # For now, we find the next speech in the original dataframe.
            original_row_index = new_rows[i-1]['original_index'] if i > 0 else new_rows[0]['original_index'] # This needs to be improved
            # This is a placeholder logic. The actual insertion and agenda assignment will be more complex.
            # A simpler approach for now: all segments get the agenda item of the first non-chair speech.
            
            first_non_chair_speech = session_df[session_df['chair'] == 0].iloc[0]
            if first_non_chair_speech is not None:
                new_row['agenda_item'] = first_non_chair_speech['agenda_item']

        # This is a simplified placeholder. The final logic will be in the reconstruction phase,
        # where the exact position of each segment is known.
        logger.warning("'assign_agenda_items' is using placeholder logic. Final implementation will be in the reconstruction phase.")
        
        return new_rows
