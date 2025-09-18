import pandas as pd
import re
import os
from dotenv import load_dotenv

def __main__():
    """
    Main function to process speeches.
    
    This function reads environment variables for input/output paths and chunk size,
    then processes speech data from a CSV file in chunks. The processing is done
    iteratively to handle large datasets efficiently while managing memory usage.

    Environment variables required:
        INPUT_CSV_PATH: Path to the input CSV file containing speech data
        OUTPUT_CSV_PATH: Path where the processed data will be saved
        CHUNK_SIZE: Number of rows to process at a time
    """
    
    load_dotenv()

    INPUT_CSV_PATH = os.getenv("INPUT_CSV_PATH")
    OUTPUT_CSV_PATH = os.getenv("OUTPUT_CSV_PATH")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))

    csv_iterator = pd.read_csv(INPUT_CSV_PATH, chunksize=CHUNK_SIZE)