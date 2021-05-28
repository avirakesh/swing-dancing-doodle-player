# https://www.google.com/doodles/celebrating-swing-dancing-and-the-savoy-ballroom
# Six keys requires numpy, because naive python was too slow when the game gets crazy


from pynput import keyboard
import multiprocessing as mp
import mss.tools
from math import sin, cos, pi
import numpy as np

# NOTE: All units in pixels

# BEGIN: Constants to change
MONITOR_NUMBER = 2  # Game with monitor. From output of `sct.monitors`

# Bounding box of the game (assuming top left of the monitor is (0, 0))
GAME_BOUNDING_BOX = (
    (149, 812),  # top-left coordinate
    (916, 1243)  # bottom-right coordinate
)

# Radius of key (the dark brown area)
KEY_RADIUS_PX = 50
# Center points (x, y) of each key (relative to GAME_BOUNDING_BOX)
KEY_TO_CENTER = {
    "s": (89, 307),
    "d": (157, 217),
    "f": (225, 125),
    "j": (543, 125),
    "k": (611, 217),
    "l": (679, 307),
}

# Radius of the white circle when the key should be pressed
RING_TARGET_RADIUS = 55
# END: Constants to change

# generalized representation of ring points to look at. These are points on a unit circle
RING_POINT_OFFSETS = [
    (cos(theta_deg * (pi / 180)), sin(theta_deg * (pi / 180)))
    for theta_deg in range(0, 360, 30)
]
# Maps the key to pixel locations in the image
RING_POINTS_TO_LOOK_AT = {
    k: [
        (v[0] + int(r_pt[0] * RING_TARGET_RADIUS), v[1] + int(r_pt[1] * RING_TARGET_RADIUS))
        for r_pt in RING_POINT_OFFSETS
    ]
    for k, v in KEY_TO_CENTER.items()
}

MAJORITY_THRESHOLD = int(len(RING_POINT_OFFSETS) * 0.5)

# Determines what is white. Lower for more sensitivity, and increased false positives
WHITE_THRESHOLD = 230

KB_CONTROLLER = keyboard.Controller()


def _setup_ring_mask(ring_pts):
    img_width = GAME_BOUNDING_BOX[1][0] - GAME_BOUNDING_BOX[0][0]
    img_height = GAME_BOUNDING_BOX[1][1] - GAME_BOUNDING_BOX[0][1]

    img_mask = np.empty([img_height, img_width], dtype=np.bool8)
    img_mask.fill(False)

    for ring_pt in ring_pts:
        img_mask[ring_pt[1]][ring_pt[0]] = True

    return img_mask

# Converts RING_POINTS_TO_LOOK_AT into a boolean mask to be consumed by numpy
NP_RING_POINTS = {
    k: _setup_ring_mask(v)
    for k, v in RING_POINTS_TO_LOOK_AT.items()
}


def is_white_color(color):
    return color[0] >= WHITE_THRESHOLD and color[1] >= WHITE_THRESHOLD and color[2] >= WHITE_THRESHOLD


def is_ring_white(game_img, key, ring_points):
    color_sum = np.sum(game_img, axis=2)  # r + g + b
    white_mask = color_sum > 3 * WHITE_THRESHOLD  # all points that are "white"
    white_ring_points = np.logical_and(white_mask, ring_points)  # all points that are white and also the ring
    num_white_points = np.count_nonzero(white_ring_points) # number of white points in the ring
    return key, num_white_points > MAJORITY_THRESHOLD


def press_key_from_result(result):
    (key, should_press) = result
    if should_press:
        print(key)
        KB_CONTROLLER.tap(key)


def main(sct, pool):
    monitor = sct.monitors[MONITOR_NUMBER]
    print(sct.monitors)
    game_box = {
        "top": monitor["top"] + GAME_BOUNDING_BOX[0][1],
        "left": monitor["left"] + GAME_BOUNDING_BOX[0][0],
        "width": GAME_BOUNDING_BOX[1][0] - GAME_BOUNDING_BOX[0][0],
        "height": GAME_BOUNDING_BOX[1][1] - GAME_BOUNDING_BOX[0][1],
        "mon": MONITOR_NUMBER
    }

    list_np_ring_points = NP_RING_POINTS.items()

    # game_img = sct.grab(game_box)
    # mss.tools.to_png(game_img.rgb, game_img.size, output="game.png")

    should_pause = True
    while True:
        if should_pause:
            input("Press Enter to start")
            should_pause = False

        game_img = np.array(sct.grab(game_box))

        results = [
            pool.apply_async(func=is_ring_white, args=(game_img, key, ring_points), callback=press_key_from_result)
            for key, ring_points in list_np_ring_points
        ]

        _ = [result.get() for result in results]


if __name__ == '__main__':
    print("----------------")
    print("    Six Keys    ")
    print("----------------")
    with mss.mss() as sct, mp.Pool(8) as pool:
        main(sct, pool)
