import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, Playwright, Error

logger = logging.getLogger(__name__)

class PlaywrightClient:
    """A web client using Playwright to handle dynamic pages and CAPTCHAs."""

    def __init__(self, headless: bool = False, timeout: int = 60000):
        """
        Initializes the PlaywrightClient.

        Args:
            headless: Whether to run the browser in headless mode. Defaults to False.
            timeout: The default navigation timeout in milliseconds.
        """
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.headless = headless
        self.timeout = timeout
        self._initialize_browser()

    def _initialize_browser(self):
        """Initializes the Playwright instance and launches a persistent browser."""
        try:
            logger.info("Initializing Playwright and launching browser...")
            self.playwright = sync_playwright().start()
            # Using chromium, which is generally well-supported
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            logger.info("Browser launched successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {e}")
            if self.playwright:
                self.playwright.stop()

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetches the content of a given URL, allowing for manual CAPTCHA solving.

        Args:
            url: The URL to fetch.

        Returns:
            The page source HTML, or None if fetching fails.
        """
        if not self.browser:
            logger.error("Browser not initialized. Cannot fetch URL.")
            return None

        page = self.browser.new_page()
        try:
            logger.info(f"Navigating to URL: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)

            # Simple check for bot detection/CAPTCHA page
            page_content = page.content()
            if "TSPD" in page_content or "captcha" in page_content.lower():
                logger.warning("CAPTCHA or bot detection page detected.")
                print("\n" + "="*50)
                print("ACTION REQUIRED: A CAPTCHA has been detected.")
                print(f"Please solve the CAPTCHA in the browser window for URL: {url}")
                print("Press Enter in this console when you are done...")
                print("="*50)
                
                # Wait for user to press Enter
                input()

                # After user intervention, get the new page content
                logger.info("Resuming script. Fetching page content after CAPTCHA.")
                page_content = page.content()

            logger.info(f"Successfully fetched content for {url}.")
            return page_content

        except Error as e:
            logger.error(f"An error occurred during Playwright navigation for {url}: {e}")
            return None
        finally:
            page.close()

    def close(self):
        """Closes the browser and stops the Playwright instance."""
        if self.browser:
            logger.info("Closing the browser.")
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Playwright client shut down.")
