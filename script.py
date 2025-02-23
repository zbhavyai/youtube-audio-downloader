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
from mutagen.id3 import COMM, ID3, TALB, TCOM, TCON, TDRC, TIT2, TPE1
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
        logging.error("headers list is empty, can't print the table.")
        raise ValueError("headers list is empty, can't print the table.")

    table = PrettyTable()
    table.field_names = headers

    for r in rows:
        row_data = [r.get(header, "") for header in headers]
        logging.debug(f"adding row for printing: {row_data}")
        table.add_row(row_data)

    table.align = "l"
    logging.info(f"\n{table}")


def format_multiple_artists(artists: str) -> str:
    """
    Splits on ',', trims spaces, and joins using ' / '.
    Args:
        artists (str): A string of multiple artists or composers separated by a comma.
    Returns:
        str: A single string of artists or composers separated by a ' / '.
    """
    logging.debug(f'formatting multiple artists: "{artists}"')

    if not artists:
        return ""

    return " / ".join(part.strip() for part in artists.split(",")) if artists else ""


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
    logging.debug(f'reading file: "{file_path}"')

    csvHeader = []
    csvRows = []

    with open(file_path, "r", newline="") as file:
        reader = csv.DictReader(file)

        csvHeader = ["ytLink", "title", "artist", "album", "composer", "year", "genre"]

        for row in reader:
            obj = {
                "ytLink": row["ytLink"],
                "title": row["title"],
                "album": row["album"],
                "artist": format_multiple_artists(row["artist"]),
                "composer": format_multiple_artists(row["composer"]),
                "year": row["year"],
                "genre": row["genre"],
            }
            logging.debug(f"read row: {obj}")
            csvRows.append(obj)

        return csvHeader, csvRows


def download_audio(yt_link: str, file_name: str, output_directory: str) -> Tuple[bool, str]:
    """
    Downloads audio from a YouTube link and saves it as an audio file in the specified output directory.
    Args:
        yt_link (str): The URL of the YouTube video to download.
        file_name (str): The desired name for the downloaded audio file (without extension).
        output_directory (str): The directory where the downloaded audio file will be saved.
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the download was successful, False otherwise.
            - str: The path to the downloaded audio file.
    """
    logging.debug(f'downloading: "{yt_link}" into "{output_directory}"')

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            logging.debug(f'created directory: "{output_directory}"')
        except OSError as e:
            logging.error(f'error creating directory "{output_directory}": {e}')
            return False

    final_filename = None

    def progress_hook(d):
        if d["status"] == "finished":
            logging.debug(f'finished downloading "{os.path.basename(d["filename"])}"')

    def postprocessor_hook(d):
        nonlocal final_filename
        if d["status"] == "finished" and d["postprocessor"] == "MoveFiles":
            final_filename = d["info_dict"]["filepath"]
            logging.debug(f'finished processing "{os.path.basename(final_filename)}"')

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
        "outtmpl": f"{output_directory}/{file_name}.%(ext)s",
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "quiet": True,
        "noprogress": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_link])

            if final_filename:
                just_filename = os.path.basename(final_filename)
                logging.info(f'downloaded "{yt_link}" as "{just_filename}"')

        return (os.path.exists(final_filename), final_filename)

    except yt_dlp.DownloadError as e:
        logging.error(f'download error for "{file_name}": {e}')
        return (False, None)

    except Exception as e:
        logging.error(f"an error occurred: {e}")
        return (False, None)


def download_audio_from_csv(file_path: str, output_directory: str) -> None:
    """
    Downloads audio files from YouTube links specified in a CSV file.
    Args:
        file_path (str): The path to the CSV file containing YouTube links.
        output_directory (str): The directory where the downloaded audio files will be saved.
    Returns:
        None
    """
    logging.debug(f'downloading audio from "{file_path}" into "{output_directory}"')

    headers, data = read_csv(file_path)

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
        (status, file) = download_audio(ytLink, f"{title} - {video_id}", output_directory)

        if status:
            set_metadata(file, row)


def clean_metadata(file_name: str) -> bool:
    """
    Removes all metadata from an audio file.
    Args:
        file_name (str): Path to the audio file.
    Returns:
        bool: True if metadata was successfully removed, False otherwise.
    """
    logging.debug(f'cleaning metadata for "{file_name}"')

    try:
        audio = File(file_name, easy=True)
        if audio is None:
            logging.error(f'corrupt file "{file_name}"')
            return False

        audio.delete()
        audio.save()
        logging.info(f'cleaned metadata for "{file_name}"')
        return True

    except Exception as e:
        logging.error(f"failed to clean metadata for {file_name}: {e}")
        return False


def clean_metadata_directory(target_directory: str) -> None:
    """
    Removes all metadata from audio files in a directory.
    Args:
        target_directory (str): The directory containing audio files.
    Returns:
        None
    """
    logging.debug(f'cleaning metadata in "{target_directory}"')

    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(".mp3"):
                clean_metadata(os.path.join(root, file))


def set_metadata(file_path: str, metadata: Dict[str, str]) -> bool:
    """
    Sets the metadata for an MP3 file.
    Args:
        file_path (str): The path to the MP3 file.
        metadata (Dict[str, str]): A dictionary containing metadata to be set.
            Possible keys are:
                - "title": The title of the track.
                - "artist": The artist of the track.
                - "album": The album name.
                - "composer": The composer of the track.
                - "year": The year of release.
                - "genre": The genre of the track.
                - "comments": Additional comments, such as a YouTube link.
    Returns:
        bool: True if metadata was set successfully, False otherwise.
    """
    logging.debug(f'setting metadata for "{file_path}"')

    if not os.path.exists(file_path):
        logging.error(f'file "{file_path}" does not exist')
        return False

    try:
        audio = MP3(file_path, ID3=ID3)
        audio.tags = ID3()

        if "title" in metadata:
            logging.debug(f'setting title: "{metadata["title"]}"')
            audio.tags.add(TIT2(encoding=3, text=metadata["title"]))

        if "artist" in metadata:
            logging.debug(f'setting artist: "{metadata["artist"]}"')
            audio.tags.add(TPE1(encoding=3, text=metadata["artist"]))

        if "album" in metadata:
            logging.debug(f'setting album: "{metadata["album"]}"')
            audio.tags.add(TALB(encoding=3, text=metadata["album"]))

        if "composer" in metadata:
            logging.debug(f'setting composer: "{metadata["composer"]}"')
            audio.tags.add(TCOM(encoding=3, text=metadata["composer"]))

        if "year" in metadata:
            logging.debug(f'setting year: "{metadata["year"]}"')
            audio.tags.add(TDRC(encoding=3, text=metadata["year"]))

        if "genre" in metadata:
            logging.debug(f'setting genre: "{metadata["genre"]}"')
            audio.tags.add(TCON(encoding=3, text=metadata["genre"]))

        if "ytLink" in metadata:
            logging.debug(f'setting comments: "{metadata["ytLink"]}"')
            audio.tags.add(COMM(encoding=3, lang="eng", desc="", text=metadata["ytLink"]))

        audio.save()
        logging.debug(f'metadata set for "{file_path}"')
        return True

    except Exception as e:
        logging.error(f'metadata error for "{file_path}": {e}')
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="A script to download audio from YouTube links.")

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
        logging.error("invalid action specified.")
        parser.error("invalid action specified.")


if __name__ == "__main__":
    main()
