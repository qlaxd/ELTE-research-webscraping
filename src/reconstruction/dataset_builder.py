from loguru import logger
import pandas as pd
from src.scraping.playwright_client import PlaywrightClient
from src.scraping.session_scraper import SessionScraper
from src.scraping.cache_manager import CacheManager
from src.segmentation.order_calculator import OrderCalculator
from src.parsing.html_parser import HTMLParser
from src.parsing.speech_extractor import SpeechExtractor
from src.parsing.link_analyzer import LinkAnalyzer
from src.reconstruction.row_inserter import RowInserter
from src.segmentation.metadata_manager import MetadataManager
from src.reconstruction.reconstruction_validator import ReconstructionValidator
from pathlib import Path
from typing import Optional
from tqdm import tqdm


class DatasetBuilder:
    """Orchestrates the end-to-end process of reconstructing the dataset."""

    def __init__(self, config: dict):
        """
        Initializes the DatasetBuilder with necessary configurations.

        Args:
            config: A dictionary containing application settings from settings.yaml.
        """
        self.config = config
        project_root = Path(__file__).resolve().parent.parent.parent
        self.rules_path = project_root / 'config/scraping_rules.yaml'

        # Initialize the components needed for the pipeline
        self.playwright_client = PlaywrightClient(
            headless=self.config['scraping'].get('headless', True) # Default to headless
        )
        self.playwright_client.start() # Start the browser
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
            logger.warning(f"Session on date {session_df['date'].iloc[0].date()} has no speaker rows. Skipping.")
            logger.debug(f"Head of skipped session DataFrame:\n{session_df.head().to_string()}")
            return session_df # Return original if no speaker row is found

        if len(speaker_rows) > 1:
            logger.info(f"Session on date {session_df['date'].iloc[0].date()} has {len(speaker_rows)} speaker rows. Processing only the first one.")
        
        speaker_row = speaker_rows.iloc[0]
        
        # All other rows (non-chair)
        other_rows = session_df[session_df['chair'] == 0].copy()

        session_url = speaker_row.get('source')
        if not session_url or not isinstance(session_url, str):
            logger.warning(f"No valid URL found for session on {speaker_row['date'].date()}. Skipping.")
            return session_df

        # --- Scraping and Parsing ---
        try:
            html_content = self.session_scraper.fetch_session_html(session_url)
            if not html_content:
                return session_df

            parser = HTMLParser(html_content, year=speaker_row['date'].year, rules_path=self.rules_path)
            content_area = parser.extract_content_area()
            if not content_area:
                return session_df

            extractor = SpeechExtractor(content_area, parser.rules)
            segments = extractor.extract_segments()
            links = extractor.extract_hyperlinks()

            link_analyzer = LinkAnalyzer(links)
            analyzed_links = link_analyzer.analyze_links()

            if not segments:
                logger.warning(f"No segments extracted for session on {speaker_row['date'].date()}. Returning original.")
                return session_df
        except Exception as e:
            logger.error(f"An error occurred during parsing/extraction for session {speaker_row['date'].date()}: {e}")
            return session_df

        # --- Segmentation and Reconstruction ---
        metadata_manager = MetadataManager(speaker_row, segments)
        new_speaker_rows = metadata_manager.create_new_rows()

        reconstructed_df = RowInserter.insert_rows(other_rows, new_speaker_rows, analyzed_links)
        ordered_df = OrderCalculator.recalculate_place_agenda(reconstructed_df)
        final_session_df = MetadataManager.assign_agenda_items(ordered_df)

        # --- Final Validation ---
        is_valid = ReconstructionValidator.validate_reconstruction(
            original_session_df=session_df,
            reconstructed_session_df=final_session_df,
            num_new_segments=len(new_speaker_rows)
        )

        if not is_valid:
            logger.error(f"Reconstruction validation failed for session on {session_df['date'].iloc[0].date()}. Returning original, unprocessed data for this session.")
            return session_df

        return final_session_df

    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Groups the DataFrame by session and applies the segmentation process.
        Ensures that the Playwright client is properly closed after processing.
        """
        if 'date' not in df.columns:
            logger.error("Input DataFrame must contain a 'date' column.")
            return pd.DataFrame()

        all_reconstructed_rows = []
        try:
            # Group by date to process each session individually
            grouped = df.groupby(df['date'].dt.date)
            
            # Use tqdm for a progress bar
            for date, session_df in tqdm(grouped, desc="Processing Sessions"):
                processed_session_df = self._process_session(session_df.copy())
                if processed_session_df is not None:
                    all_reconstructed_rows.append(processed_session_df)
        
        finally:
            # Ensure the browser is closed even if an error occurs
            logger.info("Closing Playwright client...")
            self.playwright_client.close()

        if not all_reconstructed_rows:
            logger.warning("No sessions were processed or reconstructed.")
            return pd.DataFrame()

        # Concatenate all processed sessions into a single DataFrame
        final_df = pd.concat(all_reconstructed_rows, ignore_index=True)
        
        return final_df
