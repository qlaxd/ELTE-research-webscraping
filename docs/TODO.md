# Project Completion TODO List

This document outlines the remaining tasks to complete the Polish Parliament Speech Segmentation project, as described in the project documentation.

## 1. Critical Task: Fix the Scraping Block

-   **Task:** Refactor the web scraping logic to handle the anti-bot protection on the `sejm.gov.pl` website.
-   **Details:** The current `requests`-based implementation is being blocked. This needs to be replaced with a headless browser solution like Selenium.
-   **Reference:** See `docs/refactor.md` for a detailed implementation plan.

## 2. Major Task: Update Scraping Rules

-   **Task:** Add scraping rules for the years 2012 and onwards.
-   **Details:** The `config/scraping_rules.yaml` file needs to be updated with the correct CSS selectors for the more recent session pages. This can only be done after the scraping block is resolved.
-   **Reference:** See `docs/refactor.md` for guidance on how to add new rules.

## 3. Minor Task: Implement `place_agenda` Re-calculation

-   **Task:** Implement the logic to re-calculate the `place_agenda` column after segmenting and inserting the speaker's speeches.
-   **Details:** The `OrderCalculator` class needs to be implemented and integrated into the `DatasetBuilder`.
-   **Reference:** See `docs/refactor.md` for a code example.

## 4. Additional Tasks from Documentation

The following tasks are also described in the project documentation (`docs/implementation.md` and `docs/plan_md.md`) and should be completed to finish the project:

-   **[ ] Implement `RowInserter`:** The `src/reconstruction/row_inserter.py` module is mentioned in the documentation but is not yet implemented. This module is responsible for inserting the new segmented rows into the DataFrame.
-   **[ ] Implement `SegmentValidator`:** The `src/segmentation/segment_validator.py` module is mentioned in the documentation but is not yet implemented. This module should validate the integrity of the segmented speeches.
-   **[ ] Implement `ReconstructionValidator`:** The `src/reconstruction/reconstruction_validator.py` module is mentioned in the documentation but is not yet implemented. This module should validate the reconstructed dataset.
-   **[ ] Complete the CLI:** The `scripts/run_segmentation.py` script should be enhanced with the features described in the documentation, such as a `--dry-run` mode and the ability to process specific date ranges.
-   **[ ] Implement Resume Capability:** The script should be able to save its state and resume from the last successfully processed session.
-   **[ ] Implement Testing:** The project is missing a comprehensive test suite. Unit and integration tests should be written as described in the documentation.
-   **[ ] Implement Quality Assurance and Validation Scripts:** The `scripts/validate_output.py` and other QA scripts mentioned in the documentation should be implemented.
-   **[ ] Complete the Documentation:** The `docs/API.md`, `docs/DATA_SCHEMA.md`, and `docs/TROUBLESHOOTING.md` files should be created and filled with content.
