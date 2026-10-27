DRONE_STREAMS = {
    "DRONE 1": "rtsp://192.168.144.25:8554/main.264",
    "DRONE 2": "rtsp://192.168.144.26:8554/ch01.264",
    "DRONE 3": "rtsp://192.168.144.27:8554/ch01.264",
}
 
# ---------------------------------------------------------------------------
# Size (width, height) that EACH individual video tile will be resized to
# before being placed into the 2x2 grid. All four tiles (3 video + 1
# placeholder) use this same size so the grid lines up evenly.
# ---------------------------------------------------------------------------
TILE_WIDTH = 640
TILE_HEIGHT = 360
 
# ---------------------------------------------------------------------------
# How long (in seconds) a DroneStream will wait between reconnect attempts
# after losing its RTSP connection.
# ---------------------------------------------------------------------------
RECONNECT_DELAY_SECONDS = 2.0
 
# ---------------------------------------------------------------------------
# If no new frame has been received within this many seconds, the stream is
# considered "stale" and the GCS will show NO SIGNAL for that drone even if
# an old frame is technically still stored in memory.
# ---------------------------------------------------------------------------
STALE_FRAME_TIMEOUT_SECONDS = 3.0
 
# ---------------------------------------------------------------------------
# Title text shown at the top of the GCS window.
# ---------------------------------------------------------------------------
WINDOW_TITLE = "RESCUESWARM GCS"
 
# ---------------------------------------------------------------------------
# GStreamer settings (used by drone_stream.py)
# ---------------------------------------------------------------------------
 
# Full path to gst-launch-1.0.exe. This is where the normal GStreamer
# Windows installer puts it. If you installed GStreamer somewhere else,
# change this path.
GST_LAUNCH_PATH = r"C:\Program Files\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0.exe"
 
# Size GStreamer will scale each camera frame to BEFORE sending it to Python.
# Using the same size as the tiles means main.py has almost nothing to resize.
# (SIYI cameras are 16:9, and 640x360 is 16:9, so the picture is not stretched.)
STREAM_WIDTH = TILE_WIDTH
STREAM_HEIGHT = TILE_HEIGHT
 
# If the RTSP connection goes silent for this many seconds, GStreamer gives
# up and exits, so drone_stream.py can reconnect. Without this, a frozen
# stream could hang for ~20 seconds before anything happens.
GST_TCP_TIMEOUT_SECONDS = 5
 
# NOTE ON THE RTSP PATH: SIYI cameras often use "/main.264" instead of
# "/ch01.264". If a camera is connected but you still see NO SIGNAL, try
# changing the end of the URL in DRONE_STREAMS above (test it in VLC first).
GST_SHOW_ERRORS = True

GST_CODEC = "auto"