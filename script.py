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
from mutagen import File
from mutagen.id3 import COMM, ID3, TALB, TCOM, TDRC, TIT2, TPE1
from mutagen.mp3 import MP3
from prettytable import PrettyTable

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "script.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)5s] %(module)8s (%(lineno)3d) %(funcName)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode="w", encoding="utf-8"),
    ],
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


def download_audio(ytLink: str, filename: str, o_directory: str) -> Tuple[bool, str]:
    """
    Downloads audio from a YouTube link and saves it as an audio file in the specified output directory.
    Args:
        ytLink (str): The URL of the YouTube video to download.
        filename (str): The desired name for the downloaded audio file (without extension).
        o_directory (str): The directory where the downloaded audio file will be saved.
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the download was successful, False otherwise.
            - str: The path to the downloaded audio file.
    """
    logging.debug(f'downloading: "{ytLink}" into "{o_directory}"')

    if not os.path.exists(o_directory):
        try:
            os.makedirs(o_directory)
            logging.debug(f'created directory: "{o_directory}"')
        except OSError as e:
            logging.error(f'error creating directory "{o_directory}": {e}')
            return False

    final_filename = None

    def progress_hook(d):
        if d["status"] == "finished":
            logging.debug(f'Finished downloading "{os.path.basename(d["filename"])}"')

    def postprocessor_hook(d):
        nonlocal final_filename
        if d["status"] == "finished" and d["postprocessor"] == "MoveFiles":
            final_filename = d["info_dict"]["filepath"]
            logging.debug(f'Finished processing "{os.path.basename(final_filename)}"')

    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": f"{o_directory}/{filename}.%(ext)s",
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "quiet": True,
        "noprogress": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ytLink])

            if final_filename:
                just_filename = os.path.basename(final_filename)
                logging.info(f'downloaded "{ytLink}" as "{just_filename}"')

        return (os.path.exists(final_filename), final_filename)

    except yt_dlp.DownloadError as e:
        logging.error(f"download error: {e}")
        return (False, None)

    except Exception as e:
        logging.error(f"an error occurred: {e}")
        return (False, None)


def download_audio_from_csv(csv_file: str, o_directory: str) -> None:
    """
    Downloads audio files from YouTube links specified in a CSV file.
    Args:
        csv_file (str): The path to the CSV file containing YouTube links.
        o_directory (str): The directory where the downloaded audio files will be saved.
    Returns:
        None
    """
    logging.debug(f'downloading audio from "{csv_file}" into "{o_directory}"')

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
        (status, file) = download_audio(ytLink, f"{title} - {video_id}", o_directory)

        if status:
            set_metadata(file, row)


def clean_metadata(filename: str) -> bool:
    """
    Removes all metadata from an audio file.
    Args:
        filename (str): Path to the audio file.
    Returns:
        bool: True if metadata was successfully removed, False otherwise.
    """
    try:
        audio = File(filename, easy=True)
        if audio is None:
            logging.error(f'corrupt file "{filename}"')
            return False

        audio.delete()
        audio.save()
        logging.info(f'cleaned metadata for "{filename}"')
        return True

    except Exception as e:
        logging.error(f"failed to clean metadata for {filename}: {e}")
        return False


def clean_metadata_directory(directory: str) -> None:
    """
    Removes all metadata from audio files in a directory.
    Args:
        directory (str): The directory containing audio files.
    Returns:
        None
    """
    logging.debug(f'cleaning metadata in "{directory}"')

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                clean_metadata(os.path.join(root, file))


def set_metadata(filename: str, metadata: Dict[str, str]) -> bool:
    """
    Sets the metadata for an MP3 file.
    Args:
        filename (str): The path to the MP3 file.
        metadata (Dict[str, str]): A dictionary containing metadata to be set.
            Possible keys are:
                - "title": The title of the track.
                - "artist": The artist of the track.
                - "album": The album name.
                - "composer": The composer of the track.
                - "year": The year of release.
                - "comments": Additional comments, such as a YouTube link.
    Returns:
        bool: True if metadata was set successfully, False otherwise.
    """
    logging.debug(f'setting metadata for "{filename}"')

    if not os.path.exists(filename):
        logging.error(f'file "{filename}" does not exist')
        return False

    try:
        audio = MP3(filename, ID3=ID3)
        audio.tags = ID3()

        if "title" in metadata:
            audio.tags.add(TIT2(encoding=3, text=metadata["title"]))

        if "artist" in metadata:
            audio.tags.add(TPE1(encoding=3, text=metadata["artist"]))

        if "album" in metadata:
            audio.tags.add(TALB(encoding=3, text=metadata["album"]))

        if "composer" in metadata:
            audio.tags.add(TCOM(encoding=3, text=metadata["composer"]))

        if "year" in metadata:
            audio.tags.add(TDRC(encoding=3, text=metadata["year"]))

        if "comments" in metadata:
            audio.tags.add(
                COMM(encoding=3, lang="eng", desc="", text=metadata["ytLink"])
            )

        audio.save()
        logging.debug(f'metadata set for "{filename}"')
        return True

    except Exception as e:
        logging.error(f'metadata error for "{filename}": {e}')
        return False


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

    # metadata arguments
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean all metadata from given audio files",
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

    elif args.clean:
        output_path = os.path.abspath("output")
        clean_metadata_directory(output_path)

    else:
        logging.error("Invalid action specified.")
        parser.error("Invalid action specified.")


if __name__ == "__main__":
    main()
