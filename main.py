import gcodie as gc

import time
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

# G L I V E
# This is the optional main file to the Gcodie project
# Program outputs the current layer of the print job with information on the same image
# Has the basic logic to detect calibration and print job completion
# gcodie is my library for interacting with Moonraker API and generating the images

font_path = r"./rainbow100.ttf"  # Adjust the font path as needed for Windows
# Start of main.py

async def get_layer(printer_ip, port, image_size, bg_color, layer_color, debug):
    # Generate the image for the current layer
    # Prepare for applying the stats to the image

    output_dir = "glive"

    if debug == True:
        current_layer = 39
    else:
        current_layer, _ = gc.get_moonraker_layer(printer_ip, port)
        if current_layer == None:
            gc.stats("No layer found. Exiting.")
            return
        if current_layer == 0:
            gc.stats("No layer found. Exiting.")
            return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(os.path.join(output_dir, "current_layer.txt"), "r") as f:
            saved_layer = f.read().strip()
            f.close()
    except Exception as e:
        saved_layer = None

    if str(current_layer) == saved_layer:
        gc.stats("Layer already processed.")
        try:
            path = os.path.abspath(os.path.join(output_dir, f"layer_{current_layer:03d}.png"))
            return path
        except Exception as e:
            gc.stats(f"Error: {e}")
            return
    else:
        gc.stats("New layer found. Processing now!")
        gc.remove_files(output_dir)

    with open(os.path.join(output_dir, "current_layer.txt"), "w") as f:
        f.write(str(current_layer))
        f.close()

    if debug == True:
        gcode_path = os.path.join("tests", "test.gcode")
    else:
        try:
            gcode_path = gc.get_current_file(printer_ip, port)
        except Exception as e:
            gc.stats(gc.colored(f"No print job found: {e}"), "red")

    x, y, z = gc.parse_gcode(gcode_path)

    try:
        gc.stats(f"Generating image for layer {current_layer}")
        path = gc.generate_layer_img(current_layer, x, y, z, output_dir, bg_color, layer_color, image_size)

        if path is None:
            while True:

                current_layer += 1

                with open(os.path.join(output_dir, "current_layer.txt"), "w") as f:
                    f.write(str(current_layer))
                    f.close()
                try:
                    path = gc.generate_layer_img(current_layer, x, y, z, output_dir, bg_color, layer_color, image_size)
                    break

                except Exception as e:
                    gc.stats(f"Error: {e}")

    except Exception as e:
        gc.stats(f"Error: {e}")
        return
            
    return path

async def get_current_stats(printer_ip, port, path, debug):
    # Write the temps, powers, and speed to the image

    gc.stats("Updating the image with stats:")

    output_dir = "glive"

    if debug == True:
        progress = 100
        extruder_temps = 200; heater_bed_temps = 60
        extruder_power = 0.5; heater_bed_power = 0.5
        current_speed = 3000
    else:
        try:
            progress = gc.get_moonraker_progress(printer_ip, port)
            extruder_temps, heater_bed_temps = gc.get_current_temps(printer_ip, port)
            extruder_power, heater_bed_power = gc.get_current_powers(printer_ip, port)
            current_speed = gc.get_current_speed(printer_ip, port)

        except Exception as e:
            gc.stats(f"Error: {e}")
            return

    if path:
        with Image.open(path) as im:
            # Scale the image to fit the stats
            im = im.resize((380, 380))

            cl = cl.canvas = Image.new("RGB", (400, 400))
            cl.paste(im, (10, 10))

            draw = ImageDraw.Draw(cl)
            font = ImageFont.truetype(font_path, 20)

            if progress != type(int):
                progress = int(progress)

            gc.stats(gc.colored(f"Extruder: {extruder_temps}°C | Bed: {heater_bed_temps}°C", "cyan"))
            gc.stats(gc.colored(f"E-Power: {extruder_power} | B-Power: {heater_bed_power}", "cyan"))
            gc.stats(gc.colored(f"Progress: {progress}% | Speed: {current_speed}", "cyan"))

            #output stats as json to {output_dir}/stats.json

            stats = {
                "Extruder": extruder_temps,
                "Bed": heater_bed_temps,
                "Extruder Power": extruder_power,
                "Bed Power": heater_bed_power,
                "Progress": progress,
                "Speed": current_speed
            }

            with open(os.path.join(output_dir, "stats.json"), "w") as f:
                gc.stats("Writing stats to stats.json")
                f.write(gc.json.dumps(stats))
                f.close()

            # convert the speed to cm/s if value is > 4 digits
            if current_speed > 9999:
                current_speed = f"{current_speed / 1000:.1f} m/s"
            else:
                current_speed = f"{current_speed} mm/s"

            text = [
                f"Ext: {extruder_temps}°",
                f"Bed: {heater_bed_temps}°",
                f"{int(progress)}%",
                f"{current_speed}"
            ]

            # Positions for the text elements
            positions = [(150, 10), (150, 40), (10, 360), (300, 360)]
            done_position = (122, 360)

            for i, line in enumerate(text):
                draw.text(positions[i], line, fill="#ffffff", font=font)

            # detect if the print job is completed

            if progress < 100:
                color = "#ffffff"
            else:
                draw.text(done_position, "Completed", fill="#ffffff", font=font)
                color = "#00ff00"

            # add progress bar 20 steps between progress and speed
            draw.rectangle([10, 380, 310, 390], fill="#000000")
            draw.rectangle([10, 380, 200, 390], outline="#ffffff")
            draw.rectangle([10, 380, 10 + (progress * 2), 390], fill=color)


            output_image_path = os.path.join(output_dir, f"out.png")

            cl.save(output_image_path)

            gc.stats(gc.colored("Done", "green"))

            return output_image_path
    else:
        print("No image to display.")
    
async def await_job(printer_ip, port):
        
    state, status = await check_printing(printer_ip, port)
    
    if state == True:
        return True, status
    else:
        gc.stats("Awaiting job...")

        current_time = gc.stats("")

        for i in range(5):
            dots = "." * i
            print(current_time, end='', flush=True)
            print(f"Update in {5 - i} seconds{dots}", end='\r', flush=True)
            await asyncio.sleep(1)

        gc.tidy()
        logo()
        return False, status

def measure_execution_time(func):
    def timed_execution(*args, **kwargs):
        start_timestamp = time.time()
        result = func(*args, **kwargs)
        end_timestamp = time.time()
        execution_duration = end_timestamp - start_timestamp
        gc.stats(f"Function {func.__name__} took {execution_duration:.2f} seconds to execute")
        return result
    return timed_execution

def logo():
        print(f"""
                  __      __   __   __     ___ 
                 / _` __ /  ` /  \ |  \ | |__  
                 \__>    \__, \__/ |__/ | |___  live
      
        """)

@measure_execution_time
def main():
    # Main logic and execution
    if not os.path.exists("config.ini"):
        gc.create_config()
    gc.load_config()

    config = gc.load_config()

    try:
        printer_ip = gc.get_config_value("PRINTER", "printer_ip")
        port = int(gc.get_config_value("PRINTER", "port"))

        image_size = eval(gc.get_config_value("IMAGE", "image_size"))
        bg_color = gc.get_config_value("IMAGE", "bg_color")
        layer_color = gc.get_config_value("IMAGE", "layer_color")
        font_path = gc.get_config_value("FONT", "font_path")
        output_dir = gc.get_config_value("OUTPUT", "output_dir")

        debug_bool = gc.get_config_value("DEBUG", "debug")
    except Exception as e:
        gc.stats(f"Error in reading the config, try deleting: {e}")
        return

    if debug_bool == "True":
        gc.stats(gc.colored("DEBUG MODE ENABLED", "red"))
        debug = True
    else:
        debug = False
        gc.stats(gc.colored("Config read ok", "green"))

    # Check if the printer is printing
    if debug == False:
        while True:
            printing, _ = asyncio.run(await_job(printer_ip, port))
            if printing == True:
                # Clear previous
                try:
                    gc.remove_files(output_dir)
                except Exception as e:
                    pass

                for i in range(5):
                    dots = "." * i
                    current_time = gc.stats("")
                    print(current_time, end='', flush=True)
                    print(f"Printing job found. Starting the loop in {5 - i} seconds{dots}", end='\r', flush=True)
                    time.sleep(1)

                # Start with the main loop for processing the layers
                while True:
                    # Check if the layers are correct (detect calibration process)
                    current_layer, layer_count = gc.get_moonraker_layer(printer_ip, port)
                    if current_layer > layer_count:
                        gc.stats(gc.colored(f"Calibration detected ({current_layer} < {layer_count}). Waiting for 10s", "yellow"))
                        time.sleep(10)
                    else:
                        # Check if the print job is completed if so, break the 1st loop
                        progress = gc.get_moonraker_progress(printer_ip, port)
                        if progress == 100:
                            gc.stats("Print job completed. Checking for next one")
                            time.sleep(3)
                            break

                        logo()

                        # Process the current layer and stats
                        path = asyncio.run(get_layer(printer_ip, port, image_size, bg_color, layer_color, debug))
                        if path is None:
                            print("Error: get_layer returned None")
                        else:
                            asyncio.run(get_current_stats(printer_ip, port, path, debug))
                        
                        # Wait for 3 seconds before updating
                        for i in range(3):
                            dots = "." * i
                            current_time = gc.stats("")
                            print(current_time, end='', flush=True)
                            print(f"Update in {3 - i} seconds{dots}", end='\r', flush=True)
                            time.sleep(1)
                        gc.tidy()

    else:
        gc.stats("Passing the job check in debug mode")
        path = asyncio.run(get_layer(printer_ip, port, image_size, bg_color, layer_color, debug))
        if path is None:
            print("Error: get_layer returned None")
        else:
            asyncio.run(get_current_stats(printer_ip, port, path, debug))
        



async def check_printing(printer_ip, port):
    try:
        status, message = gc.get_current_state(printer_ip, port)
    except Exception as e:
        gc.stats(gc.colored(f"Printer might be unreachable: {e}", "red"))
        gc.stats("Returing in 5 seconds. Check errors.")
        gc.stats(" ")
        time.sleep(5)

        status = False
        message = str(e)

    if status == True:
        return True, message
    else:
        return False, message

# Run the main function
if __name__ == "__main__":
    main()
