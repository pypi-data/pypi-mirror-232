import datetime
from json import JSONDecodeError

import eyed3
import requests

from rec_spotify.items import Track


class Lyrics(object):
    "Class for finding and embedding lyrics in audio files."

    API_ENDPOINT = "https://spotify-lyric-api.herokuapp.com/?trackid={track_id}"
    BASE_DATETIME = datetime.datetime(1970, 1, 1)

    @classmethod
    def find(cls, track: Track) -> str | None:
        """
        Find lyrics for a track via API and return as string

        This method uses the API_ENDPOINT attribute to send a request to the
        lyrics API and retrieve the lyrics for the specified track.
        """
        resp = requests.get(cls.API_ENDPOINT.format(track_id=track.id))

        try:
            resp = resp.json()
            if resp["error"]:
                return None
        except JSONDecodeError:
            return None

        idx = 0
        lyrics = []
        for line in resp["lines"]:
            start = cls.to_format(line["startTimeMs"])
            try:
                end = cls.to_format(resp["lines"][idx + 1]["startTimeMs"])
            except IndexError:
                continue
            words = line["words"]
            lyrics.append((idx + 1, start, end, words))
            idx += 1

        lyrics_str = ""
        unsynced = resp["syncType"] == "UNSYNCED"
        for fragment in lyrics:
            if unsynced:
                lyrics_str += f"{fragment[3]}\n"
            else:
                to_format = fragment[1].replace(",", ".")
                lyrics_str += f"[{to_format}] {fragment[3]}\n"

        return lyrics_str

    @classmethod
    def embed_lyrics(cls, track: Track, lyrics: str, field: str = "LYRICS") -> None:
        "Embeds the specified lyrics in the track file."
        file = eyed3.load(track.filepath)
        file.tag.lyrics.set(lyrics)  # type: ignore
        file.tag.save()  # type: ignore

    @classmethod
    def to_format(cls, time: str) -> str:
        """
        Converts a time string to a formatted string.

        This method converts a time string in milliseconds to a formatted
        string in the format "M:SS.sss".
        """
        delta = datetime.timedelta(0, 0, 0, int(time))
        return (cls.BASE_DATETIME + delta).strftime("%#M:%S.%f")[:-3]
