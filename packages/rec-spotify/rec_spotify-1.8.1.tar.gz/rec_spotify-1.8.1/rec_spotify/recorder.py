import io
import sys
import threading
import time
import typing as t
from threading import Thread

import pyaudiowpatch as pyaudio
from pydub import AudioSegment
from rich.progress import Progress

import rec_spotify.messages as m
from rec_spotify.config import Config
from rec_spotify.console import clear_lines, console
from rec_spotify.items import Track
from rec_spotify.spotify import SpotifyClient


class Recorder(object):
    "Handles audio recording functionality."

    DEVICE_ID: int
    SAMPLE_RATE: int
    PYAUDIO: pyaudio.PyAudio  # type: ignore

    _init: bool = False

    @t.no_type_check
    @classmethod
    def record(cls, track: Track) -> AudioSegment:
        stop_flag = threading.Event()
        frames = io.BytesIO()

        def callback(in_data, frame_count, time_info, status) -> t.Any:
            frames.write(in_data)
            return (in_data, pyaudio.paContinue)

        def updater(progress, task_id):
            while not progress.finished and not stop_flag.is_set():
                progress.update(task_id, advance=1)
                time.sleep(1)

        stream = pyaudio.Stream(
            cls.PYAUDIO,
            format=pyaudio.paInt16,
            channels=2,
            rate=cls.SAMPLE_RATE,
            frames_per_buffer=2048,
            input=True,
            start=False,
            input_device_index=cls.DEVICE_ID,
            stream_callback=callback,
        )  # type: ignore
        console.print(m.TRACK.format(title=track.title))

        if SpotifyClient.is_playing():
            SpotifyClient.pause_track()
            time.sleep(5)
        try:
            with Progress(console=console) as progress:
                task = progress.add_task("", total=track.duration)
                timer = Thread(target=updater, args=(progress, task))
                timer.start()
                stream.start_stream()
                SpotifyClient.play_track(track)
                time.sleep(t.cast(float, track.duration))  # TODO: FIX typing
                frames.seek(0)
                recorded = AudioSegment.from_file(
                    frames,
                    format="raw",
                    frame_rate=48000,
                    channels=2,
                    sample_width=2,
                )
                return recorded
        except KeyboardInterrupt:
            stop_flag.set()
            cls.close()
            sys.exit(0)
        finally:
            stream.close()

    @classmethod
    def _set_device_id(cls) -> None:
        "Helper method to select recording device interactively."
        devices = {}
        console.print(m.SELECT_AUDIO_DEVICE)
        idx = 1
        for device in cls.PYAUDIO.get_loopback_device_info_generator():
            console.print(f"{idx}. {device['name']}")
            devices[idx] = device
            idx += 1

        choice = int(console.input("Select: "))
        cls.DEVICE_ID = devices[choice]["index"]
        cls.SAMPLE_RATE = int(devices[choice]["defaultSampleRate"])

        clear_lines(idx + 1)

    @classmethod
    def init(cls) -> None:
        "Initialize PyAudio and set recording device."
        cls.PYAUDIO = pyaudio.PyAudio()
        cls._set_device_id()
        cls._init = True

    @classmethod
    def close(cls) -> None:
        "Close PyAudio instance."
        if cls._init:
            cls.PYAUDIO.terminate()
