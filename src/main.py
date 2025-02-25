#!/usr/bin/env python3

import argparse

from .config import OUTPUT_DIR, VERSION, get_logger
from .csv_handler import read_csv
from .downloader import download_audio, download_audio_from_csv
from .metadata import clean_metadata, print_metadata
from .table import display_data

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="youtube_audio_downloader",
        description="A script to download audio from YouTube links.",
        epilog="Made by https://zbhavyai.github.io",
    )

    parser.add_argument("--csv", action="store", help="The CSV file to parse")
    parser.add_argument("--download", action="store_true", help="Download audio from YouTube links specified in a CSV file")
    parser.add_argument("--testcsv", action="store_true", help="Print the data from the CSV file")
    parser.add_argument("--url", action="store", help="Download audio from the given YouTube URL")
    parser.add_argument("--filename", action="store", help="Use the filename for the downloaded audio file")
    parser.add_argument("--metadata", action="store", help="Path of the input file for processing")
    parser.add_argument("--clean", action="store", help="Clean all metadata from given audio files")
    parser.add_argument("--version", action="store_true", help="Print the version of the script")

    args = parser.parse_args()

    if args.testcsv and args.csv:
        headers, data = read_csv(args.csv)
        display_data(headers, data)
    elif args.url and args.filename:
        download_audio(args.url, "", "", args.filename, OUTPUT_DIR)
    elif args.download and args.csv:
        download_audio_from_csv(args.csv, OUTPUT_DIR)
    elif args.metadata:
        print_metadata(args.metadata)
    elif args.clean:
        clean_metadata(args.clean)
    elif args.version:
        logger.info(f"version: {VERSION}")
    else:
        logger.error("Invalid action specified.")
        parser.error("Invalid action specified.")


if __name__ == "__main__":
    main()
