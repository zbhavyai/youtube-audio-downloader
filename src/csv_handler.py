import csv
from typing import Dict, List, Tuple

from .config import get_logger
from .utils import format_multiple_artists

logger = get_logger(__name__)


def read_csv(file_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Reads a CSV file and returns its header and rows.
    Args:
        file_path (str): The path to the CSV file to be read.
    Returns:
        Tuple[List[str], List[Dict[str, str]]]: A tuple containing:
            - A list of strings representing the CSV header.
            - A list of dictionaries, each representing a row in the CSV file with keys as column names and values as cell data.
    """
    logger.debug(f'reading file: "{file_path}"')

    csvHeader = []
    csvRows = []

    with open(file_path, "r", newline="") as file:
        reader = csv.DictReader(file)
        csvHeader = ["ytLink", "title", "artist", "album", "composer", "year", "genre", "start_time", "end_time"]

        for row in reader:
            logger.debug(f"read row: {row}")
            obj = {
                "ytLink": row["ytLink"],
                "title": row["title"],
                "album": row["album"],
                "artist": format_multiple_artists(row["artist"]),
                "composer": format_multiple_artists(row["composer"]),
                "year": row["year"],
                "genre": row["genre"],
                "start_time": row.get("start_time", ""),
                "end_time": row.get("end_time", ""),
            }
            csvRows.append(obj)

        return (csvHeader, csvRows)
