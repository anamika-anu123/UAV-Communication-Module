"""
drone_stream.py  (GStreamer version)
-------------------------------------
Defines the DroneStream class: one object = one camera.

How this version gets video:
    Instead of asking OpenCV to open the RTSP address, we start GStreamer
    (gst-launch-1.0.exe) as a separate program. GStreamer connects to the
    camera, decodes the H.264 video, converts it to plain BGR pixels at a
    fixed size, and "pipes" those raw pixels into Python. Python just reads
    them, one frame at a time.

    A frame at 640x360 is exactly 640 * 360 * 3 bytes (3 bytes per pixel:
    Blue, Green, Red). So Python reads that many bytes = 1 frame.

What this file still does (same as before):
    - Runs in its own background thread, so a slow camera never blocks others.
    - Stores the latest frame safely (with a Lock).
    - If GStreamer exits or the stream breaks -> wait, then restart it
      (automatic reconnection).
    - get_frame() returns None when there is no fresh frame -> "NO SIGNAL".
    - stop() shuts down the thread and kills the GStreamer process.
"""

import os
import subprocess
import threading
import time

import numpy as np

import config


class DroneStream:
    def __init__(self, name: str, rtsp_url: str):
        self.name = name
        self.rtsp_url = rtsp_url

        # Size of each frame and how many bytes one frame takes.
        self.width = config.STREAM_WIDTH
        self.height = config.STREAM_HEIGHT
        self.frame_size = self.width * self.height * 3

        # Latest frame + when it arrived (shared with the GUI thread).
        self._latest_frame = None
        self._last_frame_time = 0.0
        self._lock = threading.Lock()

        # Used to tell the background thread to stop.
        self._stop_event = threading.Event()

        # The running GStreamer program (None when not connected).
        self._process = None

        # GStreamer's error messages are saved to a small log file next to
        # this script (for example gst_DRONE_1.log) so we can see WHY a
        # stream failed. Turn this off with GST_SHOW_ERRORS = False in config.py.
        safe_name = self.name.replace(" ", "_")
        folder = os.path.dirname(os.path.abspath(__file__))
        self._log_path = os.path.join(folder, f"gst_{safe_name}.log")
        self._log_file = None

        self._thread = None

    # -----------------------------------------------------------------
    # Public methods (called from main.py / video_manager.py)
    # -----------------------------------------------------------------

    def start(self):
        """Start the background thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._update_loop,
            name=f"{self.name}-thread",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        """Stop the thread and kill GStreamer."""
        self._stop_event.set()
        self._kill_process()  # unblocks the thread if it is waiting for data
        if self._thread is not None:
            self._thread.join(timeout=5.0)

    def get_frame(self):
        """
        Return the latest frame, or None if there is no signal.
        None is returned if we never got a frame OR the last one is too old.
        """
        with self._lock:
            frame = self._latest_frame
            frame_time = self._last_frame_time

        if frame is None:
            return None
        if time.time() - frame_time > config.STALE_FRAME_TIMEOUT_SECONDS:
            return None
        return frame

    # -----------------------------------------------------------------
    # Internal methods (run inside the background thread)
    # -----------------------------------------------------------------

    def _build_command(self):
        """The GStreamer pipeline, written as a list of words."""

        # Which decoder to use. SIYI cameras can send H.264 OR H.265, and the
        # wrong choice causes "Internal data stream error".
        #   "auto" -> GStreamer figures out the codec by itself (decodebin)
        #   "h264" -> force H.264
        #   "h265" -> force H.265
        codec = str(getattr(config, "GST_CODEC", "auto")).lower()

        if codec == "h264":
            decode_part = ["!", "rtph264depay", "!", "h264parse", "!", "avdec_h264"]
        elif codec == "h265":
            decode_part = ["!", "rtph265depay", "!", "h265parse", "!", "avdec_h265"]
        else:
            decode_part = ["!", "decodebin"]

        return (
            [
                config.GST_LAUNCH_PATH,
                "-q",                               # quiet: no extra text output
                "rtspsrc",                          # connect to the RTSP camera
                f"location={self.rtsp_url}",
                "protocols=tcp",                    # TCP is more reliable than UDP
                "latency=0",                        # don't buffer -> lowest delay
                f"tcp-timeout={config.GST_TCP_TIMEOUT_SECONDS * 1000000}",  # microseconds
            ]
            + decode_part                           # unpack + decode the video
            + [
                "!", "videoconvert",
                "!", "videoscale",
                "!", f"video/x-raw,format=BGR,width={self.width},height={self.height}",
                "!", "fdsink", "fd=1",              # send raw pixels to Python
            ]
        )

    def _start_process(self):
        """Launch GStreamer. Returns True if it started."""
        print(f"[{self.name}] Starting GStreamer for {self.rtsp_url} ...")
        try:
            # CREATE_NO_WINDOW stops a black console window popping up on
            # Windows. getattr keeps the code working on other systems too.
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            # Where GStreamer's error messages go: a log file, or nowhere.
            error_target = subprocess.DEVNULL
            if getattr(config, "GST_SHOW_ERRORS", True):
                try:
                    self._log_file = open(self._log_path, "w")
                    error_target = self._log_file
                except OSError:
                    self._log_file = None

            self._process = subprocess.Popen(
                self._build_command(),
                stdout=subprocess.PIPE,
                stderr=error_target,
                creationflags=flags,
            )
            return True
        except FileNotFoundError:
            # Wrong GST_LAUNCH_PATH, or GStreamer is not installed.
            print(f"[{self.name}] ERROR: GStreamer not found at "
                  f"{config.GST_LAUNCH_PATH}. Check GST_LAUNCH_PATH in config.py")
            self._process = None
            return False
        except OSError as error:
            print(f"[{self.name}] ERROR: could not start GStreamer: {error}")
            self._process = None
            return False

    def _kill_process(self):
        """Stop the GStreamer program if it is running."""
        process = self._process
        self._process = None
        if process is not None:
            try:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=3)
            except Exception:
                pass
        if self._log_file is not None:
            try:
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None

    def _print_last_error(self):
        """Print the most useful error line GStreamer wrote to its log."""
        if not getattr(config, "GST_SHOW_ERRORS", True):
            return
        try:
            with open(self._log_path, "r", errors="replace") as f:
                lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        except OSError:
            return
        if not lines:
            print(f"[{self.name}] GStreamer printed no error "
                  f"(the connection probably timed out).")
            return
        # Find the first line that says ERROR, and show it plus 2 lines after.
        start = len(lines) - 1
        for i, line in enumerate(lines):
            if "ERROR" in line.upper():
                start = i
                break
        for line in lines[start:start + 6]:
            print(f"[{self.name}] GStreamer: {line}")

    def _read_exact(self, process):
        """
        Read exactly one frame's worth of bytes from GStreamer.
        Returns the bytes, or None if the stream ended / broke.
        """
        try:
            data = process.stdout.read(self.frame_size)
        except (OSError, ValueError):
            return None
        if data is None or len(data) != self.frame_size:
            return None
        return data

    def _update_loop(self):
        """
        Repeat until stop():
            - make sure GStreamer is running (start it if not)
            - read one frame and store it
            - if reading fails -> kill GStreamer, wait, and try again
        """
        while not self._stop_event.is_set():

            # Step 1: make sure GStreamer is running.
            if self._process is None:
                if not self._start_process():
                    self._stop_event.wait(config.RECONNECT_DELAY_SECONDS)
                    continue

            process = self._process
            if process is None:  # stop() was called at this exact moment
                break

            # Step 2: read one frame (this waits until a frame arrives).
            raw = self._read_exact(process)

            if raw is None:
                self._kill_process()
                if not self._stop_event.is_set():
                    print(f"[{self.name}] Stream lost. Reconnecting...")
                    self._print_last_error()
                self._stop_event.wait(config.RECONNECT_DELAY_SECONDS)
                continue

            # Step 3: turn the bytes into an image and store it.
            # .copy() so the image doesn't depend on the raw byte buffer.
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                self.height, self.width, 3
            ).copy()

            with self._lock:
                self._latest_frame = frame
                self._last_frame_time = time.time()

        # Leaving the loop -> make sure GStreamer is gone.
        self._kill_process()