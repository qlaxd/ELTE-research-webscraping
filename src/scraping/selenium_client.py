from loguru import logger

class SeleniumClient:
    """A web client using undetected-chromedriver to bypass bot detection."""

    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initializes the SeleniumClient.

        Args:
            rate_limit_delay: Minimum delay in seconds between requests.
        """
        self.driver = None
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self._initialize_driver()

    def _initialize_driver(self):
        """Initializes the Chrome driver."""
        try:
            logger.info("Initializing undetected-chromedriver...")
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # You might need to adjust the version_main parameter based on your installed Chrome version
            self.driver = uc.Chrome(options=options)
            logger.info("ChromeDriver initialized successfully.")
        except WebDriverException as e:
            logger.error(f"Failed to initialize ChromeDriver: {e}")
            self.driver = None

    def _apply_rate_limit(self):
        """Ensures that requests do not exceed the defined rate limit."""
        elapsed_time = time.time() - self.last_request_time
        if elapsed_time < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed_time
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetches the content of a given URL using Selenium.

        Args:
            url: The URL to fetch.

        Returns:
            The page source HTML, or None if the request fails.
        """
        if not self.driver:
            logger.error("Driver not initialized. Cannot fetch URL.")
            return None

        self._apply_rate_limit()
        logger.info(f"Fetching URL with Selenium: {url}")

        try:
            self.driver.get(url)
            # It's good practice to wait for a moment to let JS challenges run
            time.sleep(5) 
            
            content = self.driver.page_source
            logger.info(f"Successfully fetched {url}. Page size: {len(content)} characters.")
            
            # Check if we got the threat detection page
            if "TSPD_101" in content or "Threat Detection" in content:
                logger.warning(f"Bot detection page was returned for {url}.")
                # Optionally, you could add more sophisticated handling here,
                # like solving a CAPTCHA if one appears.
                return None

            return content
        
        except WebDriverException as e:
            logger.error(f"Failed to fetch {url} with Selenium. Error: {e}")
            return None

    def close(self):
        """Closes the browser and quits the driver."""
        if self.driver:
            logger.info("Closing the browser.")
            self.driver.quit()
            self.driver = None
