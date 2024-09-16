import socket
import json
import threading

from .utils import *
from .get import *
from .images import *


def request(command, printer_ip, port):
    """
    Args:
        command (str): The command to be sent to the server.
        printer_ip (str): The IP address of the printer.
        port (int): The port number to connect to.
    Returns:
        dict: The response from the server.
    Raises:
        socket.error: If there is an error creating or connecting the socket.
        json.JSONDecodeError: If there is an error encoding or decoding the message to/from JSON.
    """
    try:
        # Create a socket object
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        client.connect((printer_ip, port))
        # Send a message to the server
        message = json.dumps({"command": command, "printer_ip": printer_ip, "port": port})
        client.send(message.encode())
        
        # Receive the response from the server
        response = client.recv(1024).decode()
        client.close()
        
        # Parse the response
        response = json.loads(response)
        return response
    except socket.error as e:
        print(f"Socket error: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

    