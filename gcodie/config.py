import configparser as cf

def load_config():
    """
    Load the configuration file.
    Returns:
        dict: The configuration dictionary.
    """
    config = cf.ConfigParser()
    config.read("config.ini")
    return config

def get_config_value(section, key):
    """
    Get a value from the configuration file.
    Args:
        section (str): The section to get the value from.
        key (str): The key to get the value for.
    Returns:
        str: The value for the given key.
    """
    config = cf.ConfigParser()
    config.read("config.ini")
    return config[section][key]

def create_config():
    """
    Create a new configuration file.
    """
    config = cf.ConfigParser()
    config["PRINTER"] = {
        "printer_ip": "10.0.0.150",
        "port": "7125"
    }
    config["IMAGE"] = {
        "image_size": "(400, 400)",
        "bg_color": "#000000",
        "layer_color": "#ffffff"
    }
    config["FONT"] = {
        "font_path": "C:/Windows/Fonts/Arial.ttf"
    }
    config["OUTPUT"] = {
        "output_dir": "output"
    }
    config["DEBUG"] = {
        "debug": "False"
    }

    with open("config.ini", "w") as configfile:
        config.write(configfile)