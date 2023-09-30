import sys
import typing as t

import spotipy
from requests.exceptions import RequestException
from spotipy.client import Spotify
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

import rec_spotify.messages as m
from rec_spotify.config import Config
from rec_spotify.console import clear_lines, console
from rec_spotify.items import Collection, Track


class SpotifyClient(object):
    """
    Class for Spotify API interactions.
    """

    _client: Spotify  # type: ignore
    _device_id: str
    _user: t.Optional[dict] = {}

    @classmethod
    def init(cls) -> None:
        cls._client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=Config.CLIENT_ID,
                client_secret=Config.CLIENT_SECRET,
                redirect_uri=Config.REDIRECT_URL,
                cache_handler=CacheFileHandler(cache_path=Config.get_cache_filepath()),
                scope="user-library-modify, playlist-modify-private, user-library-read, streaming, playlist-read-private, user-read-playback-state, user-modify-playback-state",
            )
        )
        cls._set_device_id()

    @classmethod
    def get_track(cls, track: Track) -> Track:
        data: dict = cls._make_request(cls._client.track, track.id)
        track = cls._parse_track(track, data)
        return track

    @classmethod
    def get_collection(cls, collection: Collection) -> Collection:
        sp_col: dict

        if collection.kind == "playlist":
            if collection.id == Config._LIKED_ID:
                sp_col = cls._make_request(cls._client.current_user_saved_tracks)
            else:
                sp_col = cls._make_request(cls._client.playlist, collection.id)
        else:
            sp_col = cls._make_request(cls._client.album, collection.id)

        if collection.id != Config._LIKED_ID:
            collection.name = sp_col["name"]

        if collection.id == Config._LIKED_ID:
            total_tracks = sp_col["total"]
        else:
            total_tracks = sp_col["tracks"]["total"]

        for offset in range(0, total_tracks, 100):
            if collection.kind == "playlist":
                if collection.id == Config._LIKED_ID:
                    sp_col = cls._make_request(cls._client.current_user_saved_tracks)
                else:
                    sp_col = cls._make_request(
                        cls._client.playlist_tracks,
                        collection.id,
                        offset=offset,
                    )
            else:
                sp_col = cls._make_request(
                    cls._client.album_tracks,
                    collection.id,
                    offset=offset,
                )

            for track_data in sp_col["items"]:
                if collection.kind == "playlist":
                    track_data = track_data["track"]

                track_id = track_data["id"]
                if track_id is None:
                    name = track_data["name"]
                    console.print(m.TRACK_NOT_AVAILABLE.format(track_name=name))
                else:
                    track = Track(track_data["id"])
                    track.collection = collection
                    track = cls._parse_track(track, track_data)
                    collection.add_track(track)

        return collection

    @classmethod
    def create_playlist(cls, playlist: Collection) -> Collection:
        user_id = cls.get_user()["id"]
        resp = cls._make_request(
            cls._client.user_playlist_create,
            user_id,
            playlist.name,
            public=False,
        )
        playlist.id = resp["id"]
        return playlist

    @classmethod
    def add_tracks_to_playlist(
        cls, playlist: Collection, tracks: t.List[Track]
    ) -> None:
        user_id = cls.get_user()["id"]
        track_ids = [t.id for t in tracks]
        cls._make_request(
            cls._client.user_playlist_add_tracks,
            user_id,
            playlist.id,
            track_ids,
        )

    @classmethod
    def like_tracks(cls, tracks: t.List) -> None:
        track_ids = [t.id for t in tracks]
        cls._make_request(cls._client.current_user_saved_tracks_add, track_ids)

    @classmethod
    def get_user(cls) -> dict:
        if not cls._user:
            cls._user = t.cast(dict, cls._client.current_user())
        return cls._user

    @classmethod
    def get_user_playlists(cls) -> t.List[Collection]:
        sp_playlists: dict = cls._make_request(cls._client.current_user_playlists)
        collections: t.List[Collection] = []
        for playlist in sp_playlists["items"]:
            id = playlist["id"]
            collection = Collection(id, kind="playlist")
            collection = cls.get_collection(collection)
            collections.append(collection)

        # Liked Playlist
        liked = Collection(Config._LIKED_ID)
        liked.name = Config._LIKED_NAME
        collection = cls.get_collection(liked)
        collections.append(collection)
        return collections

    @classmethod
    def _parse_track(cls, track: Track, data: dict) -> Track:
        track.id = data["id"]
        track.artist = cls._extract_artist(data["artists"])
        track.name = data["name"]
        track.duration = int(data["duration_ms"]) / 1000.0  # TODO: check time
        return track

    @classmethod
    def is_playing(cls) -> bool:
        try:
            response: dict = cls._make_request(cls._client.current_playback)
            return bool(response["is_playing"])
        except TypeError:
            console.print(m.PB_ERROR)
            sys.exit(1)

    @classmethod
    def play_track(cls, track: Track) -> None:
        cls._make_request(
            cls._client.start_playback,
            uris=[track.spotify_uri],
            device_id=cls._device_id,
        )

    @classmethod
    def pause_track(cls) -> None:
        "Pause Spotify playback."
        cls._make_request(cls._client.pause_playback)

    @classmethod
    def get_track_metadata(cls, track: Track) -> dict:
        song: dict = cls._make_request(cls._client.track, track.id)
        data = {
            "title": track.name,
            "artist": track.artist,
            "album": song["album"]["name"],
            "date": song["album"]["release_date"],
            "track": song["track_number"],
            "cover_url": song["album"]["images"][0]["url"],
        }
        genres = cls._get_song_genre(song)
        if genres:
            data["genre"] = genres
        return data

    @classmethod
    def _get_song_genre(cls, data: dict) -> str:
        artist_ids = [artist["id"] for artist in data["artists"]]
        artists = cls._make_request(cls._client.artists, artist_ids)
        artists = artists["artists"]
        genres = [artist["genres"] for artist in artists if artist["genres"]]
        genres_str = "; ".join(x.title() for artist in genres for x in artist)
        return genres_str

    @classmethod
    def _extract_artist(cls, track_artists: dict) -> str:
        if len(track_artists) > 1:
            artists = ""
            for artist in track_artists:
                artists += f"{artist['name']}, "
            return artists.strip()[0:-1]
        else:
            return f"{track_artists[0]['name']}"

    @classmethod
    def _set_device_id(cls) -> None:
        "Helper method to  Spotify playback device interactively."
        devices = {}
        i = 1
        sp_devices = t.cast(dict, cls._client.devices())
        for device in sp_devices["devices"]:
            devices[i] = (device["id"], device["name"])
            i += 1

        console.print(m.SELECT_SPOTIFY_DEVICE)
        idx = 1
        for idx, device in devices.items():
            print(f"{idx}. {device[1]} | ID: {device[0]}")
            idx += 1

        choice = int(console.input("Select: "))
        cls._device_id = devices[choice][0]
        clear_lines(idx + 1)

    @classmethod
    @t.no_type_check
    def _make_request(cls, method, *args, **kwarsg) -> t.Any:
        "Helper method to make API request."
        while True:
            try:
                resp = method(*args, **kwarsg)
                return resp
            except RequestException as ex:
                console.print(m.REQ_ERROR.format(error=ex))
            except spotipy.exceptions.SpotifyException as ex:
                console.print(m.REQ_ERROR.format(error=ex))
                sys.exit(1)

    @classmethod
    def close(cls) -> None:
        cls._client.pause_playback(device_id=cls._device_id)
