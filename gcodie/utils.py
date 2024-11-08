from datetime import datetime
import os
import time

import colorama

def stats(text):
    ctime = datetime.now().strftime("%H:%M:%S")
    flower = colored("✿", "magenta")
    minus = colored("-", "magenta")

    out = f"[Status  {minus}  {ctime}] Gcodie{flower}  {text}"

    if text == "":
        return out
    else:
        print(f"[Status  {minus}  {ctime}] Gcodie{flower}  {text}")

    

# Clear the screen
def tidy():
    """
    Clear the screen.
    """

    global no_stats

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        stats(f"Error while clearing the screen: {e}")

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

def measure_execution_time(func):
    def timed_execution(*args, **kwargs):
        start_timestamp = time.time()
        result = func(*args, **kwargs)
        end_timestamp = time.time()
        execution_duration = end_timestamp - start_timestamp
        print(f"Function {func.__name__} took {execution_duration:.2f} seconds to execute")
        return result
    return timed_execution

def get_os():
    """
    Get the operating system.
    Returns:
        str: The operating system.
    """
    if os.name == "nt":
        return "Windows"
    elif os.name == "posix":
        return "Linux"
    
def am_i_windows():
    """
    Check if the operating system is Windows.
    Returns:
        bool: True if the operating system is Windows, False otherwise.
    """
    return get_os() == "Windows"