import argparse

import rec_spotify
from rec_spotify.config import RUN_TYPE
from rec_spotify.console import console, get_logo
from rec_spotify.manager import Manager


def app() -> None:
    """CLI entrypoint."""

    console.print(get_logo(), style="green")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        required=False,
        help="Run database cleanup.",
    )
    parser.add_argument(
        "-s",
        "--sync",
        action="store_true",
        required=False,
        help="Synchronize all of your Spotify playlists with local music library.",
    )
    parser.add_argument(
        "-r",
        "--recreate",
        action="store_true",
        required=False,
        help="Create all tracks and playlists stored in the local database to the user's Spotify account.",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=False,
        help="Spotify link or ID for a separate track, playlist, or album.",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        required=False,
        help="The output directory for saving recorded files",
    )
    ver = f"Author: oSeeLight | Version: {rec_spotify.__version__}"
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    mode = RUN_TYPE.INIT

    if args.check:
        mode = RUN_TYPE.CHECK
    elif args.url and args.path:
        mode = RUN_TYPE.SINGLE
    elif args.sync:
        mode = RUN_TYPE.SYNC
    elif args.recreate:
        mode = RUN_TYPE.RECREATE

    manager = Manager()
    manager.init(mode, args)

    if mode == RUN_TYPE.INIT:
        parser.print_help()

    manager.close()


if __name__ == "__main__":
    app()
