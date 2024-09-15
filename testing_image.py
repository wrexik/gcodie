import gcodie as gc

printer_ip = "10.0.0.155"
port = 7125

#gc.show_current_layer(printer_ip, port, image_size=(800, 800), bg_color="#000000", layer_color="#ffffff", output_dir="current_layer")
gc.animate_current_print(printer_ip, port, image_size=(400, 400), bg_color="#000000", layer_color="#ff0091", output_dir="animation")

#joe = gc.get_current_file(printer_ip, port)


#gc.clear_cache()
gc.stats(gc.colored("Job done!", "green"))