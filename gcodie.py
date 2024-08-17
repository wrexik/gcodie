import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from PIL import Image
from io import BytesIO

def parse_gcode(file_path):
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
                                print(f"Warning: Invalid X value '{part[1:]}' skipped.")
                        elif part.startswith('Y'):
                            try:
                                current_position[1] = float(part[1:])
                            except ValueError:
                                print(f"Warning: Invalid Y value '{part[1:]}' skipped.")
                        elif part.startswith('Z'):
                            try:
                                current_position[2] = float(part[1:])
                            except ValueError:
                                print(f"Warning: Invalid Z value '{part[1:]}' skipped.")
                    # Store the current position after processing the line
                    x.append(current_position[0])
                    y.append(current_position[1])
                    z.append(current_position[2])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return np.array([]), np.array([]), np.array([])
    except Exception as e:
        print(f"Error reading G-code file: {e}")
        return np.array([]), np.array([]), np.array([])

    return np.array(x), np.array(y), np.array(z)

def parse_gcode_silent(file_path):
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

def generate_layer_img(layer, x, y, z, output_dir, image_size=(800, 800)):
    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if layer >= layers:
        print(f"Error: Layer {layer} is out of range. The model has {layers} layers.")
        return

    print(f"Generating image for layer {layer}...")

    try:
        fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square

        # Filter points by layer height
        layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)  # Adjust the height step as needed
        
        # Check if there are points to plot
        if np.any(layer_points):
            ax.scatter(x[layer_points], y[layer_points], c='blue', s=1)
        else:
            plt.close(fig)
            print(f"No points found for layer {layer}.")
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
            
        print("Processing complete.")

    except Exception as e:
        print(f"Error generating images: {e}")


def generate_multiple_layers(count, x, y, z, output_dir, image_size=(800, 800)):
    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if count > layers:
        print(f"Error: Requested {count} layers but the model has only {layers} layers.")
        return

    print(f"Generating images for {count} layers...")

    skip = 0 # Count skipped layers

    try:
        file_number = 1  # Start file numbering from 1
        for layer in tqdm(range(count), desc='Images Processed', unit='image', colour='green'):
            fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square

            # Filter points by layer height
            layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)  # Adjust the height step as needed
            
            # Check if there are points to plot
            if np.any(layer_points):
                ax.scatter(x[layer_points], y[layer_points], c='blue', s=1)
            else:
                plt.close(fig)
                skip = skip + 1
                continue

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
                
                # Save the image with a sequential filename
                img.save(os.path.join(output_dir, f'layer_{file_number:03d}.png')) 
                
            file_number += 1  # Increment file number for each image
        print(f"{count - skip}/{count} images saved. {skip} skipped 0 point layers.")
        print("Processing complete.")
        

    except Exception as e:
        print(f"Error generating images: {e}")

def last_layer(gcode_path):
    x, y, z = parse_gcode_silent(gcode_path)
    last_layer =  int(np.max(z) / 0.2) + 1
    print(f"Last layer is {last_layer}")

    return last_layer
