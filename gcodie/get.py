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

        stats(colored("\nLayer info:" +  f"""\nCurrent layer: {int(current_layer)} \nTotal layeres: {int(layer_count)}""", "cyan"))

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
    
def get_current_temps(printer_ip, port):
    """
    Retrieves the current temperatures of the printer from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        dict: The current temperatures of the printer, or None if an error occurs.
    """

    # -> /printer/objects/query?extruder
    # -> /printer/objects/query?heater_bed

    try:
        url_extruder = f"http://{printer_ip}:{port}/printer/objects/query?extruder"
        url_heater_bed = f"http://{printer_ip}:{port}/printer/objects/query?heater_bed"

        response_extruder = requests.get(url_extruder)
        response_extruder.raise_for_status()  # Raise an exception for HTTP errors
        response_heater_bed = requests.get(url_heater_bed)
        response_heater_bed.raise_for_status()  # Raise an exception for HTTP errors

        extruder_temps = response_extruder.json()
        heater_bed_temps = response_heater_bed.json()

        extruder_temps = extruder_temps['result']['status']['extruder']['temperature']
        heater_bed_temps = heater_bed_temps['result']['status']['heater_bed']['temperature']
        
        stats(colored("\nTemps:" + f"""\nExtruder: {extruder_temps}\nBed: {heater_bed_temps}""", "cyan"))

        return extruder_temps, heater_bed_temps
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        return None
    
def get_current_powers(printer_ip, port):
    """
    Retrieves the current power percentage of the heating elements from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        dict: The current power in %, or None if an error occurs.
    """
    # -> /printer/objects/query?extruder
    # -> /printer/objects/query?heater_bed

    #{'result': {'eventtime': 8972.150803832, 'status': {'extruder': {'temperature': 82.6, 'target': 0.0, 'power': 0.0, 'can_extrude': False, 'pressure_advance': 0.036, 'smooth_time': 0.04}}}}Bed: {'result': {'eventtime': 8972.401332999, 'status': {'heater_bed': {'temperature': 46.68, 'target': 0.0, 'power': 0.0}}}}

    try:
        url_extruder = f"http://{printer_ip}:{port}/printer/objects/query?extruder"
        url_heater_bed = f"http://{printer_ip}:{port}/printer/objects/query?heater_bed"

        response_extruder = requests.get(url_extruder)
        response_extruder.raise_for_status()  # Raise an exception for HTTP errors
        response_heater_bed = requests.get(url_heater_bed)
        response_heater_bed.raise_for_status()  # Raise an exception for HTTP errors

        extruder_power = response_extruder.json()
        heater_bed_power = response_heater_bed.json()

        extruder_power = extruder_power['result']['status']['extruder']['power']
        heater_bed_power = heater_bed_power['result']['status']['heater_bed']['power']
        
        stats(colored("\nPower:" + f"""\nExtruder: {extruder_power}\nBed: {heater_bed_power}""", "cyan"))

        return extruder_power, heater_bed_power
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        return None
    
def get_current_speed(printer_ip, port):
    """
    Retrieves the current speed of the printer from a Moonraker instance using HTTP.
    args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.
    Returns:
        dict: The current speed of the printer, or None if an error occurs.
    """
    """
        {
        "speed_factor": 1.0,
        "speed": 100.0,
        "extrude_factor": 1.0,
        "absolute_coordinates": true,
        "absolute_extrude": false,
        "homing_origin": [0.0, 0.0, 0.0, 0.0],
        "position": [0.0, 0.0, 0.0, 0.0],
        "gcode_position": [0.0, 0.0, 0.0, 0.0]
        }
    """

    try:
        url = f"http://{printer_ip}:{port}/printer/objects/query?gcode_move"

        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        speed = response.json()
        speed = speed['result']['status']['gcode_move']['speed']
        
        stats(colored(f"Speed: {speed}", "cyan"))

        return speed
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        return None


def pause_print(printer_ip, port):
    """
    Pauses the print job on the printer using Moonraker.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        bool: True if the print job was paused successfully, False otherwise.
    """

    url = f"http://{printer_ip}:{port}/printer/print/pause"
    
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        stats("Print job paused.")
        return True
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        return False


    
def resume_print(printer_ip, port):
    """
    Resumes the print job on the printer using Moonraker.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        bool: True if the print job was resumed successfully, False otherwise.
    """

    url = f"http://{printer_ip}:{port}/printer/print/resume"
    
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        stats("Print job resumed.")
        return True
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        return False
    
def cancel_print(printer_ip, port):
    """
    Cancels the print job on the printer using Moonraker.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        bool: True if the print job was canceled successfully, False otherwise.
    """

    url = f"http://{printer_ip}:{port}/printer/print/cancel"
    
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        stats("Print job canceled.")
        return True
    
    except requests.exceptions.RequestException as e:
        stats(colored(f"An error occurred: {e}", "red"))
        return False
    
def get_moonraker_state(printer_ip, port):
    """
    Retrieves the current state of the printer from a Moonraker instance using HTTP.

    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        str: The current state of the printer, or None if an error occurs.
    """
    
    try:
        response, current_layer, total_layer, state, print_duration, filament_used, z_pos, filename = get_moonraker_stats(printer_ip, port)
    except Exception as e:
        stats(colored(f"Couldnt reach moonraker at {printer_ip}:{port}: {e}", "red"))
        stats(colored("Check if your printer is connected to internet, set static IP", "yellow"))
        exit()
    
    """
    state: Current print state. Can be one of the following values:
    "standby"
    "printing"
    "paused"
    "complete"
    "cancelled"
    "error" - Note that if an error is detected the print will abort
    """
    
    if state == "printing":
        stats(colored(f"Printer is currently printing.", "green"))
        return True, state
    elif state == "paused":
        stats(colored(f"Printer is currently paused.", "yellow"))
        return False, state
    elif state == "standby":
        stats(f"Printer is currently in standby.", "yellow")
        return False, state
    elif state == "complete":
        stats(f"Print is complete.", "green")
        return False, state
    elif state == "cancelled":
        stats(colored(f"Print was cancelled.", "yellow"))
        return False, state
    elif state == "error":
        stats(colored(f"Print encountered an error.", "red"))
        return False, state
        



        