RescueSwarm GCS – Video Module
A Python-based ground control station video module for the NIDAR RescueSwarm project. It receives three SIYI camera feeds over RTSP and displays them in a single window.
Features
- Displays three live camera streams in a 2×2 layout.
- Runs each stream in a separate thread.
- Shows NO SIGNAL when a camera feed is unavailable.
- Automatically reconnects when a stream disconnects.
- Includes a placeholder tile for future map and telemetry integration.
- Shuts down streams and GStreamer processes when the application closes.
Project Structure
project-folder/
├── main.py
├── config.py
├── drone_stream.py
├── video_manager.py
├── telemetry.py
├── requirements.txt
└── README.md
Keep all Python files in the same folder.


Requirements
- Python 3.10 or later
- GStreamer for Windows (MSVC 64-bit, Complete installation)
- Python packages listed in requirements.txt


Setup
Open the project folder in VS Code and run these commands in the terminal:


python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

If PowerShell blocks activation, run the following command and activate the environment again:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Install GStreamer using the Windows MSVC 64-bit installer and select Complete. If it is installed in a different location, update GST_LAUNCH_PATH in config.py.

Configuration
Edit DRONE_STREAMS in config.py with the RTSP URLs for your cameras:
DRONE_STREAMS = {
    "DRONE 1": "rtsp://192.168.144.25:8554/ch01.264",
    "DRONE 2": "rtsp://192.168.144.26:8554/ch01.264",
    "DRONE 3": "rtsp://192.168.144.27:8554/ch01.264",
}
Replace these example addresses with the actual camera addresses and correct stream paths. 

Depending on the camera configuration, the stream path may be /main.264 instead of /ch01.264.
Run
Activate the virtual environment and start the application:
.\.venv\Scripts\Activate.ps1
python main.py


Press Q in the video window to quit.
How It Works
Each DroneStream runs independently and uses GStreamer to receive and decode its RTSP stream. VideoManager manages the three streams, while main.py displays the latest frames. If a stream is lost, the application retries automatically.
Troubleshooting
- All tiles show NO SIGNAL: Check camera power, network connectivity, RTSP URLs, and stream paths.
- GStreamer not found: Verify the installation and GST_LAUNCH_PATH in config.py.
- H.264 decoder missing: Install GStreamer with the Complete option.
- Only one camera fails: Check that camera's IP address and stream path.
- Need to test a stream: Open the RTSP URL in VLC using Media → Open Network Stream.
Scope
This module handles video display only. Telemetry, autonomous navigation, AI processing, hardware control, and network configuration are outside its current scope. The RTSP streams must already be reachable from the computer running the application.