#!/usr/bin/env python3

"""
Author: zbhavyai@gmail.com
"""

import argparse
import csv
import logging
from datetime import datetime
from typing import Dict, List, Tuple

from prettytable import PrettyTable

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)5s] %(module)8s (%(lineno)3d) %(funcName)s: %(message)s",
)


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
    logging.debug("logging data in table format")

    if not headers:
        logging.error("Headers list is empty. Can't print the table.")
        raise ValueError("Headers list is empty. Can't print the table.")

    table = PrettyTable()
    table.field_names = headers

    for r in rows:
        row_data = [r.get(header, "") for header in headers]
        logging.debug(f"adding row: {row_data}")
        table.add_row(row_data)

    table.align = "l"
    logging.info(f"\n{table}")


def read_csv(filename: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Reads a CSV file and returns its header and rows.
    Args:
        filename (str): The path to the CSV file to be read.
    Returns:
        Tuple[List[str], List[Dict[str, str]]]: A tuple containing:
            - A list of strings representing the CSV header.
            - A list of dictionaries, each representing a row in the CSV file with keys as column names and values as cell data.
    """
    logging.debug(f'reading file: "{filename}"')

    csvHeader = []
    csvRows = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        csvHeader = ["ytLink", "title", "album", "artist", "composer", "year"]

        for row in reader:
            obj = {
                "ytLink": row["ytLink"],
                "title": row["title"],
                "album": row["album"],
                "artist": row["artist"],
                "composer": row["composer"],
                "year": row["year"],
            }

            csvRows.append(obj)

        return csvHeader, csvRows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A script to download audio from YouTube videos."
    )

    # csv arguments
    parser.add_argument(
        "--csv",
        action="store",
        help="Parse the CSV file and print the contents",
    )

    # parse the arguments
    args = parser.parse_args()

    if args.csv:
        headers, data = read_csv(args.csv)
        display_data(headers, data)

    else:
        logging.error("Invalid action specified.")
        parser.error("Invalid action specified.")


if __name__ == "__main__":
    main()
