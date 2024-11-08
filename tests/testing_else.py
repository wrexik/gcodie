import gcodie as gc

import time

printer_ip = "10.0.0.155"
port = 7125

def measure_execution_time(func):
    def timed_execution(*args, **kwargs):
        start_timestamp = time.time()
        result = func(*args, **kwargs)
        end_timestamp = time.time()
        execution_duration = end_timestamp - start_timestamp
        gc.stats(f"Function {func.__name__} took {execution_duration:.2f} seconds to execute")
        return result
    return timed_execution

@measure_execution_time
def main():

    try:
        extruder_temp, heater_bed_temp = gc.get_current_temps(printer_ip, port)
        extruder_power, heater_bed_power = gc.get_current_powers(printer_ip, port)
        progress = gc.get_moonraker_progress(printer_ip, port)
    except Exception as e:
        gc.stats(f"Error: {e}")
        return

    #gc.stats(gc.colored(f"""\nExtruder: {extruder_temp}\nBed: {heater_bed_temp}""", "cyan"))
    #gc.stats(gc.colored(f"""\nExtruder power: {extruder_power}\nBed power: {heater_bed_power}""", "cyan"))

    gc.get_animated_current_print(printer_ip, port, image_size=(800, 800), bg_color="#000000", layer_color="#ffffff", output_dir="current_layer")

    #gc.resume_print(printer_ip, port)

    gc.stats(gc.colored("Job done!", "green"))

if __name__ == "__main__":
    main()