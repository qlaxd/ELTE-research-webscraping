from loguru import logger
from typing import Union, Optional, Iterator, List, Callable
from pathlib import Path
import pandas as pd

class CSVHandler:
    """Handles reading and writing CSV files with support for chunking and validation."""

    def __init__(self, encoding: str = 'utf-8', delimiter: str = ','):
        """
        Initializes the CSVHandler.

        Args:
            encoding: The character encoding to use.
            delimiter: The delimiter for the CSV file.
        """
        self.encoding = encoding
        self.delimiter = delimiter

    def read_csv(self, filepath: Path, chunksize: Optional[int] = None) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
        """
        Reads a CSV file into a pandas DataFrame or an iterator of DataFrames.

        Args:
            filepath: The path to the CSV file.
            chunksize: If specified, returns an iterator of DataFrames of this size.

        Returns:
            A DataFrame or an iterator of DataFrames.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            UnicodeDecodeError: If the file cannot be decoded with the specified encoding.
        """
        logger.info(f"Reading CSV file from: {filepath}")
        try:
            reader = pd.read_csv(
                filepath,
                encoding=self.encoding,
                delimiter=self.delimiter,
                chunksize=chunksize,
                on_bad_lines='warn'
            )
            if chunksize:
                logger.info(f"Reading in chunks of size {chunksize}.")
                return reader

            # If not chunking, read the whole file to log row count
            df = reader
            logger.info(f"Successfully read {len(df)} rows from {filepath}.")
            return df
        except FileNotFoundError:
            logger.error(f"File not found at path: {filepath}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while reading {filepath}: {e}")
            raise

    def write_csv(self, df: pd.DataFrame, filepath: Path, index: bool = False) -> None:
        """
        Writes a DataFrame to a CSV file.

        Args:
            df: The DataFrame to write.
            filepath: The path to the output CSV file.
            index: Whether to write the DataFrame index as a column.
        """
        logger.info(f"Writing {len(df)} rows to CSV file: {filepath}")
        try:
            # Ensure the parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(filepath, encoding=self.encoding, sep=self.delimiter, index=index)
            logger.info("Successfully wrote to CSV.")
        except IOError as e:
            logger.error(f"Could not write to file {filepath}: {e}")
            raise

    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validates that the DataFrame contains all required columns.

        Args:
            df: The DataFrame to validate.
            required_columns: A list of column names that must be present.

        Returns:
            True if all required columns are present.

        Raises:
            ValueError: If any required columns are missing.
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            msg = f"Missing required columns in DataFrame: {sorted(list(missing_columns))}"
            logger.error(msg)
            raise ValueError(msg)
        
        logger.debug("All required columns are present.")
        return True

    def process_in_chunks(self, filepath: Path, chunk_processor: Callable[[pd.DataFrame], pd.DataFrame], chunksize: int = 1000) -> pd.DataFrame:
        """
        Reads a large CSV file in chunks, processes each chunk, and concatenates the results.

        Args:
            filepath: The path to the input CSV file.
            chunk_processor: A function to apply to each DataFrame chunk.
            chunksize: The number of rows per chunk.

        Returns:
            A single DataFrame containing the processed and concatenated results.
        """
        logger.info(f"Processing {filepath} in chunks of {chunksize}...")
        results = []
        chunk_iterator = self.read_csv(filepath, chunksize=chunksize)
        
        for i, chunk in enumerate(chunk_iterator):
            logger.debug(f"Processing chunk {i+1}...")
            processed_chunk = chunk_processor(chunk)
            results.append(processed_chunk)
        
        if not results:
            logger.warning("No data was processed or returned from chunks.")
            return pd.DataFrame()

        logger.info("Concatenating processed chunks...")
        combined_df = pd.concat(results, ignore_index=True)
        logger.info(f"Finished processing. Total rows in combined DataFrame: {len(combined_df)}")
        return combined_df
