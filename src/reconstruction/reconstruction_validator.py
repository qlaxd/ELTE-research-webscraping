from loguru import logger
import pandas as pd

class ReconstructionValidator:
    """Validates the output of the dataset reconstruction process for a single session."""

    @staticmethod
    def _check_row_count(original_df: pd.DataFrame, reconstructed_df: pd.DataFrame, num_new_segments: int) -> bool:
        """Verifies that the new row count is correct."""
        expected_rows = len(original_df[original_df['chair'] == 0]) + num_new_segments
        actual_rows = len(reconstructed_df)
        if expected_rows != actual_rows:
            logger.error(
                f"Row count mismatch. Expected: {expected_rows}, Actual: {actual_rows}."
            )
            return False
        logger.debug("Row count validation passed.")
        return True

    @staticmethod
    def _check_non_speaker_speeches_preserved(original_df: pd.DataFrame, reconstructed_df: pd.DataFrame) -> bool:
        """Ensures that all original non-speaker speeches are preserved."""
        original_non_speaker = original_df[original_df['chair'] == 0].copy()
        reconstructed_non_speaker = reconstructed_df[reconstructed_df['chair'] == 0].copy()

        # A simple way to compare is to drop columns that might be reordered/changed
        # and compare the rest. A more robust check might use a unique ID.
        # For now, we compare the number of rows and the 'text' content.
        if len(original_non_speaker) != len(reconstructed_non_speaker):
            logger.error("Number of non-speaker speeches changed during reconstruction.")
            return False

        # This check is basic. A more robust check would merge and find non-matching rows.
        if not original_non_speaker['text'].isin(reconstructed_non_speaker['text']).all():
            logger.error("Some non-speaker speeches were altered or lost.")
            return False

        logger.debug("Non-speaker speeches preservation validation passed.")
        return True

    @staticmethod
    def _check_place_agenda(reconstructed_df: pd.DataFrame) -> bool:
        """Verifies that the 'place_agenda' column is sequential and without gaps."""
        if 'place_agenda' not in reconstructed_df.columns:
            logger.error("'place_agenda' column not found in reconstructed DataFrame.")
            return False
        
        agenda = reconstructed_df['place_agenda'].sort_values().to_list()
        expected_agenda = list(range(1, len(agenda) + 1))

        if agenda != expected_agenda:
            logger.error(f"'place_agenda' is not sequential. Expected {expected_agenda}, got {agenda}.")
            return False
        
        logger.debug("'place_agenda' sequence validation passed.")
        return True

    @staticmethod
    def validate_reconstruction(
        original_session_df: pd.DataFrame,
        reconstructed_session_df: pd.DataFrame,
        num_new_segments: int
    ) -> bool:
        """
        Runs all validation checks on the reconstructed session DataFrame.

        Args:
            original_session_df: The original DataFrame for the session.
            reconstructed_session_df: The new, reconstructed DataFrame for the session.
            num_new_segments: The number of new speaker segments that were created.

        Returns:
            True if all validation checks pass, False otherwise.
        """
        logger.info(f"Running reconstruction validation for session on {original_session_df['date'].iloc[0]}...")
        
        checks = [
            ReconstructionValidator._check_row_count(original_session_df, reconstructed_session_df, num_new_segments),
            ReconstructionValidator._check_non_speaker_speeches_preserved(original_session_df, reconstructed_session_df),
            ReconstructionValidator._check_place_agenda(reconstructed_session_df)
        ]

        if all(checks):
            logger.info("Reconstruction validation passed for this session.")
            return True
        else:
            logger.error("Reconstruction validation failed for this session.")
            return False
