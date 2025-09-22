from loguru import logger

class DataValidator:
    """Validates the structure and content of the input DataFrame."""

    def __init__(self):
        self.errors: List[str] = []
        self.required_columns = [
            'text', 'speaker_name', 'chair', 'agenda_item', 'place_agenda', 'date'
        ]
        # Regex for YYYY.MM.DD format
        self.date_format_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')

    def validate_required_columns(self, df: pd.DataFrame) -> bool:
        """Checks if all required columns are present in the DataFrame."""
        is_valid = True
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            error_msg = f"Missing required columns: {sorted(list(missing_columns))}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            is_valid = False
        return is_valid

    def validate_data_types(self, df: pd.DataFrame) -> bool:
        """Validates the data types and formats of key columns."""
        is_valid = True
        # Check 'chair' column for binary values
        if 'chair' in df.columns and not df['chair'].isin([0, 1]).all():
            error_msg = "Column 'chair' contains values other than 0 or 1."
            self.errors.append(error_msg)
            logger.warning(error_msg)
            is_valid = False

        # Check 'place_agenda' for positive integers
        if 'place_agenda' in df.columns and not (df['place_agenda'] > 0).all():
            error_msg = "Column 'place_agenda' contains non-positive integers."
            self.errors.append(error_msg)
            logger.warning(error_msg)
            is_valid = False

        # Check 'date' column format
        if 'date' in df.columns and not df['date'].astype(str).str.match(self.date_format_pattern).all():
            error_msg = f"Column 'date' has entries that do not match the format YYYY.MM.DD."
            self.errors.append(error_msg)
            logger.warning(error_msg)
            is_valid = False
            
        return is_valid

    def validate_chair_speeches(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Validates that each session (grouped by date) has exactly one chair speech to be processed.
        
        Returns:
            A dictionary with session dates as keys and validation status as values.
        """
        validation_results = {}
        if 'date' not in df.columns or 'chair' not in df.columns:
            logger.warning("Cannot validate chair speeches because 'date' or 'chair' column is missing.")
            return validation_results

        for date, group in df.groupby('date'):
            chair_speech_count = group['chair'].sum()
            if chair_speech_count == 0:
                status = f"Session on date {date} has no chair speech (chair=1)."
                logger.warning(status)
                validation_results[date] = status
            elif chair_speech_count > 1:
                status = f"Session on date {date} has {chair_speech_count} chair speeches. Expected 1."
                logger.warning(status)
                validation_results[date] = status
        return validation_results

    def validate_all(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Runs all validation checks on the DataFrame.

        Args:
            df: The DataFrame to validate.

        Returns:
            A tuple containing a boolean (True if valid) and a list of all error messages.
        """
        self.errors = []  # Reset errors for a fresh validation run
        
        # Run all validation methods
        columns_valid = self.validate_required_columns(df)
        types_valid = self.validate_data_types(df)
        self.validate_chair_speeches(df) # This method adds warnings to logs, not blocking errors to self.errors

        is_valid = columns_valid and types_valid

        if self.errors:
            logger.error(f"Validation failed with {len(self.errors)} errors.")
        else:
            logger.info("Validation successful. No critical errors found.")

        return is_valid, self.errors
