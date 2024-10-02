import configparser as cf # Importing the configparser module
import os # Importing the os module

def load_config():
    """
    Load the configuration file.
    Returns:
        dict: The configuration dictionary.
    """
    config = cf.ConfigParser() # Creating a ConfigParser object
    config.read("config.ini") # Reading the configuration file
    return config # Returning the configuration dictionary

def get_config_value(config, section, key):
    """
    Get a value from the configuration file.
    Args:
        config (dict): The configuration dictionary.
        section (str): The section to get the value from.
        key (str): The key to get the value for.
    Returns:
        str: The value for the given key.
    """
    return config[section][key] # Returning the value for the given key

def create_config():
    """
    Create a new configuration file.
    """
    config = cf.ConfigParser()
    config["PRINTER"] = { # Setting the default values
        "printer_ip": "10.0.0.150",
        "port": "7125"}

    config["IMAGE"] = {
        "image_size": "(400, 400)",
        "bg_color": "#000000",
        "layer_color": "#ffffff"}
    
    config["FONT"] = {
        "font_path": "C:/Windows/Fonts/Arial.ttf"}
    
    config["OUTPUT"] = {
        "output_dir": "current_layer"}
    
    with open("config.ini", "w") as f:
        config.write(f)
        f.close()