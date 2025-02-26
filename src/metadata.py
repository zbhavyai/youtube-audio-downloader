import os
from typing import Dict, List

from mutagen import File
from mutagen.id3 import COMM, ID3, TALB, TCOM, TCON, TDRC, TIT2, TPE1
from mutagen.mp3 import MP3

from .config import get_logger
from .table import display_data

logger = get_logger(__name__)


def print_metadata(file_or_directory_path: str) -> None:
    """
    Prints relevant metadata for an audio file or directory.
    Args:
        file_or_directory_path (str): The path to an audio file or a directory containing audio files.
    Returns:
        None
    """
    logger.info(f'getting metadata for "{file_or_directory_path}"')

    if os.path.isfile(file_or_directory_path):
        display_data(_get_headers(), _get_metadata_file(file_or_directory_path))

    elif os.path.isdir(file_or_directory_path):
        display_data(_get_headers(), _get_metadata_directory(file_or_directory_path))

    else:
        logger.error(f'"{file_or_directory_path}" is not a valid file or directory')


def clean_metadata(file_or_directory_path: str) -> bool:
    """
    Removes all metadata from an audio file or directory.
    Args:
        file_or_directory_path (str): The path to an audio file or a directory containing audio files.
    Returns:
        bool: True if metadata was removed successfully, False otherwise.
    """
    logger.info(f'cleaning metadata for "{file_or_directory_path}"')

    if os.path.isfile(file_or_directory_path):
        return _clean_metadata_file(file_or_directory_path)
    elif os.path.isdir(file_or_directory_path):
        return _clean_metadata_directory(file_or_directory_path)
    else:
        logger.error(f'"{file_or_directory_path}" is not a valid file or directory')
        return False


def set_metadata(file_path: str, title: str, artist: str, album: str, composer: str, year: int, genre: str, comments: str) -> bool:
    """
    Sets the metadata for an MP3 file.
    Args:
        file_path (str): The path to the MP3 file.
        title (str): The title of the track.
        artist (str): The artist of the track.
        album (str): The album name.
        composer (str): The composer of the track.
        year (int): The year of release.
        genre (str): The genre of the track.
        comments (str): Additional comments, such as a YouTube link.
    Returns:
        bool: `True` if metadata was set successfully, `False` otherwise.
    """
    logger.debug(f'setting metadata for "{file_path}"')

    if not os.path.isfile(file_path):
        logger.error(f'file "{file_path}" does not exist')
        return False

    try:
        audio = MP3(file_path, ID3=ID3)
        audio.tags = ID3()

        if title:
            logger.debug(f'setting title: "{title}"')
            audio.tags.add(TIT2(encoding=3, text=title))

        if artist:
            logger.debug(f'setting artist: "{artist}"')
            audio.tags.add(TPE1(encoding=3, text=artist))

        if album:
            logger.debug(f'setting album: "{album}"')
            audio.tags.add(TALB(encoding=3, text=album))

        if composer:
            logger.debug(f'setting composer: "{composer}"')
            audio.tags.add(TCOM(encoding=3, text=composer))

        if year:
            logger.debug(f'setting year: "{year}"')
            audio.tags.add(TDRC(encoding=3, text=year))

        if genre:
            logger.debug(f'setting genre: "{genre}"')
            audio.tags.add(TCON(encoding=3, text=genre))

        if comments:
            logger.debug(f'setting comments: "{comments}"')
            audio.tags.add(COMM(encoding=3, lang="eng", desc="", text=comments))

        audio.save()
        logger.info(f'metadata set for "{file_path}"')
        return True

    except Exception as e:
        logger.error(f'metadata error for "{file_path}": {e}')
        return False


def _clean_metadata_directory(directory_path: str) -> bool:
    """
    Removes all metadata from audio files in a directory.
    Args:
        directory_path (str): The directory containing audio files.
    Returns:
        bool: True if metadata was successfully removed from all the MP3 files, False otherwise.
    """
    logger.debug(f'cleaning metadata in "{directory_path}"')

    if not os.path.isdir(directory_path):
        logger.error(f'directory "{directory_path}" does not exist')
        return False

    allCleaned = True

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".mp3"):
                if not _clean_metadata_file(os.path.join(root, file)):
                    allCleaned = False

    return allCleaned


def _clean_metadata_file(file_path: str) -> bool:
    """
    Removes all metadata from an audio file.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        bool: True if metadata was successfully removed, False otherwise.
    """
    logger.debug(f'cleaning metadata for "{file_path}"')

    if not os.path.isfile(file_path):
        logger.error(f'file "{file_path}" does not exist')
        return False

    try:
        audio = File(file_path, easy=True)
        if audio is None:
            logger.error(f'corrupt file "{file_path}"')
            return False

        audio.delete()
        audio.save()
        logger.info(f'cleaned metadata for "{file_path}"')
        return True

    except Exception as e:
        logger.error(f"failed to clean metadata for {file_path}: {e}")
        return False


def _get_metadata_file(file_path: str) -> List[Dict[str, str]]:
    """
    Prints relevant metadata for an MP3 file.
    Args:
        file_path (str): The path to the MP3 file.
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the metadata for the MP3 file.
    """
    logger.debug(f'printing metadata for "{file_path}"')

    obj = {
        "file": os.path.basename(file_path),
        "title": "",
        "artist": "",
        "album": "",
        "composer": "",
        "year": "",
        "genre": "",
        "comments": "",
    }

    if not os.path.isfile(file_path):
        logger.error(f'file "{file_path}" does not exist')
        return [obj]

    try:
        audio = MP3(file_path, ID3=ID3)
        tags = audio.tags

        obj["title"] = tags.get("TIT2", "")
        obj["artist"] = tags.get("TPE1", "")
        obj["album"] = tags.get("TALB", "")
        obj["composer"] = tags.get("TCOM", "")
        obj["year"] = tags.get("TDRC", "")
        obj["genre"] = tags.get("TCON", "")
        obj["comments"] = " ".join(next((comm.text for comm in tags.getall("COMM") if comm.lang == "eng"), []))

    except Exception as e:
        logger.error(f'metadata error for "{file_path}": {e}')

    return [obj]


def _get_metadata_directory(directory_path: str) -> List[Dict[str, str]]:
    """
    Prints relevant metadata for all MP3 files in a directory.
    Args:
        directory_path (str): The path to the directory containing MP3 files.
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the metadata for all MP3 files in the directory.
    """
    logger.debug(f'printing metadata in "{directory_path}"')

    if not os.path.isdir(directory_path):
        logger.error(f'directory "{directory_path}" does not exist')
        return False

    obj = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".mp3"):
                obj.extend(_get_metadata_file(os.path.join(root, file)))

    return obj


def _get_headers() -> List[str]:
    """
    Returns the headers for the metadata table.
    Returns:
        List[str]: A list of strings representing the headers for tabular display.
    """
    return ["file", "title", "artist", "album", "composer", "year", "genre", "comments"]
