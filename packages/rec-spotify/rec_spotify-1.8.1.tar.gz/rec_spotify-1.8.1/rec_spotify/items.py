import os
import shutil
import typing as t

from rec_spotify.config import Config
from rec_spotify.utils import clear_unwanted


class Collection(object):
    """Represents playlist or album."""

    def __init__(self, id: str, kind: str = "playlist") -> None:
        self._id = id
        self._kind = kind
        self._name: t.Optional[str] = None
        self._dirpath: t.Optional[str] = None
        self._tracks: t.List[Track] = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def kind(self) -> str:
        return self._kind

    @kind.setter
    def kind(self, value: str) -> None:
        self._value = value

    @property
    def dirpath(self) -> str | None:
        return self._dirpath

    @dirpath.setter
    def dirpath(self, value: str) -> None:
        self._dirpath = value

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = clear_unwanted(value)

    def get_tracks(self) -> t.List["Track"]:
        return self._tracks

    def add_track(self, track: "Track") -> None:
        self._tracks.append(track)

    @property
    def track_count(self) -> int:
        return len(self._tracks)

    def to_sql_fields(self) -> tuple:
        return (
            self.id,
            self.name,
            self.dirpath,
        )

    def gen_dir_path(self) -> str:
        dirpath = os.path.join(Config.MUSIC_DIR, self.name)  # type: ignore
        return dirpath

    def create_dir(self) -> None:
        dirpath = self.gen_dir_path()
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
            self._dirpath = dirpath

    def change_name(self, new_name: str) -> None:
        old_dir = self.dirpath
        self._name = new_name
        new_dir = self.gen_dir_path()
        if old_dir and os.path.exists(old_dir):
            os.rename(old_dir, new_dir)
        self._dirpath = new_dir

    def delete(self) -> None:
        try:
            shutil.rmtree(t.cast(str, self.dirpath))
        except FileNotFoundError:
            pass

    def __str__(self) -> str:
        return f"Playlist: {self.name}"


class Track(object):

    """
    A class representing a track in the rec_spotify module.
    """

    def __init__(self, id: str) -> None:
        """
        Initializes a new Track object.

        This method sets all instance-level attributes to None.
        """
        self._id = id
        self._artist: t.Optional[str] = None
        self._name: t.Optional[str] = None
        self._collection: t.Optional[Collection] = None
        self._duration: float = 0.0
        self._filename: t.Optional[str] = None
        self._filepath: t.Optional[str] = None
        self._downloaded: bool = False

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value.strip()

    @property
    def artist(self) -> str | None:
        return self._artist

    @artist.setter
    def artist(self, value: str) -> None:
        self._artist = value.strip()

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def collection(self) -> Collection | None:
        return self._collection

    @collection.setter
    def collection(self, value: Collection) -> None:
        self._collection = value

    @property
    def duration(self) -> float:
        "Returns the duration of the track in seconds."
        return self._duration

    @duration.setter
    def duration(self, value: float) -> None:
        self._duration = value

    @property
    def title(self) -> str:
        """
        Returns a formatted title for the track.

        The title is formatted as "artist - name".
        """
        return f"{self.artist} - {self.name}"

    @property
    def filename(self) -> str | None:
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value

    @property
    def filepath(self) -> str | None:
        return self._filepath

    @filepath.setter
    def filepath(self, value: str) -> None:
        self._filepath = value

    @property
    def spotify_uri(self) -> str:
        return f"spotify:track:{self.id}"

    @property
    def downloaded(self) -> bool:
        return self._downloaded

    @downloaded.setter
    def downloaded(self, value: bool) -> None:
        self._downloaded = value

    def to_sql_fields(self) -> tuple:
        return (
            self.id,
            self.artist,
            self.name,
            self.collection.id,  # type: ignore
            self.duration,
            self.filename,
            self.filepath,
            self.downloaded,
        )

    def set_download_path(self) -> None:
        self._gen_filename()
        self._gen_filepath()

    def _gen_filename(self) -> str:
        """
        Generates a filename for the track.

        The filename is generated based on the track title and audio format
        specified in the Config class.
        """
        filename = f"{clear_unwanted(self.title)}.{Config.AUDIO_FORMAT}"
        self._filename = filename
        return self._filename

    def _gen_filepath(self) -> str:
        """
        Generate the filepath for the track.

        The filepath is the track filename appended to the music directory path
        and collection name directory (if available).
        """
        col_name = ""
        if self.collection:
            if self.collection.name is not None:
                col_name = self.collection.name

        filepath = os.path.join(Config.MUSIC_DIR, col_name, self.filename)  # type: ignore
        self._filepath = os.path.normpath(filepath)
        return self._filepath

    def delete(self) -> None:
        try:
            os.remove(t.cast(str, self.filepath))  # TODO
        except FileNotFoundError:
            pass

    def __str__(self) -> str:
        return f"Track: {self.title}"
