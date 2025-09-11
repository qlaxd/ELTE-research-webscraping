import logging
import pandas as pd

logger = logging.getLogger(__name__)

class OrderCalculator:
    """Handles the recalculation of position-dependent fields like 'place_agenda'."""

    @staticmethod
    def recalculate_place_agenda(session_df: pd.DataFrame) -> pd.DataFrame:
        """
        Recalculates the 'place_agenda' column for a given session DataFrame.

        This method assumes that the DataFrame is already sorted in the correct
        chronological order of speeches. It will then assign a new, sequential
        'place_agenda' value (starting from 1) to each row.

        Args:
            session_df: A DataFrame representing a single session, with rows sorted
                        in the final desired order.

        Returns:
            The DataFrame with the 'place_agenda' column updated.
        """
        if 'place_agenda' not in session_df.columns:
            logger.warning("'place_agenda' column not found. Creating it.")
            session_df['place_agenda'] = 0

        logger.info(f"Recalculating 'place_agenda' for {len(session_df)} rows.")

        # Resetting the index is crucial to ensure sequential ordering after any
        # previous manipulations (like row insertions or deletions).
        df_reset = session_df.reset_index(drop=True)

        # The new place_agenda is the new index + 1
        df_reset['place_agenda'] = df_reset.index + 1

        logger.info("'place_agenda' column has been successfully recalculated.")
        return df_reset
