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

def get_moonraker_print_status(printer_ip, port):

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

        if current_layer and total_layer == None:
            stats("Couldnt find the layer information")
            layer_info = False

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

        return(response, layer_info, state, print_duration, filament_used, z_pos, filename)
    

    except requests.exceptions.RequestException as e:
        stats(f"An error occurred: {e}")
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
            return progress  # Return as percentage
        else:
            stats("Progress information is not available.")
            return None
    
    except requests.exceptions.RequestException as e:
        stats(f"An error occurred: {e}")
        return None