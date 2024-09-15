from datetime import datetime
import os

import colorama

def stats(text):
    ctime = datetime.now().strftime("%H:%M:%S")
    print(f"[Status  -  {ctime}] Gcodie✿  {text}")

# Clear the screen
def tidy():

    global no_stats

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        stats(f"Error while clearing the screen: {e}")
    stats("Screen cleared")

def clear_cache():
    """
    Clean up the cache directory.
    """
    try:
        for file in os.listdir("cache"):
            file_path = os.path.join("cache", file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        stats(f"Error while cleaning up the cache: {e}")
    stats(" ")
    stats("Cache cleaned up")

def remove_files(directory):
    """
    Remove all files in a directory.
    Args:
        directory (str): The directory to remove files from.
    """
    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        stats(f"Error while removing files: {e}")
    stats("Files removed")

def cleanup():
    """
    Clean up the cache and current_layer and frames directories.
    """
    clear_cache()
    remove_files("current_layer")
    remove_files("frames")
    stats("Cleanup complete")

def colored(text, color):
    """
    Color the text.
    Args:
        text (str): The text to color.
        color (str): The color to use.
    Returns:
        str: The colored text.
    """
    return colorama.Fore.__dict__[color.upper()] + text + colorama.Fore.RESET