import math
import re
import shutil
import tempfile
import typing as t

import requests
from pydub import AudioSegment
from pydub.silence import detect_leading_silence


def parse_spotify_url(url: str) -> tuple[str, str] | None:
    "Parses a Spotify URL and returns the type of link and its ID."
    match = re.search(r"open\.spotify\.com/(track|album|playlist)/(\w+)", url.strip())
    if match:
        link_type = match.group(1)
        link_id = match.group(2)
        return link_type, link_id
    else:
        return None


def download_cover(url: str) -> tempfile._TemporaryFileWrapper:
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    response = requests.get(url, stream=True)
    with open(tmp_file.name, "w+b") as out_file:
        shutil.copyfileobj(response.raw, out_file)

    tmp_file.close()
    return tmp_file


def get_estimate_time(seconds: float) -> str:
    """
    Converts a duration in seconds to a human readable
    string with hours, minutes, and seconds.
    """
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    seconds = math.floor((seconds % 3600) % 60)

    return f"{int(hours)} hours {int(minutes)} minutes and {int(seconds)} seconds."


def clear_unwanted(text: str) -> str:
    "Clear unwanted characters from a string."
    text = text.strip()
    unwanted_chars = r" /\:*?\"<>|%^&!()'."
    table = str.maketrans({char: "_" for char in unwanted_chars})
    text = text.translate(table)
    return text


@t.no_type_check
def trim_silence(audio: AudioSegment) -> AudioSegment:
    "Remove leading and trailing silence from an audio segment."

    def trim_leading_silence(x):
        return x[detect_leading_silence(x) :]  # noqa

    def trim_trailing_silence(x):
        reversed_x = x.reverse()
        trimmed = trim_leading_silence(reversed_x)
        return trimmed.reverse()

    def strip_silence(x):
        trimmed_leading = trim_leading_silence(x)
        trimmed_trailing = trim_trailing_silence(trimmed_leading)
        return trimmed_trailing

    stripped: AudioSegment = strip_silence(audio)
    return stripped
