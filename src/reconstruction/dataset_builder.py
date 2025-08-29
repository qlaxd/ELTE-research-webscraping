import logging
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Import all necessary components from other modules
from src.scraping.playwright_client import PlaywrightClient
from src.scraping.cache_manager import CacheManager
from src.scraping.session_scraper import SessionScraper
from src.parsing.html_parser import HTMLParser
from src.parsing.speech_extractor import SpeechExtractor
from src.segmentation.metadata_manager import MetadataManager
# from .row_inserter import RowInserter # To be implemented in the next step
# from src.segmentation.order_calculator import OrderCalculator # To be used later

logger = logging.getLogger(__name__)

class DatasetBuilder:
    """Orchestrates the end-to-end process of reconstructing the dataset."""

    def __init__(self, config: dict):
        """
        Initializes the DatasetBuilder with necessary configurations.

        Args:
            config: A dictionary containing application settings from settings.yaml.
        """
        self.config = config
        self.rules_path = Path('config/scraping_rules.yaml')

        # Initialize the components needed for the pipeline
        self.playwright_client = PlaywrightClient(
            headless=self.config['scraping'].get('headless', False)
        )
        cache_manager = CacheManager(cache_dir=Path(config['paths']['cache_dir']))
        self.session_scraper = SessionScraper(self.playwright_client, cache_manager)

    def _process_session(self, session_df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes a single session to segment the speaker's speech.

        Args:
            session_df: A DataFrame containing all rows for a single session.

        Returns:
            A new DataFrame for the session with the speaker's speech segmented.
        """
        # Find the main speaker row
        speaker_rows = session_df[session_df['chair'] == 1]
        if len(speaker_rows) == 0:
            logger.warning(f"Session on date {session_df['date'].iloc[0]} has no speaker rows. Skipping.")
            return session_df # Return original if no speaker row is found

        if len(speaker_rows) > 1:
            logger.info(f"Session on date {session_df['date'].iloc[0]} has {len(speaker_rows)} speaker rows. Processing only the first one.")
        
        speaker_row = speaker_rows.iloc[0]
        
        # All other rows, including other speaker rows
        other_rows = session_df[session_df.index != speaker_row.name]

        session_url = speaker_row.get('source') # Assumes a 'source' column exists
        if not session_url or not isinstance(session_url, str):
            logger.warning(f"No valid URL found for session on {speaker_row['date']}. Skipping.")
            return session_df

        # --- Scraping and Parsing ---
        html_content = self.session_scraper.fetch_session_html(session_url)
        if not html_content:
            return session_df # Return original if scraping fails

        try:
            parser = HTMLParser(html_content, year=speaker_row['date'].year, rules_path=self.rules_path)
            content_area = parser.extract_content_area()
            if not content_area:
                return session_df

            extractor = SpeechExtractor(content_area, parser.rules)
            segments = extractor.extract_segments()
            if not segments:
                logger.warning(f"No segments extracted for session on {speaker_row['date']}. Returning original.")
                return session_df
        except Exception as e:
            logger.error(f"An error occurred during parsing/extraction for session {speaker_row['date']}: {e}")
            return session_df

        # --- Segmentation and Reconstruction ---
        metadata_manager = MetadataManager(speaker_row, segments)
        new_speaker_rows = metadata_manager.create_new_rows()

        # In the next steps, we will insert these rows and re-order.
        # For now, this method demonstrates the pipeline up to segment creation.
        logger.info("Placeholder for row insertion and re-ordering.")
        
        reconstructed_rows = pd.concat([other_rows, pd.DataFrame(new_speaker_rows)], ignore_index=True)
        
        return reconstructed_rows

    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the entire dataset by iterating through each session.

        Args:
            df: The full input DataFrame.

        Returns:
            A new DataFrame with all applicable sessions reconstructed.
        """
        logger.info("Starting dataset reconstruction process...")
        reconstructed_sessions = []
        # Group by date to process each session individually
        session_groups = df.groupby('date')

        for date, session_df in tqdm(session_groups, desc="Processing Sessions"):
            processed_session_df = self._process_session(session_df.copy())
            reconstructed_sessions.append(processed_session_df)

        if not reconstructed_sessions:
            logger.error("No sessions were processed. Returning original dataset.")
            return df

        # Combine all processed sessions into a single DataFrame
        final_df = pd.concat(reconstructed_sessions, ignore_index=True)
        logger.info("Dataset reconstruction complete.")
        return final_df
