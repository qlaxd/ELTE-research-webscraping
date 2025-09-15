# Refactoring Plan for the Polish Parliament Speech Segmentation Pipeline

## 1. Overview

This document outlines the necessary refactoring to address several critical issues that are preventing the successful segmentation of the Polish parliament speeches dataset. The main problem is that the scraper is being blocked by an anti-bot service on the `sejm.gov.pl` website. Additionally, there are issues with missing scraping rules for recent years and incomplete implementation of the data reconstruction logic.

## 2. Identified Issues

### 2.1. Critical: Scraping is Blocked by Anti-Bot Service

The primary issue is that the `sejm.gov.pl` website is protected by an anti-bot service (likely Incapsula). This service detects and blocks our script, returning a CAPTCHA page instead of the actual HTML content of the session pages. This causes the `HTMLParser` to fail, as it cannot find the expected content area, leading to the script skipping most of the sessions.

The current scraping logic in `src/scraping/web_client.py` uses the `requests` library, which is a simple HTTP client that cannot execute JavaScript or handle CAPTCHAs. This makes it unsuitable for scraping websites with advanced anti-bot protection.

### 2.2. Major: Missing Scraping Rules for 2012 and Onwards

The `config/scraping_rules.yaml` file only contains rules for the year range `[1991, 2011]`. The script fails with a `ValueError` when it encounters a session from 2012 or later, as it cannot find the appropriate scraping rules. The website's layout has likely changed over the years, so new rules are needed to correctly parse the HTML of more recent sessions.

### 2.3. Minor: `place_agenda` Column is Not Re-calculated

The project documentation specifies that the `place_agenda` column should be a running number by session, re-calculated after the speaker's speeches are segmented and inserted into the dataset. The current implementation in `src/reconstruction/dataset_builder.py` has a placeholder for this logic, but it is not yet implemented. The `OrderCalculator` class, which is supposed to handle this, is commented out.

## 3. Implementation Plan

### 3.1. Refactor the Scraping Logic with a Headless Browser

To bypass the anti-bot protection, the `WebClient` in `src/scraping/web_client.py` needs to be refactored to use a headless browser, such as Selenium with either ChromeDriver or GeckoDriver.

**1. Add Selenium as a dependency:**
   - Add `selenium` to your `pyproject.toml` and run `poetry install`.

**2. Refactor `src/scraping/web_client.py`:**
   - Modify the `WebClient` class to use the Selenium WebDriver.

```python
# src/scraping/web_client.py

import time
import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)

class WebClient:
    """A robust HTTP client for scraping web pages using a headless browser."""

    def __init__(
        self,
        rate_limit_delay: float = 0.5
    ):
        """
        Initializes the WebClient.

        Args:
            rate_limit_delay: The minimum delay in seconds between consecutive requests.
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

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
        Fetches the content of a given URL using a headless browser.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content of the page, or None if the request fails.
        """
        self._apply_rate_limit()
        logger.info(f"Fetching URL: {url}")

        try:
            self.driver.get(url)
            # Wait for the page to load, you might need to adjust the wait time
            time.sleep(5) 
            html = self.driver.page_source
            logger.info(f"Successfully fetched {url}. Response size: {len(html)} characters.")
            return html
        
        except WebDriverException as e:
            logger.error(f"Failed to fetch {url} with Selenium. Error: {e}")
            return None

    def close(self):
        """Closes the browser session."""
        self.driver.quit()

```

**3. Update `DatasetBuilder` to close the driver:**
   - The `DatasetBuilder` should close the `WebClient`'s browser session when it's done.

```python
# src/reconstruction/dataset_builder.py

# ... imports

class DatasetBuilder:
    def __init__(self, config: dict):
        # ...
        self.web_client = WebClient(
            rate_limit_delay=config['scraping']['rate_limit_delay']
        )
        # ...

    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        # ...
        # At the end of the method, before returning the final_df
        self.web_client.close()
        return final_df
```

### 3.2. Add Scraping Rules for 2012 and Onwards

After fixing the scraping issue, you will need to add new rules to `config/scraping_rules.yaml` for the years 2012 and onwards.

**1. Inspect the HTML of a 2012+ session page:**
   - Use the new Selenium-based scraper to download the HTML of a session page from 2012 or later.
   - Analyze the HTML to find the correct CSS selectors for the content area and the speech links.

**2. Add a new rule to `config/scraping_rules.yaml`:**
   - Add a new entry to the YAML file with the correct year range and selectors. For example:

```yaml
# config/scraping_rules.yaml

- year_range: [1991, 2011]
  selectors:
    content_container: 'td[width="100%"][valign="top"]'
    speech_link: 'a[href*="OpenDocument"]'
    speaker_block_start_pattern: 'Marszałek'

- year_range: [2012, 2023] # Adjust the end year as needed
  selectors:
    content_container: 'div.content' # Example selector, replace with the correct one
    speech_link: 'a.speech-link' # Example selector, replace with the correct one
    speaker_block_start_pattern: 'Marszałek'
```

### 3.3. Implement the `place_agenda` Re-calculation

Finally, you need to implement the logic for re-calculating the `place_agenda` column.

**1. Uncomment the `OrderCalculator` import in `src/reconstruction/dataset_builder.py`:**
   - `from src.segmentation.order_calculator import OrderCalculator`

**2. Implement the `OrderCalculator` class in `src/segmentation/order_calculator.py`:**
   - This class should take the reconstructed DataFrame and re-calculate the `place_agenda` column based on the new order of the rows.

```python
# src/segmentation/order_calculator.py

import pandas as pd

class OrderCalculator:
    """Recalculates the 'place_agenda' column for a session DataFrame."""

    def reorder(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts the DataFrame by speech order and recalculates 'place_agenda'.

        Args:
            df: The DataFrame for a single session.

        Returns:
            The DataFrame with a new 'place_agenda' column.
        """
        # Assuming there is a column that defines the order of the speeches.
        # If not, you might need to create one based on the order of the segments.
        # For now, we will sort by the original index to keep the order.
        df = df.sort_index().reset_index(drop=True)
        df['place_agenda'] = range(1, len(df) + 1)
        return df
```

**3. Integrate the `OrderCalculator` into the `DatasetBuilder`:**
   - In `_process_session` of `dataset_builder.py`, after creating the `reconstructed_rows` DataFrame, use the `OrderCalculator` to re-calculate the `place_agenda`.

```python
# src/reconstruction/dataset_builder.py

# ... imports
from src.segmentation.order_calculator import OrderCalculator

class DatasetBuilder:
    # ...

    def _process_session(self, session_df: pd.DataFrame) -> pd.DataFrame:
        # ... (scraping and segmentation logic)

        reconstructed_df = pd.DataFrame(reconstructed_rows)
        
        # Re-order the place_agenda
        order_calculator = OrderCalculator()
        reordered_df = order_calculator.reorder(reconstructed_df)
        
        return reordered_df
```
