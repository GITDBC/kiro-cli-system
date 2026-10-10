"""
Network access shared by every documentation source.

A single fetch helper is the whole network surface of the tool. Keeping
it alone in this module gives the test suite one seam to replace, which
is what makes the suite offline by construction.
"""

# Standard libraries
import time
import urllib.request
from typing import Final

USER_AGENT: Final[str] = "work-agents-docsync/1.0"
TIMEOUT: Final[int] = 15
MAX_RETRIES: Final[int] = 3


def fetch(url: str, retries: int = MAX_RETRIES) -> bytes:
    """
    Fetch a URL with timeout and exponential backoff retry.

    Args:
        url: Absolute URL to download.
        retries: Maximum number of attempts before giving up.

    Returns:
        Raw response body as bytes.

    Raises:
        OSError: If all attempts fail to retrieve the URL.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as resp:  # noqa: S310
                body: bytes = resp.read()
                return body
        except OSError as error:
            if attempt == retries - 1:
                raise
            wait = 2**attempt
            print(
                f"  Retry {attempt + 1}/{retries} for {url} "
                f"({error}), waiting {wait}s..."
            )
            time.sleep(wait)
    error_message = f"Unable to fetch {url} after {retries} attempts."
    raise OSError(error_message)
