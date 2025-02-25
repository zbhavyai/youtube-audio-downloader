from .config import get_logger

logger = get_logger(__name__)


def format_multiple_artists(artists: str) -> str:
    """
    Splits on ',', trims spaces, and joins using ' / '.
    Args:
        artists (str): A string of multiple artists or composers separated by a comma.
    Returns:
        str: A single string of artists or composers separated by a ' / '.
    """
    logger.debug(f'formatting multiple artists: "{artists}"')

    if not artists:
        return ""

    return " / ".join(part.strip() for part in artists.split(",")) if artists else ""
