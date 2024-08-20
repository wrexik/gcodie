import numpy as np

from .utils import stats
from .parse import parse_gcode_silent

def last_layer(gcode_path):

    x, y, z = parse_gcode_silent(gcode_path)
    last_layer =  int(np.max(z) / 0.2) + 1

    last_layer = last_layer - 1 # usually last layer is nothing

    stats(f"Last layer is {last_layer}")

    return last_layer

def first_layer(gcode_path):

    global no_stats

    x, y, z = parse_gcode_silent(gcode_path)
    first_layer =  int(np.min(z) / 0.2) + 1

    stats(f"First layer is {first_layer}")

    return first_layer