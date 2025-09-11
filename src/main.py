import logging
from pathlib import Path
import pandas as pd

from src.utils.config_loader import load_config
from src.utils.logger import setup_logging
from src.data.csv_handler import CSVHandler
from src.reconstruction.dataset_builder import DatasetBuilder

# It's good practice to have a dedicated logger for the main script
logger = logging.getLogger(__name__)

def run_pipeline():
    """Executes the end-to-end segmentation and reconstruction pipeline."""
    # --- 1. Configuration and Setup ---
    config_path = Path('config/settings.yaml')
    config = load_config(config_path)

    log_dir = Path(config['paths']['log_dir'])
    setup_logging(log_dir=log_dir, log_level="INFO")

    logger.info("--- Starting Polish Parliament Speech Segmentation Pipeline ---")

    # Define input and output paths
    input_dir = Path(config['paths']['input_dir'])
    output_dir = Path(config['paths']['output_dir'])
    input_filepath = input_dir / 'Szejm_0731_1.csv' # Assuming this is the main input file
    output_filepath = output_dir / 'Szejm_0731_1_segmented.csv'

    # --- 2. Read Input Data ---
    csv_handler = CSVHandler()
    try:
        # For now, we assume the file is small enough to be read into memory.
        # For larger files, chunking would be necessary here.
        input_df = csv_handler.read_csv(input_filepath)
        input_df = input_df.rename(columns={'date_presented': 'date'})
        # Convert date column to datetime objects for processing
        input_df['date'] = pd.to_datetime(input_df['date'], format='mixed')
    except (FileNotFoundError, ValueError) as e:
        logger.exception(f"Failed to read or parse the input CSV file. Pipeline aborted. Error: {e}")
        return

    # --- 3. Process and Reconstruct Dataset ---
    try:
        dataset_builder = DatasetBuilder(config)
        reconstructed_df = dataset_builder.process_dataset(input_df)
    except Exception as e:
        logger.exception(f"An unexpected error occurred during dataset reconstruction. Pipeline aborted. Error: {e}")
        return

    # --- 4. Save Output Data ---
    if reconstructed_df is not None and not reconstructed_df.empty:
        logger.info(f"Saving reconstructed dataset to: {output_filepath}")
        # Convert datetime back to string for consistent CSV format
        reconstructed_df['date'] = reconstructed_df['date'].dt.strftime('%Y-%m-%d')
        csv_handler.write_csv(reconstructed_df, output_filepath)
        logger.info("--- Pipeline finished successfully! ---")
    else:
        logger.error("Reconstruction resulted in an empty or invalid dataset. No output file was saved.")

if __name__ == "__main__":
    run_pipeline()
