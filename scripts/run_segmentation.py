#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the project root to the Python path to allow imports from 'src'
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.main import run_pipeline

def main():
    """The main entry point for the command-line script."""
    print("Starting the segmentation pipeline...")
    try:
        run_pipeline()
        print("Pipeline finished. Check logs for details.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # The logger in the pipeline should have already captured the details.
        sys.exit(1)

if __name__ == "__main__":
    main()
