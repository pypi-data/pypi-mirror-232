import configparser
import os
import sys
import enum

import rec_spotify.messages as m
from rec_spotify.console import console


class RUN_TYPE(enum.Enum):
    INIT = 1
    SYNC = 2
    SINGLE = 3
    CHECK = 4
    RECREATE = 5


class Config(object):
    """
    Main configuration class for the rec_spotify module.
    """

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URL: str
    MUSIC_DIR: str
    DATABASE_PATH: str
    AUDIO_FORMAT: str
    AUDIO_QUALITY: int
    TRIM_SILENCE: bool

    _DEFAULT_FILENAME = "config.ini"
    _DEFAULT_DBNAME = "spotify.db"
    _DEFAULT_CACHE = ".cache"

    _LIKED_ID = "likedVUqLsoulrg55rDqjp"
    _LIKED_NAME = "Liked Songs"

    @classmethod
    def init(cls) -> None:
        """
        Initializes the Config class.

        This method checks if a configuration file exists and if not,
        it creates a new one.
        """
        if not os.path.exists(cls.get_config_filepath()):
            console.print(m.CONFIG_NOT_FOUND, style="")
            cls.create_config_file()
            sys.exit(0)

        cls.parse()

        if cls.is_valid():
            msg = m.CONFIG_VALID.format(filepath=cls.get_config_filepath())
            console.print(msg)

    @classmethod
    def parse(cls) -> None:
        """
        Parses the configuration file.

        This method reads the configuration file and sets the class-level
        attributes based on the values in the file.
        """
        config_path = os.path.join(cls.get_config_folder(), cls._DEFAULT_FILENAME)
        config = configparser.ConfigParser()
        config.read(config_path)
        sp = config["SPOTIFY"]
        sn = config["SETTINGS"]
        cls.CLIENT_ID = sp.get("CLIENT_ID")
        cls.CLIENT_SECRET = sp.get("CLIENT_SECRET")
        cls.REDIRECT_URL = sp.get("REDIRECT_URL")
        cls.MUSIC_DIR = os.path.normpath(sn.get("MUSIC_DIR"))
        cls.AUDIO_FORMAT = sn.get("AUDIO_FORMAT")
        cls.AUDIO_QUALITY = sn.getint("AUDIO_QUALITY")
        cls.TRIM_SILENCE = sn.getboolean("TRIM_SILENCE")

    @classmethod
    def create_config_file(cls) -> None:
        """
        Creates a new configuration file.

        This method creates a new configuration file by prompting the user for input using the console.
        """
        config = configparser.ConfigParser()
        config.optionxform = str  # type: ignore
        config["SPOTIFY"] = {
            "CLIENT_ID": console.input(":key: CLIENT ID: "),
            "CLIENT_SECRET": console.input(":key: CLIENT_SECRET: "),
            "REDIRECT_URL": console.input(":link: REDIRECT_URL: "),
        }
        config["SETTINGS"] = {
            "MUSIC_DIR": console.input(":file_folder: MUSIC DIRECTORY: "),
            "AUDIO_FORMAT": "mp3",
            "AUDIO_QUALITY": "320",
            "TRIM_SILENCE": "False",
        }

        if not os.path.exists(cls.get_config_folder()):
            os.mkdir(cls.get_config_folder())

        with open(cls.get_config_filepath(), "w") as file:
            config.write(file)

        msg = m.CONFIG_CREATED.format(filepath=cls.get_config_filepath())
        console.print(msg)

    @classmethod
    def is_valid(cls) -> bool:
        """
        Checks if all required attributes are set.
        """
        return all((cls.CLIENT_ID, cls.CLIENT_SECRET, cls.REDIRECT_URL))

    @classmethod
    def get_database_filepath(cls) -> str:
        """
        Returns the file path for the database.
        """
        return os.path.join(cls.get_config_folder(), cls._DEFAULT_DBNAME)

    @classmethod
    def get_config_folder(cls) -> str:
        """
        Returns the file path for the config folder.
        """
        home_folder = os.path.expanduser("~")
        config_folder = os.path.join(home_folder, ".rec_spotify")
        return config_folder

    @classmethod
    def get_config_filepath(cls) -> str:
        """
        Returns the file path for the config file.
        """
        return os.path.join(cls.get_config_folder(), cls._DEFAULT_FILENAME)

    @classmethod
    def get_cache_filepath(cls) -> str:
        """
        Returns the file path for the cache file.
        """
        return os.path.join(cls.get_config_folder(), cls._DEFAULT_CACHE)
