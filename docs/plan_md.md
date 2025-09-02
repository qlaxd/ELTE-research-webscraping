# Polish Parliament Speech Segmentation System - Architecture Plan

## Project Overview

This system addresses a data quality issue in the Polish parliamentary speeches dataset (1991-2011) where the Parliament Speaker's (Marszałek) speeches are incorrectly concatenated into single entries per session. The solution involves web scraping, text parsing, and intelligent segmentation to properly split and reorder these speeches within the dataset.

## Big-Scope Architecture

### System Components

The architecture follows a modular ETL (Extract-Transform-Load) pipeline pattern with the following major components:

1. **Data Ingestion Layer** - Handles CSV input/output and data validation
2. **Web Scraping Engine** - Fetches parliamentary session pages from the Sejm website
3. **HTML Parser & Analyzer** - Extracts speech segments and identifies split points
4. **Segmentation Processor** - Splits concatenated speeches and manages metadata
5. **Data Reconstruction Engine** - Rebuilds the dataset with properly ordered entries
6. **Quality Assurance Module** - Validates output and ensures data integrity

### Data Flow Architecture

```
Input CSV → Validation → Session Identification → Web Scraping → 
HTML Parsing → Speech Segmentation → Metadata Assignment → 
Order Reconstruction → Output CSV Generation → Quality Check
```

## Directory Structure

```
polish-parliament-segmentation/
│
├── config/
│   ├── settings.yaml              # Application configuration
│   ├── logging.yaml               # Logging configuration
│   └── scraping_rules.yaml        # Web scraping patterns and rules
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── csv_handler.py         # CSV reading/writing operations
│   │   ├── validator.py           # Input data validation
│   │   └── models.py              # Data models and schemas
│   │
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── web_client.py          # HTTP client with retry logic
│   │   ├── session_scraper.py     # Sejm website scraper
│   │   └── cache_manager.py       # Caching scraped content
│   │
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── html_parser.py         # HTML structure parser
│   │   ├── speech_extractor.py    # Extract speech segments
│   │   └── link_analyzer.py       # Analyze hyperlink patterns
│   │
│   ├── segmentation/
│   │   ├── __init__.py
│   │   ├── text_splitter.py       # Split concatenated speeches
│   │   ├── metadata_manager.py    # Handle metadata assignment
│   │   └── order_calculator.py    # Calculate place_agenda values
│   │
│   ├── reconstruction/
│   │   ├── __init__.py
│   │   ├── dataset_builder.py     # Rebuild complete dataset
│   │   ├── row_inserter.py        # Insert segmented rows
│   │   └── sequence_manager.py    # Manage speech ordering
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging utilities
│       ├── date_handler.py         # Date parsing and formatting
│       └── text_cleaner.py         # Text preprocessing utilities
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_csv_handler.py
│   │   ├── test_html_parser.py
│   │   ├── test_text_splitter.py
│   │   └── test_order_calculator.py
│   │
│   ├── integration/
│   │   ├── test_scraping_pipeline.py
│   │   ├── test_segmentation_flow.py
│   │   └── test_reconstruction.py
│   │
│   └── fixtures/
│       ├── sample_data.csv
│       ├── sample_html.html
│       └── expected_output.csv
│
├── data/
│   ├── input/                     # Original CSV files
│   ├── output/                    # Processed CSV files
│   ├── cache/                     # Cached web pages
│   └── logs/                      # Application logs
│
├── docs/
│   ├── API.md                     # API documentation
│   ├── DATA_SCHEMA.md             # Data structure documentation
│   └── TROUBLESHOOTING.md         # Common issues and solutions
│
├── scripts/
│   ├── run_segmentation.py        # Main execution script
│   ├── validate_output.py         # Output validation script
│   └── generate_report.py         # Processing report generator
│
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── setup.py                        # Package setup
├── README.md                       # Project documentation
├── .env.example                    # Environment variables template
├── .gitignore
└── Dockerfile                      # Container configuration
```

## Module Interconnections

### Core Dependencies Flow

1. **main.py** orchestrates the entire pipeline by:
   - Loading configuration from `config/`
   - Initializing the CSV handler to read input data
   - Invoking the scraping module for each session
   - Passing scraped content to the parsing module
   - Sending parsed segments to the segmentation module
   - Using reconstruction module to build final dataset
   - Writing output through CSV handler

2. **Data Layer** (`src/data/`):
   - Provides data models used throughout the application
   - Handles all file I/O operations
   - Validates data integrity at input and output stages

3. **Scraping Layer** (`src/scraping/`):
   - Depends on data models for session information
   - Implements caching to avoid redundant requests
   - Provides HTML content to parsing layer

4. **Parsing Layer** (`src/parsing/`):
   - Consumes raw HTML from scraping layer
   - Identifies speech boundaries using link patterns
   - Extracts clean text segments for segmentation

5. **Segmentation Layer** (`src/segmentation/`):
   - Receives parsed segments and metadata
   - Splits speaker's concatenated text
   - Calculates new metadata values
   - Prepares segmented data for reconstruction

6. **Reconstruction Layer** (`src/reconstruction/`):
   - Takes segmented speeches and original dataset
   - Inserts new rows in correct positions
   - Recalculates sequential values (place_agenda)
   - Produces final ordered dataset

## Technology Stack

### Core Technologies

1. **Python 3.9+**
   - Primary language for implementation
   - Strong ecosystem for web scraping and data processing
   - Excellent CSV handling capabilities

2. **pandas 2.0+**
   - Efficient CSV data manipulation
   - Complex data transformations
   - Memory-efficient processing of large datasets

3. **BeautifulSoup4 4.12+**
   - HTML parsing and navigation
   - Robust handling of malformed HTML
   - CSS selector support for element extraction

4. **requests 2.31+**
   - HTTP client for web scraping
   - Session management for efficiency
   - Retry mechanisms for reliability

5. **lxml 4.9+**
   - Fast XML/HTML processing
   - XPath support for complex queries
   - Better performance than pure Python parsers

### Supporting Libraries

6. **pydantic 2.0+**
   - Data validation and settings management
   - Type hints and runtime validation
   - Configuration schema enforcement

7. **tqdm 4.66+**
   - Progress bars for long-running operations
   - User feedback during processing
   - ETA calculations

8. **python-dotenv 1.0+**
   - Environment variable management
   - Configuration security
   - Development/production separation

9. **pytest 7.4+**
   - Comprehensive testing framework
   - Fixture support for test data
   - Coverage reporting capabilities

10. **loguru 0.7+**
    - Structured logging
    - Automatic rotation and retention
    - Better debugging capabilities

### Infrastructure Tools

11. **Redis (optional)**
    - Caching scraped web pages
    - Reducing load on Sejm servers
    - Improving processing speed

12. **Docker**
    - Consistent development environment
    - Easy deployment
    - Dependency isolation

## Justification for Technology Choices

### pandas
Essential for handling CSV operations efficiently. The dataset spans 20 years of parliamentary data, requiring robust data manipulation capabilities that pandas provides through vectorized operations and memory optimization.

### BeautifulSoup4 + lxml
The Sejm website uses complex HTML structures with nested elements. BeautifulSoup4 provides intuitive navigation while lxml offers performance. This combination handles both well-formed and malformed HTML gracefully.

### requests
Standard Python HTTP library with excellent session management, crucial for maintaining cookies and handling potential authentication requirements when accessing parliamentary archives.

### pydantic
Ensures data integrity throughout the pipeline. With complex transformations happening to parliamentary records, runtime validation prevents data corruption and provides clear error messages.

### pytest
Critical for validating the segmentation logic. The complexity of splitting and reordering speeches requires comprehensive testing to ensure no data loss or misalignment.

### loguru
Given the complexity of web scraping and text processing, detailed logging is essential for debugging and monitoring. Loguru's structured logging helps track the transformation of each parliamentary session.

## System Constraints and Considerations

1. **Rate Limiting**: Respect Sejm website's server capacity with configurable delays
2. **Memory Management**: Process large CSV files in chunks when necessary
3. **Data Integrity**: Maintain audit trail of all transformations
4. **Idempotency**: Ensure rerunning doesn't create duplicate segments
5. **Error Recovery**: Save progress periodically to resume after failures
6. **Encoding**: Handle Polish characters (UTF-8) correctly throughout