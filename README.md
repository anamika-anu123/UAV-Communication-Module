# RescueSwarm GCS – Video Module

A Python-based ground control station (GCS) video module for the RescueSwarm project. It connects to multiple RTSP camera streams, displays them in a single 2x2 monitoring view, and automatically handles reconnects and missing signal states.

## Overview

This project is designed to monitor multiple drones or camera feeds from a single operator interface. Each camera runs in its own background thread and is rendered into a tile in the main display window.

The application includes:
- 3 live drone camera feeds in one window
- automatic reconnection when a feed drops
- a placeholder tile for telemetry or map data
- clean shutdown of all threads and GStreamer processes

## Features

- Displays three camera streams in a 2x2 layout
- Runs each stream independently in a background thread
- Shows `NO SIGNAL` when a stream is unavailable or stale
- Automatically reconnects to RTSP streams after failures
- Keeps the latest valid frame for each camera
- Provides a placeholder area for future telemetry/map integration
- Gracefully shuts down all active streams on exit

## Project Structure

```text
com_mod/
├── main.py
├── config.py
├── drone_stream.py
├── video_manager.py
├── telemetry.py
├── requirements.txt
├── README.md
├── gst_DRONE_1.log
├── gst_DRONE_2.log
├── gst_DRONE_3.log
└── .venv/   (optional local virtual environment)
```

Keep all Python files in the same folder so imports work correctly.

## Requirements

- Python 3.10 or newer
- Windows
- GStreamer for Windows (MSVC 64-bit, Complete installation)
- Python dependencies from `requirements.txt`

## Setup

1. Open the project folder in VS Code.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

3. Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

4. Install GStreamer from the official Windows installer and choose the Complete option.

5. Confirm the GStreamer binary path in `config.py`:

```python
GST_LAUNCH_PATH = r"C:\Program Files\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0.exe"
```

If GStreamer is installed in another location, update this path.

## Configuration

Edit the RTSP URL list in `config.py` before running the app:

```python
DRONE_STREAMS = {
    "DRONE 1": "rtsp://192.168.144.25:8554/main.264",
    "DRONE 2": "rtsp://192.168.144.26:8554/ch01.264",
    "DRONE 3": "rtsp://192.168.144.27:8554/ch01.264",
}
```

Notes:
- Replace the sample IP addresses with your actual drone camera addresses.
- Some SIYI cameras use `/main.264` while others use `/ch01.264`.
- Test the stream in VLC before running the app if it does not connect.

## Running the Application

From the project directory:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

A window will open showing:
- Drone 1 feed
- Drone 2 feed
- Drone 3 feed
- telemetry/map placeholder tile

Press `Q` in the video window to quit.

## How It Works

- `main.py` creates the display layout and keeps the window open.
- `VideoManager` creates one `DroneStream` object for each camera.
- Each `DroneStream` runs in its own thread and reads RTSP frames using GStreamer.
- Frames are stored in memory and checked for staleness.
- If a stream is lost or stale, the app shows `NO SIGNAL` until the feed reconnects.

## Troubleshooting

### All tiles show `NO SIGNAL`
- Check that the cameras are powered on
- Verify that the RTSP URLs are correct
- Confirm the camera stream path (`/main.264` vs `/ch01.264`)
- Make sure the machine can reach the camera network

### GStreamer not found
- Reinstall GStreamer using the Windows MSVC 64-bit package
- Check the `GST_LAUNCH_PATH` value in `config.py`

### Decoder or stream issues
- Use VLC to test the RTSP URL
- Check the stream path and camera settings
- Ensure the camera is sending a valid H.264/H.265 stream

### One camera fails while others work
- Verify that specific camera's IP address and RTSP path
- Check the camera for network or power issues

## Scope

This module currently handles video display and RTSP monitoring only. Telemetry overlays, autonomous navigation, AI processing, hardware control, and broader mission software are not implemented here yet.

## License

This project is provided as-is for local use in the RescueSwarm system. Please check with the project owner before redistributing or reusing it in a production or commercial environment.
