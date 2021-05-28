# https://www.google.com/doodles/celebrating-swing-dancing-and-the-savoy-ballroom

from pynput import keyboard
import multiprocessing as mp
import mss.tools

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
# Center points of each key
KEY_TO_CENTER = {
    "d": (136, 290),
    "f": (203, 144),
    "j": (565, 144),
    "k": (634, 290),
}

# Radius of the white circle when the key should be pressed
RING_TARGET_RADIUS = 60
# END: Constants to change

# general ring points to look at to detect ring. Currently looking at the cardinal axes
RING_POINT_OFFSETS = [(-1, 0), (1, 0), (0, -1), (-1, 0)]
# Maps the key to to specific ring points
RING_POINTS_TO_LOOK_AT = {
    k: [(v[0] + int(r_pt[0] * RING_TARGET_RADIUS), v[1] + int(r_pt[1] * RING_TARGET_RADIUS)) for r_pt in RING_POINT_OFFSETS]
    for k, v in KEY_TO_CENTER.items()
}
# Determines what is white. Lower for more sensitivity, and increased false positives
WHITE_THRESHOLD = 230

KB_CONTROLLER = keyboard.Controller()


def is_white_color(color):
    return color[0] + color[1] + color[2] >= 3 * WHITE_THRESHOLD


def is_ring_white(game_img, key, ring_points):
    is_white = 0
    majority_threshold = int(len(ring_points) / 2)
    for ring_point in ring_points:
        color = game_img.pixels[ring_point[1]][ring_point[0]]
        is_white += 1 if is_white_color(color) else 0
        if is_white >= majority_threshold:
            return key, True
    return key, False


def press_key_from_result(result):
    (key, should_press) = result
    if should_press:
        print(key)
        KB_CONTROLLER.press(key)
        KB_CONTROLLER.release(key)


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

    # game_img = sct.grab(game_box)
    # mss.tools.to_png(game_img.rgb, game_img.size, output="game.png")

    should_pause = True
    while True:
        if should_pause:
            input("Press Enter to start")
            should_pause = False

        game_img = sct.grab(game_box)

        results = [
            pool.apply_async(func=is_ring_white, args=(game_img, key, ring_points), callback=press_key_from_result)
            for key, ring_points in RING_POINTS_TO_LOOK_AT.items()
        ]

        _ = [result.get() for result in results]


if __name__ == '__main__':
    print("---------------")
    print("   Four Keys   ")
    print("---------------")
    with mss.mss() as sct, mp.Pool(8) as pool:
        main(sct, pool)
