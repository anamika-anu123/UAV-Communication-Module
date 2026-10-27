"""
telemetry.py
-------------
PLACEHOLDER MODULE for future telemetry / map integration.

Nothing in here does real telemetry work yet. This file exists so that:
    1. main.py has ONE clear place to import telemetry from.
    2. When you're ready to add real map/telemetry data (e.g. from
       MAVLink/pymavlink), you build it here and main.py barely changes -
       you'd just replace get_placeholder_tile() with something that draws
       real telemetry data.

For now, get_placeholder_tile() just returns a plain gray image with text
saying "MAP / TELEMETRY (placeholder)", sized to fit the GCS grid.
"""

import numpy as np
import cv2

import config


def get_placeholder_tile():
    """
    Returns a single BGR image (NumPy array) sized TILE_WIDTH x TILE_HEIGHT,
    to be placed in the bottom-right cell of the 2x2 GCS grid.

    Replace the contents of this function later with real map/telemetry
    rendering. The rest of main.py does not need to change as long as this
    function keeps returning an image of the same size.
    """
    tile = np.full(
        (config.TILE_HEIGHT, config.TILE_WIDTH, 3),
        (40, 40, 40),  # dark gray background (BGR)
        dtype=np.uint8,
    )

    text = "MAP / TELEMETRY"
    subtext = "(placeholder - not yet implemented)"

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Center the main text roughly in the middle of the tile.
    text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
    text_x = (config.TILE_WIDTH - text_size[0]) // 2
    text_y = config.TILE_HEIGHT // 2
    cv2.putText(tile, text, (text_x, text_y), font, 1.0, (200, 200, 200), 2)

    sub_size = cv2.getTextSize(subtext, font, 0.5, 1)[0]
    sub_x = (config.TILE_WIDTH - sub_size[0]) // 2
    sub_y = text_y + 30
    cv2.putText(tile, subtext, (sub_x, sub_y), font, 0.5, (150, 150, 150), 1)

    return tile
