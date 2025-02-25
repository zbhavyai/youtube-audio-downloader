#!/usr/bin/env python3

"""
Author: zbhavyai@gmail.com
"""

import logging
import os
from typing import Dict

from mutagen import File
from mutagen.id3 import COMM, ID3, TALB, TCOM, TCON, TDRC, TIT2, TPE1
from mutagen.mp3 import MP3

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


def clean_metadata(file_path: str) -> bool:
    """
    Removes all metadata from an audio file.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        bool: True if metadata was successfully removed, False otherwise.
    """
    logging.debug(f'cleaning metadata for "{file_path}"')

    if not os.path.exists(file_path):
        logging.error(f'file "{file_path}" does not exist')
        return False

    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logging.error(f'corrupt file "{file_path}"')
            return False

        audio.delete()
        audio.save()
        logging.info(f'cleaned metadata for "{file_path}"')
        return True

    except Exception as e:
        logging.error(f"failed to clean metadata for {file_path}: {e}")
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
