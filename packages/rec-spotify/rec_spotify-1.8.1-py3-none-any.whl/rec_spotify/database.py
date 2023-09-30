import sqlite3
import typing as t

import rec_spotify.messages as m
from rec_spotify.config import Config
from rec_spotify.console import console
from rec_spotify.items import Collection, Track


class Database(object):
    "Database class for working with tracks and playlists."

    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor

    _init: bool = False

    CREATE_TABLES_SQL = """
        CREATE TABLE IF NOT EXISTS playlists (
            id TEXT PRIMARY KEY,
            name TEXT,
            dir_path TEXT
        );
        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY,
            artist TEXT,
            name TEXT,
            playlist_id INTEGER,
            duration INT DEFAULT 0,
            filename TEXT,
            filepath TEXT,
            downloaded BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """

    @classmethod
    def init_db(cls) -> None:
        "Initialize the database by creating a connection and initializing the schema."

        cls._connection = sqlite3.connect(Config.get_database_filepath())
        cls._cursor = cls._connection.cursor()
        cls._cursor.execute("PRAGMA foreign_keys = ON")
        cls._cursor.executescript(cls.CREATE_TABLES_SQL)
        cls._connection.commit()
        console.print(m.DATABASE_OK)
        cls._init = True

    @classmethod
    def get_playlist(cls, id: str) -> t.Union[Collection, None]:
        "Get playlist by id, returns Collection object or None if not found"
        sql = "SELECT * FROM playlists WHERE id = ?;"
        cls._cursor.execute(sql, (id,))
        row = cls._cursor.fetchone()
        if row:
            return cls._parse_playlist_row(row)
        return None

    @classmethod
    def get_playlists(cls) -> t.List[Collection]:
        "Get all playlists, returns list of Collection objects."
        sql = "SELECT * FROM playlists;"
        cls._cursor.execute(sql)
        rows = cls._cursor.fetchall()
        playlists: t.List[Collection] = []
        for row in rows:
            playlists.append(cls._parse_playlist_row(row))
        return playlists

    @classmethod
    def get_playlist_tracks(cls, playlist: Collection) -> t.List[Track]:
        "Get tracks for a given playlist"
        sql = "SELECT * FROM tracks WHERE playlist_id = ?;"
        cls._cursor.execute(sql, (playlist.id,))
        tracks: t.List[Track] = []
        rows = cls._cursor.fetchall()
        for row in rows:
            tracks.append(cls._parse_track_row(row))
        return tracks

    @classmethod
    def add_playlist(cls, playlist: Collection) -> None:
        "Add new playlist to database"
        sql = "INSERT INTO playlists VALUES (?, ?, ?)"
        cls._cursor.execute(sql, (playlist.to_sql_fields()))
        cls._connection.commit()

    @classmethod
    def update_playlist(cls, playlist: Collection) -> None:
        "Update existing playlist in database"
        sql = "UPDATE playlists SET name = ?, dir_path = ? WHERE id = ?"
        cls._cursor.execute(sql, (playlist.name, playlist.dirpath, playlist.id))
        cls._connection.commit()

    @classmethod
    def update_playlist_id(cls, oid: str, nid):
        sql = "UPDATE playlists SET id = ? WHERE id = ?"
        cls._cursor.execute(sql, (nid, oid))
        cls._connection.commit()

    @classmethod
    def delete_playlist(cls, playlist: Collection) -> None:
        "Delete playlist from database"
        sql = "DELETE FROM playlists WHERE id = ?"
        cls._cursor.execute(sql, (playlist.id,))
        cls._connection.commit()

    @classmethod
    def get_playlists_deleted(cls, ids: list) -> t.List[Collection]:
        "Get playlists that were deleted. This queries for playlists that are not in the given ids list."
        ids_str = ",".join(f"'{value}'" for value in ids)
        sql = f"select * from playlists where id not in ({ids_str})"
        cls._cursor.execute(sql)
        rows = cls._cursor.fetchall()
        deleted: t.List[Collection] = []
        for row in rows:
            deleted.append(cls._parse_playlist_row(row))
        return deleted

    @classmethod
    def _parse_playlist_row(cls, row: tuple) -> Collection:
        "Parse a playlist data row into a Collection object."
        playlist = Collection(id=row[0])
        playlist.name = row[1]
        playlist.dirpath = row[2]
        return playlist

    @classmethod
    def get_track(cls, id: str, playlist_id: str = "") -> Track | None:
        "Get track by id, returns Track or None if not found"
        if playlist_id:
            sql = "SELECT * FROM tracks WHERE id = ? AND playlist_id = ?;"
            params = (id, playlist_id)
        else:
            sql = "SELECT * FROM tracks WHERE id = ?;"
            params = (id,)
        cls._cursor.execute(sql, params)
        row = cls._cursor.fetchone()
        if row is not None:
            return cls._parse_track_row(row)
        return None

    @classmethod
    def add_track(cls, track: Track) -> bool:
        "Add new track to database"
        sql = "INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        try:
            cls._cursor.execute(sql, (track.to_sql_fields()))
            cls._connection.commit()
            return True
        except sqlite3.IntegrityError:
            track_ex = cls.get_track(track.id)
            if track_ex is not None:
                console.print(
                    m.TRACK_DUPLICATE.format(
                        playlist_new=track.collection.name,
                        track_name=track_ex.title,
                        playlist_old=track_ex.collection.name,
                        track_path=track_ex.filepath,
                    )
                )
            return False

    @classmethod
    def get_tracks(cls, downloaded: bool = False, total: bool = False) -> t.List[Track]:
        "Get all tracks"
        if total:
            sql = "SELECT * FROM tracks;"
        else:
            sql = f"SELECT * FROM tracks WHERE downloaded = {str(downloaded).lower()};"
        cls._cursor.execute(sql)
        rows = cls._cursor.fetchall()
        tracks: t.List[Track] = []
        for row in rows:
            track = cls._parse_track_row(row)
            tracks.append(track)
        return tracks

    @classmethod
    def get_deleted_tracks(cls, ids: list, playlist: Collection) -> t.List[Track]:
        """
        Get tracks that were deleted from a playlist.
        This queries for tracks that are not in the given ids list.
        """
        ids_str = ",".join(f"'{value}'" for value in ids)
        sql = f"select * from tracks where id not in ({ids_str}) AND playlist_id = ?"
        cls._cursor.execute(sql, (playlist.id,))
        rows = cls._cursor.fetchall()
        deleted: t.List[Track] = []
        for row in rows:
            deleted.append(cls._parse_track_row(row))
        return deleted

    @classmethod
    def delete_track(cls, track: Track) -> None:
        "Delete track from database"
        sql = "DELETE FROM tracks WHERE id = ?"
        cls._cursor.execute(sql, (track.id,))
        cls._connection.commit()

    @classmethod
    def mark_downloaded(cls, track: Track, state: bool = True) -> None:
        "Update downloaded status of track"
        sql = f"UPDATE tracks SET downloaded = {str(state).lower()} WHERE id = ?"
        cls._cursor.execute(sql, (track.id,))
        cls._connection.commit()

    @classmethod
    def _parse_track_row(cls, row: tuple) -> Track:
        "Parse a track data row into a Track object."
        track = Track(row[0])
        track.artist = row[1]
        track.name = row[2]
        track.collection = cls.get_playlist(row[3])  # type: ignore
        track.duration = row[4]
        track.filename = row[5]
        track.filepath = row[6]
        track.downloaded = bool(row[7])
        return track

    @classmethod
    def close(cls) -> None:
        "Close database connection"
        if cls._init:
            cls._connection.commit()
            cls._connection.close()
