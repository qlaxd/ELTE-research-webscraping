# Step-by-Step Implementation Roadmap: Polish Parliament Speech Segmentation

## Project Goal
This document outlines the implementation plan for the Polish Parliament Speech Segmentation System. The primary objective is to correct the segmentation of the Parliament Speaker's (Marszałek) speeches in the 1991-2011 dataset. Currently, the Speaker's speeches for an entire session are concatenated into a single record. This project will involve web scraping the official parliamentary session transcripts, parsing the HTML to identify the correct speech boundaries, segmenting the concatenated text, and reconstructing the dataset with each speech segment as a separate, correctly ordered entry.

---

## Phase 1: Project Setup and Environment Configuration

### Step 1: Initialize Project Structure
Create the complete directory structure as defined in the architecture plan. This includes top-level directories like `src`, `tests`, `config`, `data`, `docs`, and `scripts`, along with all necessary subdirectories. Place `__init__.py` files in all Python package directories (`src/*`, `tests/*`) to ensure they are recognized as modules.

### Step 2: Set Up Version Control
Initialize a Git repository in the project root. Create a comprehensive `.gitignore` file to exclude virtual environment directories (`.venv/`, `venv/`), Python bytecode (`*.pyc`, `__pycache__/`), temporary data files (`data/cache/*`, `data/output/*`), log files (`*.log`), and common OS/IDE-specific files (`.idea/`, `.vscode/`, `.DS_Store`).

### Step 3: Configure Python Virtual Environment
Create a dedicated Python virtual environment (e.g., using `venv`: `python3 -m venv .venv`). Activate the environment and ensure it uses Python 3.9 or higher. Document the activation commands (`source .venv/bin/activate`) in the `README.md`.

### Step 4: Define Dependencies
Create two requirements files:
- `requirements.txt`: For production dependencies, including `pandas`, `beautifulsoup4`, `lxml`, `requests`, `pydantic`, `tqdm`, `python-dotenv`, `loguru`, and `PyYAML`.
- `requirements-dev.txt`: For development dependencies, including `pytest`, `pytest-cov`, `black`, `flake8`, and `mypy`.
Install the dependencies into the virtual environment.

### Step 5: Create Configuration Files
In the `config/` directory, create `settings.yaml` to manage application settings.
- **Structure**: Use nested keys: `scraping`, `processing`, `paths`, and `logging`.
- **Scraping**: `base_url`, `timeout` (e.g., 30), `retry_count` (e.g., 3), `retry_delay` (e.g., 1.0), `rate_limit_delay` (e.g., 0.5), and a descriptive `user_agent`.
- **Processing**: `chunk_size` for CSV reading (e.g., 1000), `encoding` ('utf-8'), `csv_delimiter` (','), and `date_format` ('%Y.%m.%d').
- **Paths**: `input_dir`, `output_dir`, `cache_dir`, and `log_dir`.

### Step 6: Set Up Environment Variables
Create a `.env.example` file in the root directory to serve as a template for environment variables. This can include paths or optional credentials (e.g., for a Redis cache). Document the purpose of each variable.

---

## Phase 2: Data Models and Core Utilities

### Step 7: Define Data Models
In `src/data/models.py`, use Pydantic to define data structures.
- **Speech Model**: A `Speech(BaseModel)` class with fields: `text: str`, `speaker_name: str`, `chair: int` (0 or 1), `agenda_item: Optional[str]`, `place_agenda: int`, `date: datetime`, and `session_id: str`. Add validators to clean text (strip whitespace, remove HTML) and validate field values.
- **Session Model**: A `Session(BaseModel)` class with fields: `session_id: str`, `date: datetime`, `url: str`, and `speeches: List[Speech]`.

### Step 8: Implement CSV Handler
In `src/data/csv_handler.py`, create a `CSVHandler` class.
- **Methods**: Implement `2` (with support for chunking), `write_csv` (ensuring parent directories exist), `validate_columns` to check for required headers, and `process_in_chunks` to apply a function to a large CSV file piece by piece. Handle potential `FileNotFoundError` and `UnicodeDecodeError`.

### Step 9: Create Data Validator
In `src/data/validator.py`, create a `DataValidator` class.
- **Methods**: Implement `validate_required_columns`, `validate_data_types` (e.g., 'chair' is 0/1, 'date' matches format), and `validate_chair_speeches` (ensuring each session has exactly one concatenated chair speech to be processed). A main `validate_all` method should run all checks and return a comprehensive list of errors.

### Step 10: Build Text Cleaning Utilities
In `src/utils/text_cleaner.py`, create a `TextCleaner` class with static methods for text manipulation.
- **Methods**: `remove_html_tags`, `normalize_polish_chars` (using `unicodedata`), `remove_session_brackets` (to strip informational text like `(godz. 9:02)`), and a primary `clean_text` method that orchestrates the cleaning pipeline.

### Step 11: Implement Date Handler
In `src/utils/date_handler.py`, create a `DateHandler` class.
- **Methods**: `parse_polish_date` to convert string dates to `datetime` objects, `generate_session_id` from a date (e.g., 'session_20100806'), `validate_date_range`, and `format_date_for_url`.

### Step 12: Set Up Logging System
In `src/utils/logger.py`, configure `loguru` for structured logging.
- **Setup**: Create a `setup_logging` function that configures file-based logging with rotation (`rotation="10 MB"`) and retention (`retention="7 days"`) as well as a formatted console logger.
- **Helpers**: Implement functions for contextual logging, such as `log_error_with_context` to capture relevant data (e.g., session ID) when an error occurs.

---

## Phase 3: Web Scraping Infrastructure

### Step 13: Build Web Client
In `src/scraping/web_client.py`, create a `WebClient` class using `requests`.
- **Features**: Implement a `requests.Session` for connection pooling. Add automatic retries with exponential backoff for handling transient network errors and 5xx server errors. Implement rate limiting to avoid overwhelming the server.

### Step 14: Implement Cache Manager
In `src/scraping/cache_manager.py`, build a `CacheManager` to store fetched HTML content.
- **Features**: Use `pathlib` for file-based caching. Generate cache keys from URLs using a hash function (e.g., `hashlib.sha256`). Implement methods to `save_to_cache`, `get_from_cache`, and check for cache expiration based on a configurable TTL (Time-To-Live). Add methods to clear expired or all cache.

### Step 15: Create Session Scraper
In `src/scraping/session_scraper.py`, create a `SessionScraper` class.
- **Logic**: Implement `_build_session_url` to construct the correct URL for a given session date. The `fetch_session` method will orchestrate the process: first check the cache, and if not found, use the `WebClient` to fetch the page and then save it to the cache.

### Step 16: Add Scraping Rules Configuration
In `config/scraping_rules.yaml`, define selectors for parsing.
- **Content**: Since the website's HTML structure may have changed between 1991 and 2011, define different CSS selectors or XPath expressions for various year ranges. This includes selectors for the main content area, speaker sections, and hyperlinks. A loader function in `src/scraping/rules_loader.py` will provide the correct rules for a given year.

---

## Phase 4: HTML Parsing and Analysis

### Step 17: Implement HTML Parser
In `src/parsing/html_parser.py`, create an `HTMLParser` class that uses `BeautifulSoup` with the `lxml` backend.
- **Logic**: The parser will take raw HTML content. It will use the scraping rules to `extract_content_area` and provide a structured representation of the document, focusing on the speech elements.

### Step 18: Build Speech Extractor
In `src/parsing/speech_extractor.py`, create a `SpeechExtractor` class.
- **Methods**:
    - `find_chair_speech_block`: Locate the single, concatenated speech from the Speaker (Marszałek).
    - `extract_hyperlinks`: Find all `<a>` tags within the content that point to the other individual speeches. Extract their `href` and link text.
    - `identify_segment_boundaries`: Use the positions of the hyperlinks within the text to determine the start and end points of each of the Speaker's speech segments.
    - `extract_segments`: Use the identified boundaries to split the concatenated text into a list of individual speech strings.

### Step 19: Create Link Analyzer
In `src/parsing/link_analyzer.py`, create a `LinkAnalyzer` class.
- **Logic**: This class will process the hyperlinks extracted in the previous step. It will `extract_speaker_from_link` text and `map_links_to_speeches` in the original dataset to ensure the order is correct and all speeches are accounted for.

### Step 20: Implement Segment Boundary Detection
Enhance the `SpeechExtractor` with more robust boundary detection.
- **Logic**: Accurately identify where one speech segment ends and another begins by analyzing the DOM structure around the hyperlinks. This helps handle cases with no clear text delimiter or nested HTML elements that might incorrectly split text. Validate that the sum of segment lengths equals the original text length to prevent data loss.

---

## Phase 5: Segmentation Processing

### Step 21: Build Text Splitter
In `src/segmentation/text_splitter.py`, create a `TextSplitter` class.
- **Logic**: This class takes the concatenated Speaker text and the list of boundaries (start/end positions). Its primary method, `split_text`, iterates through the boundaries, extracts the text for each segment, and uses the `TextCleaner` utility to clean it.

### Step 22: Implement Metadata Manager
In `src/segmentation/metadata_manager.py`, create a `MetadataManager` class.
- **Logic**: This class is responsible for creating the metadata for the new speech segments.
    - `copy_base_metadata`: Copy the metadata (date, session_id, etc.) from the original Speaker's row to each new segment. The `chair` value remains 1.
    - `assign_agenda_items`: For each new segment, assign the `agenda_item` from the speech that immediately follows it in the session, as per the task description.

### Step 23: Create Order Calculator
In `src/segmentation/order_calculator.py`, implement logic to recalculate the `place_agenda` for the entire session.
- **Logic**: After the new Speaker segments are inserted, the `place_agenda` column, which is a running number for speeches within a session, must be completely re-calculated for all rows in that session to ensure it is sequential and correct.

### Step 24: Build Segment Validator
Add validation logic to the segmentation process.
- **Checks**: Verify that no text is lost during segmentation by comparing the character count of the original text with the sum of segment character counts. Ensure all new segments have the required metadata and that no duplicate segments are created.

---

## Phase 6: Dataset Reconstruction

### Step 25: Implement Dataset Builder
In `src/reconstruction/dataset_builder.py`, create the main `DatasetBuilder` class.
- **Orchestration**: This class will manage the entire reconstruction process. It will iterate through each session in the input DataFrame, identify the Speaker's row (`chair==1`), trigger the scraping/parsing/segmentation process for it, and then use the results to build a new, corrected DataFrame for that session.

### Step 26: Create Row Inserter
In `src/reconstruction/row_inserter.py`, develop functions to modify the DataFrame.
- **Logic**: Given a session's DataFrame and the newly created segment rows, this module will remove the original concatenated row and insert the new rows at their correct positions based on the hyperlink analysis. This requires careful management of DataFrame indices.

### Step 27: Build Sequence Manager
In `src/reconstruction/sequence_manager.py`, create a class to finalize the session's order.
- **Logic**: After inserting the new rows, this manager will use the `OrderCalculator` to re-index the `place_agenda` column for the entire session. It ensures all speeches are in the correct chronological sequence.

### Step 28: Add Reconstruction Validator
Create a final validation step for the reconstructed data.
- **Checks**: Ensure the reconstructed DataFrame for a session contains all original non-Speaker speeches, that the new segments are correctly placed, and that the total row count is as expected.

---

## Phase 7: Integration and Pipeline Orchestration

### Step 29: Implement Main Pipeline
In `src/main.py`, create the main orchestration logic.
- **Flow**: The script will load configuration, initialize all necessary handlers and services, read the input CSV, and loop through each session to apply the segmentation and reconstruction process. It should include robust error handling and checkpointing to save progress.

### Step 30: Build Execution Script
In `scripts/run_segmentation.py`, create a user-facing command-line interface (CLI) using `argparse`.
- **Options**: The CLI should accept arguments for the input and output file paths, allow processing of specific date ranges, and include a `--dry-run` mode that performs the analysis without writing any output.

### Step 31: Create Progress Reporting
Integrate `tqdm` to provide progress bars for long-running processes, especially the session processing loop. The logs should provide detailed status updates and estimates for time remaining.

### Step 32: Add Resume Capability
Implement a mechanism to save the processing state periodically (e.g., after each session). If the script is interrupted, it should be able to detect the last successfully processed session and resume from that point, avoiding reprocessing the entire dataset.

---

## Phase 8: Testing Implementation

### Step 33: Create Unit Tests
In `tests/unit/`, write unit tests for each class and function in isolation.
- **Coverage**: Test `TextCleaner` with various malformed strings. Test `CSVHandler` with different encodings. Test `DateHandler` with invalid date formats. Test `OrderCalculator` with edge cases. Use `pytest` and mock external dependencies like web requests.

### Step 34: Develop Integration Tests
In `tests/integration/`, create tests for the end-to-end pipeline components.
- **Scenarios**: Test the full flow for a single session: scraping, parsing, segmentation, and reconstruction. Verify that the final output for the session matches an expected result. Use real (but fixed) HTML and CSV fixture data.

### Step 35: Build Test Fixtures
In `tests/fixtures/`, create a collection of test data.
- **Content**: Include a sample `sample_data.csv` with a known session requiring segmentation, a `sample_html.html` file corresponding to that session's transcript, and an `expected_output.csv` to compare against.

### Step 36: Implement Performance Tests
Create tests to benchmark the performance of critical parts of the system.
- **Focus**: Profile memory usage when processing large files and measure the time taken for the segmentation of a large number of sessions.

---

## Phase 9: Quality Assurance and Validation

### Step 37: Create Output Validator
In `scripts/validate_output.py`, build a script to perform a final validation on the generated output file.
- **Checks**: Verify that no data was lost, check for schema integrity, and run statistical analyses (e.g., distribution of segments per session) to spot anomalies.

### Step 38: Build Comparison Tools
Develop a simple tool to compare the original and processed datasets side-by-side, highlighting the changes made to a specific session.

### Step 39: Implement Manual Review Interface
Create a simple CLI-based tool that allows a user to review sessions that were flagged as problematic during processing. It should display the original concatenated text and the new segments for manual verification.

### Step 40: Add Data Quality Metrics
Implement logic to generate a data quality report after each run, including metrics like the number of sessions processed, segments created, and agenda item assignment consistency.

---

## Phase 10: Documentation and Deployment

### Step 41: Write API Documentation
In `docs/API.md`, document the public functions and classes, their parameters, and return values. Use a standard docstring format like Google's or reStructuredText.

### Step 42: Create Data Schema Documentation
In `docs/DATA_SCHEMA.md`, document the structure of the input and output CSV files, detailing each column and its meaning.

### Step 43: Build Troubleshooting Guide
In `docs/TROUBLESHOOTING.md`, list common errors and their solutions, such as how to handle scraping failures or data validation issues.

### Step 44: Implement Dockerfile
Create a `Dockerfile` to containerize the application. It should install all dependencies, set up the environment (e.g., encoding), and define an entry point for running the segmentation script.

### Step 45: Create Deployment Scripts
Build shell scripts to automate the process of running the application, including setting up the environment and passing the correct arguments to the main script.

---

## Phase 11: Optimization and Monitoring

### Step 46: Implement Parallel Processing
Investigate opportunities for parallelization, such as scraping multiple sessions concurrently using `multiprocessing` or `asyncio`. Ensure that any parallel processing is done in a thread-safe manner, especially when writing to files or a cache.

### Step 47: Add Memory Optimization
For very large datasets, ensure the pipeline can stream data instead of loading everything into memory at once. Use generators and process the CSV in chunks where possible.

### Step 48: Create Monitoring Dashboard
Develop a simple HTML-based report that is updated during processing to show real-time progress, error rates, and performance metrics.

### Step 49: Implement Logging Analytics
Write a script to parse the log files to generate summary reports, identify common issues, and track processing trends over time.

---

## Phase 12: Final Validation and Production Readiness

### Step 50: Complete End-to-End Testing
Run the entire pipeline on the full dataset from 1991-2011. Verify that the output is complete and correct. Generate a final, comprehensive processing report with statistics and validation results to confirm the project's success.
