import gcodie as gc

import time

printer_ip = "10.0.0.155"
port = 7125



@measure_execution_time
def main():
    #gc.show_current_layer(printer_ip, port, image_size=(800, 800), bg_color="#000000", layer_color="#ffffff", output_dir="current_layer")
    gc.get_animated_current_print(printer_ip, port, image_size=(400, 400), bg_color="#000000", layer_color="#ff0091", output_dir="animation")

    #joe = gc.get_current_file(printer_ip, port)

    #gc.clear_cache()

    gc.stats(gc.colored("Job done!", "green"))

if __name__ == "__main__":
    main()