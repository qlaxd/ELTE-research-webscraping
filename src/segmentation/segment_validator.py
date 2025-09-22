from loguru import logger

class SegmentValidator:
    """Provides validation methods for the segmentation process."""

    REQUIRED_METADATA_KEYS = [
        'text', 'speaker_name', 'chair', 'date', 'session_id'
    ]

    @staticmethod
    def validate_metadata(new_rows: List[Dict[str, Any]]) -> bool:
        """
        Validates that all newly created rows have the required metadata keys.

        Args:
            new_rows: A list of dictionaries, where each dictionary is a new row.

        Returns:
            True if all rows are valid, False otherwise.
        """
        is_valid = True
        if not new_rows:
            logger.warning("Metadata validation called on an empty list of new rows.")
            return True

        for i, row in enumerate(new_rows):
            missing_keys = set(SegmentValidator.REQUIRED_METADATA_KEYS) - set(row.keys())
            if missing_keys:
                logger.error(f"Row {i} is missing required metadata keys: {missing_keys}")
                is_valid = False
        
        if is_valid:
            logger.info("Metadata validation passed for all new rows.")
        
        return is_valid

    @staticmethod
    def check_for_duplicate_segments(segments: List[str]) -> List[str]:
        """
        Checks for and logs any duplicate text segments.

        Args:
            segments: A list of extracted speech text segments.

        Returns:
            A list of the duplicate segments that were found.
        """
        if not segments:
            return []

        counts = Counter(segments)
        duplicates = [item for item, count in counts.items() if count > 1]

        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate segments. This may indicate a parsing error.")
            for dup in duplicates:
                logger.debug(f"Duplicate segment: {dup[:100]}...")
        else:
            logger.info("No duplicate segments found.")
            
        return duplicates
