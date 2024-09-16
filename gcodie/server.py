# Desc: Server side code for Gcodie
import socket
import json
import threading

from .utils import *
from .get import *
from .images import *


# make function to listen for instructions
def handle_client(client, addr):
    stats('Instructions from ', addr)
    # Receive the message
    message = client.recv(1024).decode()
    try:
        # Parse the JSON message
        data = json.loads(message)
        command = data.get("command")
        printer_ip = data.get("printer_ip")
        port = data.get("port")
        
        # Process the message
        if command == "get_moonraker_layer":
            try:
                current_layer, layer_count = get_moonraker_layer(printer_ip, port)
                response = { "current_layer": current_layer, "layer_count": layer_count }
            except Exception as e:
                response = { "error": str(e) }
        else:
            response = { "error": "Unknown command" }
    except json.JSONDecodeError:
        response = { "error": "Invalid JSON format" }

    # Send the response back to the client
    client.send(json.dumps(response).encode())
    # Close the connection with the client
    client.close()

def server():
    """
    Listen for instructions from the client.
    """
    # Create a socket object

    stats("Listening")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Get local machine name
    host = socket.gethostname()
    port = 7125
    # Bind to the port
    server.bind((host, port))
    # Now wait for client connection.
    server.listen(5)
    while True:
        # Establish connection with client.
        client, addr = server.accept()
        # Handle the client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()
