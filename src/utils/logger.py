import logging
import sys
from pathlib import Path
from loguru import logger

def setup_logging(log_dir: Path, log_level: str = "INFO"):
    """
    Configures the Loguru logger for the application.

    This setup removes the default handler, adds a new handler for console output
    with a specific format, and adds a file handler for writing logs to a file
    with rotation and retention policies.

    Args:
        log_dir: The directory where log files will be stored.
        log_level: The minimum log level to be captured (e.g., "INFO", "DEBUG").
    """
    # Ensure the log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove the default logger
    logger.remove()

    # Add a console logger
    logger.add(
        sys.stderr,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        colorize=True
    )

    # Add a file logger
    log_file_path = log_dir / "segmentation_pipeline.log"
    logger.add(
        log_file_path,
        level="DEBUG",  # Capture debug messages in the file
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        enqueue=False, # Make logging synchronous for easier debugging
        backtrace=True,
        diagnose=True
    )

    logging.info(f"Logger configured. Log level: {log_level}. Log file: {log_file_path}")

# Example of a more advanced logging helper (can be expanded later)
def log_error_with_context(error: Exception, **kwargs):
    """
    Logs an error with additional context.

    Args:
        error: The exception that occurred.
        **kwargs: Arbitrary keyword arguments to provide context (e.g., session_id, row_number).
    """
    with logger.contextualize(**kwargs):
        logger.exception(error)

