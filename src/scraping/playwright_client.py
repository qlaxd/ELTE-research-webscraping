import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext, Playwright, Error
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class PlaywrightClient:
    """
    A persistent web client using Playwright with a persistent browser context
    to maintain sessions and cookies across runs.
    """

    def __init__(self, headless: bool = False, timeout: int = 60000):
        """
        Initializes the PlaywrightClient.

        Args:
            headless: Whether to run the browser in headless mode.
            timeout: The default navigation timeout in milliseconds.
        """
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.headless = headless
        self.timeout = timeout
        
        self.user_data_dir = Path('data/browser_context')
        self.user_data_dir.mkdir(exist_ok=True)
        
        self.debug_dir = Path('data/debug')
        self.debug_dir.mkdir(exist_ok=True)

    def start(self):
        """Initializes Playwright and launches a persistent browser context."""
        if self.context:
            logger.warning("A browser context is already running.")
            return
        try:
            logger.info(f"Initializing Playwright and launching persistent context from: {self.user_data_dir}")
            self.playwright = sync_playwright().start()
            self.context = self.playwright.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            logger.info("Persistent browser context launched successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright persistent context: {e}")
            self.close()
            raise

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetches content from a URL, handling CAPTCHAs and different page load states intelligently.
        It checks for multiple possible content selectors before deciding if a page has loaded successfully.
        """
        if not self.page:
            logger.error("Browser page not started. Call start() before fetching.")
            return None

        try:
            logger.info(f"Navigating to URL: {url}")
            self.page.goto(url, wait_until='domcontentloaded')

            # First, check for an explicit CAPTCHA page
            page_content_for_captcha_check = self.page.content()
            captcha_signature = "This question is for testing whether you are a human visitor"
            if captcha_signature in page_content_for_captcha_check:
                logger.warning("Definitive CAPTCHA page detected. Pausing for user intervention.")
                self._handle_captcha_or_error(url, "Real CAPTCHA detected.")
                return self.page.content()

            # If no immediate CAPTCHA, wait for one of the potential success selectors
            potential_selectors = [
                'div.stenogram', # Added for modern layouts (Sejm7 onwards)
                'body > blockquote:nth-of-type(2)',
                'body > div > blockquote',
                'body > blockquote'
            ]
            
            success = False
            for selector in potential_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000) # 10s timeout for each selector
                    logger.info(f"Success selector '{selector}' found. Page loaded correctly.")
                    success = True
                    break # Found a valid selector, no need to check others
                except Error:
                    logger.debug(f"Selector '{selector}' not found, trying next one.")
                    continue

            if success:
                return self.page.content()
            else:
                logger.warning(f"None of the potential success selectors {potential_selectors} were found, and no CAPTCHA was detected. "
                             f"The page might have an unsupported layout or was too slow to load. Skipping.")
                self._save_debug_page(url, "no_selector_found")
                return None

        except Error as e:
            logger.error(f"A critical error occurred during Playwright navigation for {url}: {e}")
            self._save_debug_page(url, "critical_error")
            return None

    def _save_debug_page(self, url: str, suffix: str):
        """Saves the current page content for debugging."""
        try:
            debug_content = self.page.content()
            sanitized_url = re.sub(r'[^a-zA-Z0-9_-]', '_', url)
            debug_filepath = self.debug_dir / f"{suffix}_{sanitized_url[:100]}.html"
            with open(debug_filepath, 'w', encoding='utf-8') as f:
                f.write(debug_content)
            logger.info(f"The current page HTML has been saved to: {debug_filepath}")
        except Exception as e:
            logger.error(f"Failed to save debug page: {e}")

    def _handle_captcha_or_error(self, url: str, reason: str):
        """Saves debug info and pauses the script for manual user intervention."""
        self._save_debug_page(url, "captcha_or_error")
        
        print("\n" + "="*60)
        print(f"ACTION REQUIRED: {reason}")
        print(f"Please solve the CAPTCHA or resolve the issue in the browser window for URL: {url}")
        print("The script will wait indefinitely. Press Enter in this console when you are done...")
        print("="*60)
        
        input()
        logger.info("Resuming script after manual intervention.")

    def close(self):
        """Closes the browser context and stops the Playwright instance."""
        if self.context:
            logger.info("Closing the browser context.")
            self.context.close()
            self.context = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        logger.info("Playwright client shut down.")
