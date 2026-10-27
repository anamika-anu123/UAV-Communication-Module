"""
main.py
--------
The entry point of the RescueSwarm GCS video module.

What this file does:
    1. Creates a VideoManager and starts all 3 drone camera threads.
    2. Every loop iteration:
        - Asks VideoManager for the latest frame from each drone.
        - Resizes/labels each frame (or shows "NO SIGNAL" if None).
        - Gets the telemetry placeholder tile.
        - Stacks all 4 tiles into a 2x2 grid.
        - Adds a title bar on top.
        - Displays the result in one OpenCV window.
    3. Watches for the "Q" key to exit.
    4. On exit, stops all threads and releases resources cleanly.

Run this file with:  python main.py
(See README.md for full setup instructions.)
"""

import cv2
import numpy as np

import config
import telemetry
from video_manager import VideoManager


def make_no_signal_tile(label):
    """
    Builds a placeholder image shown when a drone's video isn't available.
    Same size as a normal video tile so it fits the grid perfectly.
    """
    tile = np.zeros((config.TILE_HEIGHT, config.TILE_WIDTH, 3), dtype=np.uint8)

    text = "NO SIGNAL"
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1.2, 3)[0]
    text_x = (config.TILE_WIDTH - text_size[0]) // 2
    text_y = config.TILE_HEIGHT // 2
    cv2.putText(tile, text, (text_x, text_y), font, 1.2, (0, 0, 255), 3)

    return tile


def add_label(tile, label):
    """
    Draws a small label (e.g. "DRONE 1") in the top-left corner of a tile.
    Returns a NEW image so we don't accidentally modify a frame that's still
    being used elsewhere.
    """
    labeled = tile.copy()
    cv2.rectangle(labeled, (0, 0), (150, 30), (0, 0, 0), -1)  # label background
    cv2.putText(
        labeled, label, (8, 21),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
    )
    return labeled


def prepare_tile(frame, label):
    """
    Takes a raw frame (or None) for one drone and returns a properly sized,
    labeled tile ready to be placed into the grid.
    """
    if frame is None:
        tile = make_no_signal_tile(label)
    else:
        tile = cv2.resize(frame, (config.TILE_WIDTH, config.TILE_HEIGHT))

    return add_label(tile, label)


def build_grid(drone_names, frames):
    """
    Builds the full 2x2 GCS layout:

        DRONE 1        | DRONE 2
        ----------------+----------------
        DRONE 3        | MAP / TELEMETRY

    drone_names: list of 3 names in order, e.g. ["DRONE 1", "DRONE 2", "DRONE 3"]
    frames:      dict {name: frame_or_None} from VideoManager.get_frames()
    """
    tile1 = prepare_tile(frames.get(drone_names[0]), drone_names[0])
    tile2 = prepare_tile(frames.get(drone_names[1]), drone_names[1])
    tile3 = prepare_tile(frames.get(drone_names[2]), drone_names[2])
    tile4 = add_label(telemetry.get_placeholder_tile(), "MAP / TELEMETRY")

    top_row = np.hstack((tile1, tile2))
    bottom_row = np.hstack((tile3, tile4))
    grid = np.vstack((top_row, bottom_row))

    return grid


def add_title_bar(grid):
    """Adds a title bar with the window/app name above the 2x2 grid."""
    bar_height = 40
    width = grid.shape[1]

    title_bar = np.zeros((bar_height, width, 3), dtype=np.uint8)
    text = config.WINDOW_TITLE
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 0.9, 2)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (bar_height + text_size[1]) // 2
    cv2.putText(title_bar, text, (text_x, text_y), font, 0.9, (255, 255, 255), 2)

    return np.vstack((title_bar, grid))


def main():
    # Fixed order so DRONE 1 / DRONE 2 / DRONE 3 always land in the same
    # grid position regardless of dict ordering.
    drone_names = list(config.DRONE_STREAMS.keys())

    video_manager = VideoManager()
    video_manager.start_all()

    window_name = config.WINDOW_TITLE
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("RescueSwarm GCS running. Press 'Q' in the video window to quit.")

    try:
        while True:
            frames = video_manager.get_frames()
            grid = build_grid(drone_names, frames)
            display = add_title_bar(grid)

            cv2.imshow(window_name, display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Q pressed. Shutting down...")
                break

            # If the user closes the window with the X button, exit too.
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("Window closed. Shutting down...")
                break

    finally:
        # This block always runs, even if something above raises an error,
        # so we never leave camera threads running in the background.
        video_manager.stop_all()
        cv2.destroyAllWindows()
        print("Shutdown complete. All streams stopped and resources released.")


if __name__ == "__main__":
    main()
