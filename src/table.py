from typing import Dict, List

from prettytable import PrettyTable

from .config import get_logger

logger = get_logger(__name__)


def display_data(headers: List, rows: List[Dict]) -> None:
    """
    Prints the data in a table format using PrettyTable.
    Args:
        headers (List): A list of strings representing the column headers for the table.
        rows (List[Dict]): A list of dictionaries where each dictionary represents a row in the table.
                           The keys in the dictionary should match the headers.
    Returns:
        None
    """
    logger.debug("logging data in table format")

    if not headers:
        logger.error("headers list is empty, can't print the table.")
        raise ValueError("headers list is empty, can't print the table.")

    table = PrettyTable()
    table.field_names = headers

    for r in rows:
        row_data = [r.get(header, "") for header in headers]
        logger.debug(f"adding row for printing: {row_data}")
        table.add_row(row_data)

    table.align = "l"
    logger.info(f"\n{table}")
