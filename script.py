#!/usr/bin/env python3

"""
Author: zbhavyai@gmail.com
"""

import argparse
import csv
import logging
import os
import re
from typing import Dict, List, Tuple

import yt_dlp
from prettytable import PrettyTable

logging.basicConfig(
    level=logging.INFO,
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
        logging.debug(f"adding row for printing: {row_data}")
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
            logging.debug(f"read row: {obj}")
            csvRows.append(obj)

        return csvHeader, csvRows


def download_audio(ytLink: str, filename: str, output_directory: str) -> bool:
    """
    Downloads audio from a YouTube link and saves it as audio file in the specified output directory.
    Args:
        ytLink (str): The URL of the YouTube video to download.
        filename (str): The desired name for the downloaded audio file (without extension).
        output_directory (str): The directory where the downloaded audio file will be saved.
    Returns:
        bool: True if the download was successful, False otherwise.
    """
    logging.debug(f'downloading: "{ytLink}" into "{output_directory}"')

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            logging.debug(f'created directory: "{output_directory}"')
        except OSError as e:
            logging.error(f'error creating directory "{output_directory}": {e}')
            return False

    final_filename = None

    def progress_hook(d):
        nonlocal final_filename
        if d["status"] == "finished":
            final_filename = d["filename"]

    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        # "postprocessors": [
        #     {
        #         "key": "FFmpegExtractAudio",
        #         "preferredcodec": "mp3",
        #         "preferredquality": "0",
        #     }
        # ],
        "outtmpl": f"{output_directory}/{filename}.%(ext)s",
        "progress_hooks": [progress_hook],
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ytLink])

            if final_filename:
                just_filename = os.path.basename(final_filename)
                logging.info(f'downloaded: "{ytLink}" as "{just_filename}"')

        return os.path.exists(final_filename)

    except yt_dlp.DownloadError as e:
        logging.error(f"download error: {e}")
        return False

    except Exception as e:
        logging.error(f"an error occurred: {e}")
        return False


def download_audio_from_csv(csv_file: str, output_directory: str) -> None:
    """
    Downloads audio files from YouTube links specified in a CSV file.
    Args:
        csv_file (str): The path to the CSV file containing YouTube links.
        output_directory (str): The directory where the downloaded audio files will be saved.
    Returns:
        None
    """
    headers, data = read_csv(csv_file)

    def get_video_id(url):
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    for row in data:
        ytLink = row.get("ytLink")
        title = row.get("title")
        video_id = get_video_id(ytLink)
        download_audio(ytLink, f"{title} - {video_id}", output_directory)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A script to download audio from YouTube links."
    )

    # csv arguments
    parser.add_argument(
        "--csv",
        action="store",
        help="The CSV file to parse",
    )

    # download arguments
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download audio from YouTube links specified in a CSV file",
    )

    # test arguments
    parser.add_argument(
        "--testcsv",
        action="store_true",
        help="Print the data from the CSV file",
    )
    parser.add_argument(
        "--url",
        action="store",
        help="Download audio from the given YouTube URL",
    )
    parser.add_argument(
        "--filename",
        action="store",
        help="Use the filename for the downloaded audio file",
    )

    # parse the arguments
    args = parser.parse_args()

    if args.testcsv and args.csv:
        headers, data = read_csv(args.csv)
        display_data(headers, data)

    elif args.url and args.filename:
        output_path = os.path.abspath("output")
        download_audio(args.url, args.filename, output_path)

    elif args.download and args.csv:
        output_path = os.path.abspath("output")
        download_audio_from_csv(args.csv, output_path)

    else:
        logging.error("Invalid action specified.")
        parser.error("Invalid action specified.")


if __name__ == "__main__":
    main()
