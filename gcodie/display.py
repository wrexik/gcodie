from .utils import *
from .get import *
from .images import *
from .parse import *


from PIL import Image

def show_current_layer(printer_ip, port, image_size=(800, 800), bg_color="#000000", layer_color="#ff007b", output_dir="current_layer"):
    """
    Display the current layer of a print job in a window.
    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        error: If an error occurs, the error message is displayed.
    """
    current_layer, _ = get_moonraker_layer(printer_ip, port)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(os.path.join(output_dir, "current_layer.txt"), "r") as f:
            saved_layer = f.read().strip()
            f.close()
    except Exception as e:
        saved_layer = None

    if str(current_layer) == saved_layer:
        stats("Layer already processed.")
        return
    else:
        stats("New job found.")
        remove_files(output_dir)

    with open(os.path.join(output_dir, "current_layer.txt"), "w") as f:
        f.write(str(current_layer))
        f.close()

    try:
        gcode_path = get_current_file(printer_ip, port)
    except Exception as e:
        stats(f"No print job found: {e}")
        return

    x, y, z = parse_gcode(gcode_path)

    try:
        path = generate_layer_img(current_layer, x, y, z, output_dir, bg_color, layer_color, image_size)
    except Exception as e:
        while True:
            stats(f"No points found for layer {current_layer}.")
            stats("Getting the next layer.")
            try:
                current_layer += 1
                path = generate_layer_img(current_layer, x, y, z, output_dir, bg_color, layer_color, image_size)
                break
            except Exception as e:
                stats(f"Error: {e}")
                return

    try:
        img = Image.open(path)
        img.show()
    except Exception as e:
        stats(f"Error: {e}")
        return

def animate_current_print(printer_ip, port, image_size=(800, 800), bg_color="#000000", layer_color="#ffffff", output_dir="animation"):
    """
    Display the current layer of a print job in a window.
    Args:
        printer_ip (str): The IP address of the printer running Moonraker.
        port (int): The port on which Moonraker is running.

    Returns:
        error: If an error occurs, the error message is displayed.
    """
    try:
        gcode_path = get_current_file(printer_ip, port)
    except Exception as e:
        stats(f"No print job found: {e}")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        path = os.path.join(output_dir, "current_job.txt")
        with open(path, "r") as f:
            current_job = f.read().strip()
            f.close()
    except Exception as e:
        current_job = None
    
    if gcode_path == current_job:
        stats("Print job already processed.")
        return
    else:
        stats("New print job found.")
        remove_files(output_dir)
    
    path = os.path.join(output_dir, "current_job.txt")
    with open(path, "w") as f:
        f.write(gcode_path)
        f.close()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    x, y, z = parse_gcode(gcode_path)

    path = generate_all_layers(x, y, z, output_dir, bg_color, layer_color, image_size, make_animation=False)
    
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

    try:
        path = os.path.join(output_dir, "animation.gif")
        img = Image.open(path)
        img.show()
    except Exception as e:
        stats(f"Error: {e}")
        return
    
    try:
        #delete all .png files in the output_dir
        stats("Cleaning up...")
        
        for file in os.listdir(output_dir):
            if file.endswith(".png"):
                os.remove(os.path.join(output_dir, file))
    except Exception as e:
        stats(f"Error: {e}")
        return  
    
    




