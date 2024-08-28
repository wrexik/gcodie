import os
import json
import requests
import numpy as np

CACHE_DIR = 'gcode_cache'
CACHE_EXTENSION = '.json'

from .utils import stats

def download_and_cache_file(printer_ip, port, file_path, cache_dir=CACHE_DIR):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    cache_file_path = os.path.join(cache_dir, file_path.replace('/', '_') + CACHE_EXTENSION)

    if os.path.exists(cache_file_path):
        stats(f"File already cached: {cache_file_path}")
        return cache_file_path

    full_url = f"http://{printer_ip}:{port}/server/files/gcodes/{file_path}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        
        with open(cache_file_path, 'w') as file:
            file.write(response.text)
        
        stats(f"Cached file saved to {cache_file_path}")
        return cache_file_path
    
    except requests.exceptions.RequestException as e:
        stats(f"An error occurred while downloading the file: {e}")
        return None

def parse(file_path):
    cache_file_path = file_path + CACHE_EXTENSION
    
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as cache_file:
            data = json.load(cache_file)
            return np.array(data['z'])

    z = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                
                if not line or not line.startswith('G1'):
                    continue
                
                parts = line.split(' ')
                for part in parts:
                    if part.startswith('Z'):
                        try:
                            z_value = float(part[1:])
                            z.append(z_value)
                        except ValueError:
                            stats(f"Warning: Invalid Z value '{part[1:]}' skipped.")

        with open(cache_file_path, 'w') as cache_file:
            json.dump({'z': z}, cache_file)
        
        stats(f"Parsed and cached data for {file_path}.")

    except FileNotFoundError:
        stats(f"Error: File '{file_path}' not found.")
        return np.array([])
    except Exception as e:
        stats(f"Error reading G-code file: {e}")
        return np.array([])

    return np.array(z)

def estimate_current_layer(printer_ip, port, file_path, z_position):
    cached_file_path = download_and_cache_file(printer_ip, port, file_path)
    
    if not cached_file_path:
        stats("Could not cache the current file.")
        return None

    z_positions = parse(cached_file_path)

    if len(z_positions) == 0:
        stats("Could not parse Z positions from the cached file.")
        return None

    # Estimate layer thickness
    min_z = np.min(z_positions)
    max_z = np.max(z_positions)
    num_layers = len(z_positions)
    
    if num_layers < 2:
        stats("Not enough Z positions to estimate layer thickness.")
        return None
    
    layer_thickness = (max_z - min_z) / (num_layers - 1)
    
    # Estimate the current layer
    estimated_layer = int((z_position - min_z) / layer_thickness) + 1

    # Ensure the layer number is within valid bounds
    if estimated_layer < 1:
        estimated_layer = 1
    elif estimated_layer > num_layers:
        estimated_layer = num_layers

    return estimated_layer