import requests
import json
import time
import os
import re

# This is the bridge.py that will be used to communicate with the 3d printer
#  https://moonraker.readthedocs.io/en/latest/web_api/#get-system-info

import socket
import json

from .utils import *

def get_moonraker_stats(printer_ip, port):

    # Initialize variables
    response = None
    layer_info = None
    state = None
    print_duration = None
    filament_used = None
    z_pos = None
    filename = None

    """
    Retrieves print status information from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        dict: Print status information in JSON format, or None if an error occurs.
    """
    url = f"http://{printer_ip}:{port}/printer/objects/query?print_stats"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response = response.json()
    
        #{'result': {'eventtime': 2235.215919333, 'status': {'print_stats': {'filename': '', 'total_duration': 0.0, 'print_duration': 0.0, 'filament_used': 0.0, 'state': 'standby', 'message': '', 'info': {'total_layer': None, 'current_layer': None}, 'power_loss': 0, 'z_pos': 11.2}}}}

        current_layer = response['result']['status']['print_stats']['info']['current_layer']
        total_layer = response['result']['status']['print_stats']['info']['total_layer']

        state = response['result']['status']['print_stats']['state']
        print_duration = response['result']['status']['print_stats']['print_duration']
        filament_used = response['result']['status']['print_stats']['filament_used']
        z_pos = response['result']['status']['print_stats']['z_pos']

        filename = response['result']['status']['print_stats']['filename']

        if filename == '':
            filename = None

        #how to use the data in return:
        #def get_user_data():
        #    return 'Anna', 23, 'anna123'
        
        #----> name, age, id = get_user_data()

        return(response, current_layer, total_layer, state, print_duration, filament_used, z_pos, filename)
    

    except requests.exceptions.RequestException as e:
        stats(colored(f"Couldnt reach moonraker at {printer_ip}:{port}: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        return None
    

def get_moonraker_progress(printer_ip, port):
    """
    Retrieves the print percentage from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        float: The print progress as a percentage, or None if an error occurs.
    """
    url = f"http://{printer_ip}:{port}/printer/objects/query?display_status"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        print_status = response.json()

        # Access the progress value directly
        progress = print_status['result']['status']['display_status']['progress']
        if progress == 1.0:
            progress = 100
        else:
            progress = progress * 100
    
        if progress is not None:
            #stats(f"Progress: {progress:.2f}%")
            return progress  # Return as percentagef
        else:
            stats("Progress information is not available.")
            return None
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"Couldnt reach moonraker at {printer_ip}:{port}: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        return None
    
def get_moonraker_layer(printer_ip, port):
    """
    Retrieves the current layer and all layers information from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.
        filename (str): The name of the file being printed.

    Returns:
        tuple: The current layer number and total layer count, or None if an error occurs.
    """
    try:
        filename = get_moonraker_stats(printer_ip, port)[7]
    except Exception as e:
        stats(colored(f"Couldnt reach moonraker at {printer_ip}:{port}: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        exit()

    try:
        progress = get_moonraker_progress(printer_ip, port)
    except Exception as e:
        stats(colored(f"Couldnt reach moonraker at {printer_ip}:{port}: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        exit()

    url_gcode_move = f"http://{printer_ip}:{port}/printer/objects/query?gcode_move"
    url_metadata = f"http://{printer_ip}:{port}/server/files/metadata?filename={filename}"

    try:
        # Get current position
        response_gcode_move = requests.get(url_gcode_move)
        response_gcode_move.raise_for_status()  # Raise an exception for HTTP errors
        layer_info = response_gcode_move.json()

        current_position = layer_info['result']['status']['gcode_move']['gcode_position'][2]

        # Get layer height
        response_metadata = requests.get(url_metadata)
        response_metadata.raise_for_status()  # Raise an exception for HTTP errors
        metadata = response_metadata.json()

        layer_height = metadata['result']['layer_height']
        layer_count = metadata['result']['layer_count']

        # To not get invalid values
        if int(progress) == 100:
            current_layer = layer_count

        else:
            current_layer = current_position / layer_height

        return int(current_layer), layer_count
    
    except requests.exceptions.RequestException as e:
        stats(f"An error occurred: {e}")
        return None
    
def get_current_file(printer_ip, port):
    """
    Retrieves the current file being printed from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        str: The name of the file being printed, or None if an error occurs.
    """
    filename = get_moonraker_stats(printer_ip, port)[7]


    cache_dir = "cache"

    try:
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        #check for old cache files
        for file in os.listdir(cache_dir):
            if file != filename:
                os.remove(os.path.join(cache_dir, file))

        if filename is not None:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
        
        cache_file_path = os.path.join(cache_dir, filename.replace('/', '_'))

        if os.path.exists(cache_file_path):
            stats(f"File already cached: {cache_file_path}")
            return cache_file_path

        full_url = f"http://{printer_ip}:{port}/server/files/gcodes/{filename}"

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            
            with open(cache_file_path, 'w') as file:
                file.write(response.text)
            
            stats(f"Cached file saved to {cache_file_path}")
            return cache_file_path
        
        except requests.exceptions.RequestException as e:
            stats(colored(f"An error occurred while downloading the file: {e}", "red"))
            return None
        
    except requests.exceptions.RequestException as e:
        stats(colored(f"Error: {e}", "red"))
        return None
        