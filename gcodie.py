import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from datetime import datetime

global no_stats
no_stats = False

def stats(text):
    ctime = datetime.now().strftime("%H:%M:%S")
    print(f"[Status  -  {ctime}] Gcodie {text}")

def parse_gcode(file_path):

    global no_stats

    x, y, z = [], [], []
    current_position = [0, 0, 0]  # X, Y, Z coordinates

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('G1'):  # Only process movement commands
                    parts = line.split(' ')
                    for part in parts:
                        if part.startswith('X'):
                            try:
                                current_position[0] = float(part[1:])
                            except ValueError:

                                if no_stats == False:
                                    stats(f"Warning: Invalid X value '{part[1:]}' skipped.")

                        elif part.startswith('Y'):
                            try:
                                current_position[1] = float(part[1:])
                            except ValueError:
                                if no_stats == False:
                                    stats(f"Warning: Invalid Y value '{part[1:]}' skipped.")
                        elif part.startswith('Z'):
                            try:
                                current_position[2] = float(part[1:])
                            except ValueError:
                                if no_stats == False:
                                    stats(f"Warning: Invalid Z value '{part[1:]}' skipped.")
                    # Store the current position after processing the line
                    x.append(current_position[0])
                    y.append(current_position[1])
                    z.append(current_position[2])
    except FileNotFoundError:
        if no_stats == False:
            stats(f"Error: File '{file_path}' not found.")
        return np.array([]), np.array([]), np.array([])
    except Exception as e:
        if no_stats == False:
            stats(f"Error reading G-code file: {e}")
        return np.array([]), np.array([]), np.array([])

    return np.array(x), np.array(y), np.array(z)

def parse_gcode_silent(file_path):

    global no_stats

    x, y, z = [], [], []
    current_position = [0, 0, 0]  # X, Y, Z coordinates

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('G1'):  # Only process movement commands
                    parts = line.split(' ')
                    for part in parts:
                        if part.startswith('X'):
                            try:
                                current_position[0] = float(part[1:])
                            except ValueError:
                                pass
                        elif part.startswith('Y'):
                            try:
                                current_position[1] = float(part[1:])
                            except ValueError:
                                pass
                        elif part.startswith('Z'):
                            try:
                                current_position[2] = float(part[1:])
                            except ValueError:
                                pass
                    # Store the current position after processing the line
                    x.append(current_position[0])
                    y.append(current_position[1])
                    z.append(current_position[2])
    except FileNotFoundError:
        pass
        return np.array([]), np.array([]), np.array([])
    except Exception as e:
        pass
        return np.array([]), np.array([]), np.array([])

    return np.array(x), np.array(y), np.array(z)

def generate_layer_img(layer, x, y, z, output_dir, bg_color, layer_color, image_size):

    global no_stats

    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if layer > layers:
        if no_stats == False:
            stats(f"Error: Layer {layer} is out of range. The model has {layers} layers.")
        return

    try:
        fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square

        #not needed but what if
        try:
            fig.patch.set_facecolor(bg_color)  # Set the background color
        except Exception as e:
            if no_stats == False:
                stats(f"Error: Invalid color")

        # Filter points by layer height
        layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)  # Adjust the height step as needed
        
        # Check if there are points to plot

        if np.any(layer_points):
            #If yes, print message generating and scatter points
            if no_stats == False:
                stats(f"Generating image for layer {layer}...")
            ax.scatter(x[layer_points], y[layer_points], c=layer_color, s=1)

        else:
            plt.close(fig)
            if no_stats == False:
                stats(f"No points found for layer {layer}.")
            return

        # Calculate limits to center the visualization
        x_min, x_max = x[layer_points].min(), x[layer_points].max()
        y_min, y_max = y[layer_points].min(), y[layer_points].max()

        # Set limits to ensure 1:1 aspect ratio
        x_range = x_max - x_min
        y_range = y_max - y_min
        max_range = max(x_range, y_range)

        x_center = (x_max + x_min) / 2
        y_center = (y_max + y_min) / 2

        ax.set_xlim(x_center - max_range / 2, x_center + max_range / 2)
        ax.set_ylim(y_center - max_range / 2, y_center + max_range / 2)

        ax.set_aspect('equal')
        ax.axis('off')  # Turn off axis

        # Save the figure to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, bbox_inches='tight', pad_inches=0, format='png')
        plt.close(fig)

        # Rewind the buffer and save it as an image file
        buf.seek(0)
        with Image.open(buf) as img:
            img = img.resize(image_size, Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
            
            # Save the image with the correct filename for the current layer
            img.save(os.path.join(output_dir, f'layer_{layer:03d}.png'))
        if no_stats == False: 
            stats("Processing complete.")

    except Exception as e:
        if no_stats == False:
            stats(f"Error generating images: {e}")

def generate_multiple_layers(count, x, y, z, output_dir, bg_color, layer_color, image_size):

    global no_stats

    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if count > layers:
        if no_stats == False:
            stats(f"Error: Requested count ({count}) exceeds the total number of layers ({layers}).")
        return

    if no_stats == False:
        stats(f"Generating images for {count} layers...")

    skip = 0  # Count skipped layers
    file_number = 1  # Start file numbering from 1

    try:
        for layer in tqdm(range(count), desc='Images Processed', unit='image', colour='green'):
            fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square
            
            # Set the background color, handling any invalid color exceptions
            try:
                fig.patch.set_facecolor(bg_color)
            except Exception as e:
                if no_stats == False:
                    stats(f"Error: Invalid background color '{bg_color}'. Defaulting to white.")
                fig.patch.set_facecolor('white')

            # Filter points by layer height
            layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)  # Adjust the height step as needed
            
            # Check if there are points to plot
            if np.any(layer_points):
                ax.scatter(x[layer_points], y[layer_points], c=layer_color, s=1)
            else:
                plt.close(fig)
                skip += 1
                continue

            # Calculate limits to center the visualization
            x_min, x_max = x[layer_points].min(), x[layer_points].max()
            y_min, y_max = y[layer_points].min(), y[layer_points].max()

            # Ensure that the range is non-zero to avoid collapsing axes
            x_range = max(x_max - x_min, 1e-5)
            y_range = max(y_max - y_min, 1e-5)
            max_range = max(x_range, y_range)

            x_center = (x_max + x_min) / 2
            y_center = (y_max + y_min) / 2

            ax.set_xlim(x_center - max_range / 2, x_center + max_range / 2)
            ax.set_ylim(y_center - max_range / 2, y_center + max_range / 2)

            ax.set_aspect('equal')
            ax.axis('off')  # Turn off axis

            # Save the figure to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, bbox_inches='tight', pad_inches=0, format='png')
            plt.close(fig)

            # Rewind the buffer and save it as an image file
            buf.seek(0)
            with Image.open(buf) as img:
                img = img.resize(image_size, Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
                
                # Save the image with a sequential filename
                img.save(os.path.join(output_dir, f'layer_{file_number:03d}.png')) 
                
            file_number += 1  # Increment file number for each image

        if no_stats == False:
            stats(f"{count - skip}/{count} images saved. {skip} layers skipped due to no points.")

    except Exception as e:

        if no_stats == False:
            stats(f"Error generating images: {e}")

def last_layer(gcode_path):

    global no_stats

    x, y, z = parse_gcode_silent(gcode_path)
    last_layer =  int(np.max(z) / 0.2) + 1

    last_layer = last_layer - 1 # usually last layer is nothing

    if no_stats == False:
        stats(f"Last layer is {last_layer}")

    return last_layer

def first_layer(gcode_path):

    global no_stats

    x, y, z = parse_gcode_silent(gcode_path)
    first_layer =  int(np.min(z) / 0.2) + 1

    if no_stats == False:
        stats(f"First layer is {first_layer}")

    return first_layer

def echo(args):
    global no_stats

    if args == True:
        no_stats = True
    if args == False:
        no_stats = False
    if args == None:
        no_stats = False