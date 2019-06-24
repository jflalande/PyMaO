from enum import IntEnum

""" Helps to encode the device status """
class Colors(IntEnum):

    WHITE = 1 # Not seen by adb
    GREEN = 2
    YELLOW = 3
    RED = 4