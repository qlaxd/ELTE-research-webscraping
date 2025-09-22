import time
from loguru import logger

class WebClient:
    """A robust HTTP client for scraping web pages with session management, retries, and rate limiting."""

    def __init__(
        self,
        user_agent: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        rate_limit_delay: float = 0.5
    ):
        """
        Initializes the WebClient.

        Args:
            user_agent: The User-Agent string to use for requests.
            timeout: The timeout in seconds for requests.
            max_retries: The maximum number of retry attempts.
            backoff_factor: The backoff factor for exponential backoff between retries.
            rate_limit_delay: The minimum delay in seconds between consecutive requests.
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Set up a requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        })

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504], # Status codes to trigger a retry
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

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
        Fetches the content of a given URL.

        Args:
            url: The URL to fetch.

        Returns:
            The text content of the response, or None if the request fails.
        """
        self._apply_rate_limit()
        logger.info(f"Fetching URL: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # The response content is already decoded by requests
            logger.info(f"Successfully fetched {url}. Response size: {len(response.text)} characters.")
            return response.text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url} after multiple retries. Error: {e}")
            return None
