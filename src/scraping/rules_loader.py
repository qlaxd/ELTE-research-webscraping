from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
import yaml

_rules_cache: List[Dict[str, Any]] = []

def load_scraping_rules(rules_path: Path, year: int) -> Dict[str, str]:
    """
    Loads scraping rules from a YAML file and returns the appropriate set for a given year.

    Args:
        rules_path: The path to the YAML file containing the scraping rules.
        year: The year of the session to find rules for.

    Returns:
        A dictionary of CSS selectors and patterns for the given year.

    Raises:
        FileNotFoundError: If the rules file does not exist.
        ValueError: If no matching rule set is found for the given year.
    """
    global _rules_cache

    # Load rules from YAML file if the cache is empty
    if not _rules_cache:
        logger.info(f"Loading scraping rules from: {rules_path}")
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                _rules_cache = yaml.safe_load(f)
            if not _rules_cache:
                 raise ValueError("Rules file is empty or invalid.")
        except FileNotFoundError:
            logger.error(f"Scraping rules file not found at: {rules_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {rules_path}: {e}")
            raise ValueError(f"Invalid YAML format in {rules_path}")

    # Find the matching rule set for the given year
    for rule_set in _rules_cache:
        year_range = rule_set.get('year_range', [])
        if len(year_range) == 2 and year_range[0] <= year <= year_range[1]:
            logger.debug(f"Found matching rule set for year {year}.")
            return rule_set.get('selectors', {})

    logger.error(f"No matching scraping rule set found for year: {year}")
    raise ValueError(f"No scraping rules defined for year {year}.")
