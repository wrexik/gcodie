import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from PIL import Image
from io import BytesIO
import shutil

from datetime import datetime
import os

from .utils import *

# Generate an image of a single layer, starting from firt layer
def generate_layer_img(layer, x, y, z, output_dir, bg_color, layer_color, image_size):

    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if layer > layers:
        stats(f"Error: Layer {layer} is out of range. The model has {layers} layers.")
        return

    try:
        for layer in range(layer, layer + 1):
            fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square

            #not needed but what if
            try:
                fig.patch.set_facecolor(bg_color)  # Set the background color
            except Exception as e:
                stats(f"Error: Invalid color")

            # Filter points by layer height
            layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)  # Adjust the height step as needed
            
            # Check if there are points to plot

            if np.any(layer_points):
                #If yes, print message generating and scatter points
                stats(f"Generating image for layer {layer}")
                ax.scatter(x[layer_points], y[layer_points], c=layer_color, s=1)

            else:
                plt.close(fig)
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
            ax.axis('off')

            buf = BytesIO()
            plt.savefig(buf, bbox_inches='tight', pad_inches=0, format='png')
            plt.close(fig)

            buf.seek(0)
            with Image.open(buf) as img:
                img = img.resize(image_size, Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
                
                # Save the image with the correct filename for the current layer
                img.save(os.path.join(output_dir, f'layer_{layer:03d}.png')) 
                stats("Processing complete.")

            break #breakes the loop after generating the image

    except Exception as e:
        stats(f"Error generating images: {e}")

# Generate multiple layers, skipping any layers with no points, starting from the first layer
def generate_multiple_layers(count, x, y, z, output_dir, bg_color, layer_color, image_size):

    global no_stats

    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Adjust the height step as needed

    if count > layers:
        stats(f"Error: Requested count ({count}) exceeds the total number of layers ({layers}).")
        return

    stats(f"Generating images for {count} layers")

    skip = 0
    file_number = 1

    try:
        for layer in tqdm(range(count), desc='Images Processed', unit='image', colour='cyan'):
            fig, ax = plt.subplots(figsize=(8, 8))  # Make the plot square
            
            # Set the background color, handling any invalid color exceptions
            try:
                fig.patch.set_facecolor(bg_color)
            except Exception as e:
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
            ax.axis('off')

            buf = BytesIO()
            plt.savefig(buf, bbox_inches='tight', pad_inches=0, format='png')
            plt.close(fig)

            buf.seek(0)
            with Image.open(buf) as img:
                img = img.resize(image_size, Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
                
                # Save the image with a sequential filename
                img.save(os.path.join(output_dir, f'layer_{file_number:03d}.png')) 
                
            file_number += 1  # Increment file number for each image

        stats(f"{count - skip}/{count} images saved. {skip} layers skipped due to no points.")

    except Exception as e:
        stats(f"Error generating images: {e}")

# Generate all layers, including skipped ones (skipped ones will be the last image repeated)
def generate_all_layers(x, y, z, output_dir, bg_color, layer_color, image_size, make_animation):

    global no_stats
    
    os.makedirs(output_dir, exist_ok=True)
    layers = int(np.max(z) / 0.2) + 1  # Calculate the total number of layers

    stats(f"Generating images for {layers} layers")

    same_imgs = 0  # Counter for copied images
    file_number = 1  # Sequential file number

    try:
        for layer in tqdm(range(layers), desc='Images Processed', unit='image', colour='cyan'):
            fig, ax = plt.subplots(figsize=(8, 8))  # Create a square plot
            
            # Set the background color, handling invalid colors
            try:
                fig.patch.set_facecolor(bg_color)
            except Exception as e:
                stats(f"Error: Invalid background color '{bg_color}'. Defaulting to white.")
                fig.patch.set_facecolor('white')

            # Filter points by the current layer height
            layer_points = (z >= layer * 0.2) & (z < (layer + 1) * 0.2)
            
            # Check if there are points to plot for this layer
            if np.any(layer_points):
                ax.scatter(x[layer_points], y[layer_points], c=layer_color, s=1)

            # If no points are found, close the figure and copy last one
            else:
                plt.close(fig)
                
                # Handle the case where no points exist for the first layer
                if layer == 0:
                    skipped_first_layer = True
                    continue  # Skip the first layer if no points exist

                # Copy the previous layer's image if no points are found for non-first layers
                last_layer = layer - 1
                if os.path.exists(os.path.join(output_dir, f'layer_{last_layer:03d}.png')):
                    try:
                        shutil.copy(os.path.join(output_dir, f'layer_{last_layer:03d}.png'), 
                                    os.path.join(output_dir, f'layer_{file_number:03d}.png'))
                        same_imgs += 1
                    except Exception as e:
                        if no_stats == False:
                            stats(f"Error copying previous layer: {e}")
                file_number += 1  # Increment file number even when copying
                continue

            # Calculate limits to center the visualization
            x_min, x_max = x[layer_points].min(), x[layer_points].max()
            y_min, y_max = y[layer_points].min(), y[layer_points].max()

            # Ensure non-zero range to avoid collapsing axes
            x_range = max(x_max - x_min, 1e-5)
            y_range = max(y_max - y_min, 1e-5)
            max_range = max(x_range, y_range)

            x_center = (x_max + x_min) / 2
            y_center = (y_max + y_min) / 2

            ax.set_xlim(x_center - max_range / 2, x_center + max_range / 2)
            ax.set_ylim(y_center - max_range / 2, y_center + max_range / 2)

            ax.set_aspect('equal')
            ax.axis('off')  # Turn off the axes for a cleaner image

            # Save the figure to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, bbox_inches='tight', pad_inches=0, format='png')
            plt.close(fig)

            # Save the buffered image
            buf.seek(0)
            with Image.open(buf) as img:
                img = img.resize(image_size, Image.LANCZOS)
                img.save(os.path.join(output_dir, f'layer_{file_number:03d}.png'))

            file_number += 1  # Increment file number for each image

        if skipped_first_layer == True:
            stats("No points found for layer 1. Skipped image generation.")
        stats(f"{layers - same_imgs}/{layers} different images saved. {same_imgs} same images used")

    except Exception as e:
        stats(f"Error generating images: {e}")

    if make_animation:
        make_gif(output_dir)

#Gif creation
def make_gif(output_dir):
        global no_stats
        
        stats(f"make_animation is set to True. Creating animation")

        try:
            images = []
            for filename in tqdm(os.listdir(output_dir), desc='Images added to gif', unit='image', colour='cyan'):
                if filename.endswith('.png'):
                    images.append(Image.open(os.path.join(output_dir, filename)))

            stats(f"Processing {len(images)} images. Could take a while")
            # Save the images as an animated GIF
            images[0].save(os.path.join(output_dir, 'animation.gif'), save_all=True, append_images=images[1:], loop=0, duration=100)

            stats("Animation saved as 'animation.gif'")
    
        except Exception as e:
            stats(f"Error creating animation: {e}")