import argparse
import os
import sys
import typing as t

import rec_spotify.messages as m
from rec_spotify.config import RUN_TYPE, Config
from rec_spotify.console import console
from rec_spotify.database import Database
from rec_spotify.items import Collection, Track
from rec_spotify.lyrics import Lyrics
from rec_spotify.recorder import Recorder
from rec_spotify.spotify import SpotifyClient
from rec_spotify.utils import (
    download_cover,
    get_estimate_time,
    parse_spotify_url,
    trim_silence,
)


class Manager(object):
    @classmethod
    def sync(cls) -> None:
        "Synchronize Spotify content with local database"

        # Print db stats
        playlists = Database.get_playlists()
        tracks = Database.get_tracks(total=True)
        undownloaded = list(filter(lambda x: not x.downloaded, tracks))
        console.print(
            m.STATS.format(
                playlists_count=len(playlists),
                tracks_count=len(tracks),
                undownloaded_count=len(undownloaded),
            )
        )
        # Sync Playlists
        process_play_ids = []
        sp_playlists = SpotifyClient.get_user_playlists()
        for sp_playlist in sp_playlists:
            loc_playlist = Database.get_playlist(sp_playlist.id)
            if loc_playlist is None:
                sp_playlist.create_dir()
                Database.add_playlist(sp_playlist)
                console.print(m.NEW_PLAYLIST.format(playlist=sp_playlist.name))

            elif sp_playlist.name != loc_playlist.name:
                old_name = loc_playlist.name
                loc_playlist.change_name(str(sp_playlist.name))
                Database.update_playlist(loc_playlist)
                console.print(
                    m.RENAME_PLAYLIST.format(
                        from_name=old_name,
                        to_name=sp_playlist.name,
                    )
                )
            process_play_ids.append(sp_playlist.id)

        deleted_playlists = Database.get_playlists_deleted(process_play_ids)
        for playlist in deleted_playlists:
            tracks_to_delete = Database.get_playlist_tracks(playlist)
            playlist.delete()
            Database.delete_playlist(playlist)
            console.print(m.DEL_PLAYLIST.format(playlist=playlist.name))
            for track in tracks_to_delete:
                track.delete()
                console.print(m.DEL_TRACK.format(track_title=track.title))

        # Sync Tracks
        tracks_to_download: t.Set[Track] = set()
        for sp_playlist in sp_playlists:
            processed_track_ids = []
            for sp_track in sp_playlist.get_tracks():
                loc_track = Database.get_track(sp_track.id, sp_playlist.id)
                if loc_track is None:
                    sp_track.set_download_path()
                    added = Database.add_track(sp_track)
                    if added:
                        console.print(m.NEW_TRACK.format(track_title=sp_track.title))

                processed_track_ids.append(sp_track.id)

            to_delete = Database.get_deleted_tracks(processed_track_ids, sp_playlist)
            for track in to_delete:
                track.delete()
                Database.delete_track(track)
                console.print(m.DEL_TRACK.format(track_title=track.title))

        undownloaded = Database.get_tracks(downloaded=False)
        tracks_to_download = tracks_to_download.union(undownloaded)
        if len(undownloaded) == 0:
            console.print(m.SYNC_OK)
            sys.exit(0)

        # Recording
        total_time = get_estimate_time(
            sum(track.duration for track in tracks_to_download)
        )
        console.print(
            m.SYNC_START.format(
                total_time=total_time,
                track_count=len(tracks_to_download),
            )
        )
        console.print()
        console.rule(":radio: Recorder Log")
        for track in tracks_to_download:
            cls._record_and_save(track)
            Database.mark_downloaded(track, state=True)

    @classmethod
    def recreate(cls):
        local_playlists = Database.get_playlists()
        for playlist in local_playlists:
            tracks = Database.get_playlist_tracks(playlist)
            if playlist.id == Config._LIKED_ID:
                if tracks:
                    SpotifyClient.like_tracks(tracks)
            else:
                old_id = playlist.id
                playlist = SpotifyClient.create_playlist(playlist)
                Database.update_playlist_id(old_id, playlist.id)
                SpotifyClient.add_tracks_to_playlist(playlist, tracks)

    @classmethod
    def record_track(cls, track: Track) -> None:
        "Record and save single track."
        track = SpotifyClient.get_track(track)
        console.print(
            m.JOB_TYPE.format(
                job_type="track",
                name=track.title,
            )
        )
        console.print()
        console.rule(":radio: Recorder Log")
        cls._record_and_save(track)

    @classmethod
    def record_collection(cls, collection: Collection) -> None:
        "Record and save all tracks in a collection."
        collection = SpotifyClient.get_collection(collection)
        collection.create_dir()
        console.print(
            m.JOB_TYPE.format(
                job_type=collection.kind,
                name=collection.name,
            )
        )
        total_time = get_estimate_time(
            sum(track.duration for track in collection.get_tracks())
        )

        console.print(
            m.SYNC_START.format(
                total_time=total_time,
                track_count=collection.track_count,
            )
        )
        console.print()
        console.rule(":radio: Recorder Log")
        for track in collection.get_tracks():
            cls._record_and_save(track)

    @classmethod
    def _record_and_save(cls, track: Track) -> None:
        "Helper method to record and save a single track."
        metadata = SpotifyClient.get_track_metadata(track)
        song_cover = download_cover(metadata["cover_url"])
        recorded_obj = Recorder.record(track)
        track.set_download_path()
        if Config.TRIM_SILENCE:
            recorded_obj = trim_silence(recorded_obj)
        recorded_obj.export(
            out_f=track.filepath,
            format=Config.AUDIO_FORMAT,
            codec="libmp3lame",
            parameters=["-b:a", "320k", "-abr", "1"],
            tags=metadata,
            cover=song_cover.name,
        )
        lyrics = Lyrics.find(track)
        if lyrics is not None:
            Lyrics.embed_lyrics(track, lyrics)

        
        if lyrics:
            console.print(m.TRACK_SAVED.format(lyrics='LYRICS', filepath=track.filepath))
        else:
            console.print(m.TRACK_SAVED.format(lyrics='NOLYRICS', filepath=track.filepath))
        
        os.remove(song_cover.name)
        console.print()

    @classmethod
    def database_cleanup(cls) -> None:
        tracks = Database.get_tracks(total=True)
        fixed = 0
        for track in tracks:
            if track.downloaded and track.filepath:
                if not os.path.exists(track.filepath):
                    console.print(m.TRACK_NO_LOCAL.format(track=track))
                    Database.mark_downloaded(track, state=False)
                    fixed += 1
        if fixed == 0:
            console.print(m.DB_CHECK_OK)

    @classmethod
    def init(cls, mode: RUN_TYPE, args: argparse.Namespace):
        if mode == RUN_TYPE.INIT:
            Config.init()
        elif mode == RUN_TYPE.SYNC:
            Database.init_db()
            Config.init()
            SpotifyClient.init()
            Recorder.init()
            cls.sync()
        elif mode == RUN_TYPE.SINGLE:
            Config.init()
            match = parse_spotify_url(args.url)
            if match is not None:
                link_type, id = match
                Config.MUSIC_DIR = args.path
                SpotifyClient.init()
                Recorder.init()
                if link_type == "track":
                    track = Track(id)
                    cls.record_track(track)
                else:
                    collection = Collection(id, kind=link_type)
                    cls.record_collection(collection)
            else:
                console.print(m.LINK_ERR)
                sys.exit(1)

        elif mode == RUN_TYPE.CHECK:
            Database.init_db()
            cls.database_cleanup()
        elif mode == RUN_TYPE.RECREATE:
            Config.init()
            Database.init_db()
            SpotifyClient.init()
            cls.recreate()

    @classmethod
    def close(cls) -> None:
        "Cleanup - close database connections etc."
        Database.close()
        Recorder.close()
