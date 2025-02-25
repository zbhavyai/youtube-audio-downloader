import os

from mutagen import File
from mutagen.id3 import COMM, ID3, TALB, TCOM, TCON, TDRC, TIT2, TPE1
from mutagen.mp3 import MP3

from .config import get_logger

logger = get_logger(__name__)


def clean_metadata(file_path: str) -> bool:
    """
    Removes all metadata from an audio file.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        bool: True if metadata was successfully removed, False otherwise.
    """
    logger.debug(f'cleaning metadata for "{file_path}"')

    if not os.path.exists(file_path):
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


def clean_metadata_directory(target_directory: str) -> None:
    """
    Removes all metadata from audio files in a directory.
    Args:
        target_directory (str): The directory containing audio files.
    Returns:
        None
    """
    logger.debug(f'cleaning metadata in "{target_directory}"')

    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(".mp3"):
                clean_metadata(os.path.join(root, file))


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

    if not os.path.exists(file_path):
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
        logger.debug(f'metadata set for "{file_path}"')
        return True

    except Exception as e:
        logger.error(f'metadata error for "{file_path}": {e}')
        return False
