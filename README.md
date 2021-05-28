# Celebrating Swing Dancing and the Savoy Ballroom!

Auto player for Google's [Swing Dancing](https://www.google.com/doodles/celebrating-swing-dancing-and-the-savoy-ballroom) 
doodle.

Use [`four_keys.py`](four_keys.py) for Single player version, and [`six_keys.py`](six_keys.py) for Bonus stage, or the Two 
Player version.

### How to use script
To use either script, you will need to change the following constants to meet your setup:
  - `MONITOR_NUMBER`: The monitor where game is displayed. Check from output of `sct.monitors`
  - `GAME_BOUNDING_BOX`: Location of game within the monitor
  - `KEY_RADIUS_PX`: Radius of notes key when nothing is pressed
  - `KEY_TO_CENTER`: Coordinates of notes key, relative to GAME_BOUNDING_BOX
  - `RING_TARGET_RADIUS`: Size of the white ring when the key should be pressed.

### Notes
- There is no kill switch implemented, be prepared to spam `Ctrl + C` if the script starts misbehaving :P
- [`four_keys.py`](four_keys.py) uses naive python constructs to determine if a key should be pressed. Each snapshot 
  takes ~50ms to process (~20 snapshots per second). If stars line up, this can cause misses; but misses were not very 
  common in my case, so leaving it as is.
- [`six_keys.py`](six_keys.py) uses numpy to process the screenshot because six key version moves much quicker and 
  requires more computation to detect rings, causing frequent misses. With numpy, each snapshot takes ~30ms to process 
  (~33 snapshots per second).