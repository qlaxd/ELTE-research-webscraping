from typing import Any, Dict, List
from loguru import logger
import pandas as pd

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
            # agenda_item will be assigned after reordering
            new_row['agenda_item'] = None # Placeholder value
            new_rows.append(new_row)
        
        logger.info("Successfully created new rows for segmented speeches.")
        return new_rows

    @staticmethod
    def assign_agenda_items(df: pd.DataFrame) -> pd.DataFrame:
        """
        Assigns the correct 'agenda_item' to each speaker segment ('chair' == 1).

        A speaker's segment receives the 'agenda_item' of the speech that immediately
        follows it in the reconstructed order. This is done by back-filling the data.

        Args:
            df: The session DataFrame, already sorted in the correct chronological order.

        Returns:
            The DataFrame with the 'agenda_item' column correctly populated for speaker segments.
        """
        logger.info("Assigning agenda items to speaker segments...")
        
        # Create a boolean mask for the speaker rows
        is_speaker_row = df['chair'] == 1
        
        # Temporarily set agenda_item to NaN for speaker rows to allow backfilling
        # This ensures that only speaker rows get modified
        df.loc[is_speaker_row, 'agenda_item'] = None
        
        # Backfill the NaN values from the next valid observation in the column
        df['agenda_item'] = df['agenda_item'].bfill()
        
        logger.info("Finished assigning agenda items.")
        return df
