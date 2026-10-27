"""
video_manager.py
-----------------
Defines the VideoManager class.

This is a thin "manager" layer that sits between main.py and the individual
DroneStream objects. main.py never talks to DroneStream directly - it only
talks to VideoManager. This keeps main.py simple and means you could later
swap out how streams work internally without touching main.py at all.

Responsibilities:
    - Create one DroneStream per entry in config.DRONE_STREAMS.
    - start_all() / stop_all() to control every stream at once.
    - get_frames() to fetch the latest frame from every drone in one call.
"""

import config
from drone_stream import DroneStream


class VideoManager:
    def __init__(self):
        # Build one DroneStream object per camera listed in config.py.
        # self.streams looks like: {"DRONE 1": DroneStream(...), ...}
        self.streams = {
            name: DroneStream(name, url)
            for name, url in config.DRONE_STREAMS.items()
        }

    def start_all(self):
        """Start every drone's background reading thread."""
        for stream in self.streams.values():
            stream.start()

    def stop_all(self):
        """Stop every drone's thread and release its camera cleanly."""
        for stream in self.streams.values():
            stream.stop()

    def get_frames(self):
        """
        Returns a dict of {drone_name: frame_or_None}.

        frame_or_None is either a NumPy image (BGR, as OpenCV likes it) or
        None if that drone currently has no signal.
        """
        return {
            name: stream.get_frame()
            for name, stream in self.streams.items()
        }
