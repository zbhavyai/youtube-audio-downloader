import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "script.log")
VERSION = "1.0.0"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)7s] %(module)8s (%(lineno)3d) %(funcName)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the given name.
    Args:
        name (str): The name of the logger.
    Returns:
        logging.Logger: The logger object.
    """
    return logging.getLogger(name)
