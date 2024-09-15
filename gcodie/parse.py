import numpy as np

from .utils import *

def parse_gcode(file_path):

    global no_stats

    x, y, z = [], [], []
    current_position = [0, 0, 0]  # X, Y, Z coordinates

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Skip empty or malformed lines
                if not line or not line.startswith('G1'):
                    continue
                
                parts = line.split(' ')
                for part in parts:
                    if part.startswith('X'):
                        try:
                            current_position[0] = float(part[1:])
                        except ValueError:
                            stats(colored(f"Warning: Invalid X value '{part[1:]}' skipped.", "yellow"))
                    elif part.startswith('Y'):
                        try:
                            current_position[1] = float(part[1:])
                        except ValueError:
                            stats(colored(f"Warning: Invalid Y value '{part[1:]}' skipped.", "yellow"))
                    elif part.startswith('Z'):
                        try:
                            current_position[2] = float(part[1:])
                        except ValueError:
                            stats(colored(f"Warning: Invalid Z value '{part[1:]}' skipped.", "yellow"))
                
                # Store the current position after processing the line
                x.append(current_position[0])
                y.append(current_position[1])
                z.append(current_position[2])

    except FileNotFoundError:
        stats(f"Error: File '{file_path}' not found.")
        return np.array([]), np.array([]), np.array([])
    except Exception as e:
        stats(f"Error reading G-code file: {e}")
        return np.array([]), np.array([]), np.array([])

    return np.array(x), np.array(y), np.array(z)

def parse_gcode_silent(file_path):

    global no_stats

    x, y, z = [], [], []
    current_position = [0, 0, 0]  # X, Y, Z coordinates

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('G1'):  # Only process movement commands
                    parts = line.split(' ')
                    for part in parts:
                        if part.startswith('X'):
                            try:
                                current_position[0] = float(part[1:])
                            except ValueError:
                                pass
                        elif part.startswith('Y'):
                            try:
                                current_position[1] = float(part[1:])
                            except ValueError:
                                pass
                        elif part.startswith('Z'):
                            try:
                                current_position[2] = float(part[1:])
                            except ValueError:
                                pass
                    # Store the current position after processing the line
                    x.append(current_position[0])
                    y.append(current_position[1])
                    z.append(current_position[2])
    except FileNotFoundError:
        pass
        return np.array([]), np.array([]), np.array([])
    except Exception as e:
        pass
        return np.array([]), np.array([]), np.array([])

    return np.array(x), np.array(y), np.array(z)