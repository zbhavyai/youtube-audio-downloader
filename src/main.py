#!/usr/bin/env python3

import argparse

from .config import OUTPUT_DIR, VERSION, get_logger
from .csv_handler import read_csv
from .downloader import download_audio, download_audio_from_csv
from .metadata import clean_metadata, print_metadata, set_metadata
from .table import display_data

logger = get_logger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for the script.
    Returns:
        argparse.ArgumentParser: The argument parser
    """

    parser = argparse.ArgumentParser(
        prog="youtube_audio_downloader",
        description="A script to download audio from YouTube links.",
        epilog="Made by https://zbhavyai.github.io",
    )

    subparsers = parser.add_subparsers(dest="group", required=True, help="Select a group")

    # metadata
    metadata_parser = subparsers.add_parser("metadata", help="Manipulate metadata of audio files")
    metadata_subparsers = metadata_parser.add_subparsers(dest="action", required=True, help="Metadata actions")

    meta_print = metadata_subparsers.add_parser("print", help="Print metadata of a file or directory")
    meta_print.add_argument("--file", required=True, help="File or directory path")

    meta_clean = metadata_subparsers.add_parser("clean", help="Clean metadata from a file or directory")
    meta_clean.add_argument("--file", required=True, help="File or directory path")

    meta_set = metadata_subparsers.add_parser("set", help="Set metadata for a file or directory")
    meta_set.add_argument("--file", required=True, help="File or directory path")
    meta_set.add_argument("--title", required=False, default="", help="Title of the audio")
    meta_set.add_argument("--album", required=False, default="", help="Album name")
    meta_set.add_argument("--artist", required=False, default="", help="Artist name")
    meta_set.add_argument("--composer", required=False, default="", help="Composer name")
    meta_set.add_argument("--year", required=False, default="", help="Year of release")
    meta_set.add_argument("--comment", required=False, default="", help="Comment")
    meta_set.add_argument("--genre", required=False, default="", help="Genre")

    # download
    download_parser = subparsers.add_parser("download", help="Download audio from YouTube URL")
    download_parser.add_argument("--url", required=True, help="YouTube video URL")
    download_parser.add_argument("--output", required=True, help="Output file path")

    # trim
    trim_parser = subparsers.add_parser("trim", help="Trim an audio file")
    trim_parser.add_argument("--file", required=True, help="Input file path")
    trim_parser.add_argument("--start", required=True, help="Start time (in seconds)")
    trim_parser.add_argument("--end", required=True, help="End time (in seconds)")
    trim_parser.add_argument("--output", required=True, help="Output file path")

    # csv
    csv_parser = subparsers.add_parser("csv", help="Process CSV file")
    csv_parser.add_argument("--file", required=True, help="CSV file path")
    csv_parser.add_argument("--print", action="store_true", help="Print CSV data")
    csv_parser.add_argument("--download", action="store_true", help="Download from CSV file")

    # version
    version_parser = subparsers.add_parser("version", help="Print version")

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.group == "metadata":
        if args.action == "print":
            print_metadata(args.file)
        elif args.action == "clean":
            clean_metadata(args.file)
        elif args.action == "set":
            set_metadata(args.file, args.title, args.artist, args.year, args.composer, args.comment, args.genre, args.album)

    elif args.group == "download":
        download_audio(args.url, args.output, OUTPUT_DIR)

    elif args.group == "trim":
        # trim_audio(args.file, args.start, args.end, args.output)
        logger.error("Trimming is not implemented yet.")

    elif args.group == "csv":
        if args.print:
            headers, data = read_csv(args.file)
            display_data(headers, data)
        elif args.download:
            download_audio_from_csv(args.file)

    elif args.group == "version":
        logger.info(f"version: {VERSION}")

    else:
        logger.error("Invalid action specified.")
        parser.error("Invalid action specified.")


if __name__ == "__main__":
    main()
