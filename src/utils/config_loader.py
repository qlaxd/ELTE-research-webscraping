from pathlib import Path
from loguru import logger
import yaml

def load_config(config_path: Path) -> dict:
    """Loads the application configuration from a YAML file."""
    logger.info(f"Loading configuration from {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration file: {e}")
        raise
