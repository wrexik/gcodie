import gcodie as gc
import time

printer_ip = "10.0.0.154"
port = 7125


# Fetch updated print status and progress
response, layer_info, state, print_duration, filament_used, z_pos, filename = gc.get_moonraker_print_status(printer_ip, port)
progress = gc.get_moonraker_progress(printer_ip, port)

# Clear previous status messages
#gc.tidy()

# Display the updated information
gc.stats(f"{filename} is {progress:.2f}% complete.")
gc.stats(f"State: {state}")
gc.stats(f"Print duration: {print_duration}")
gc.stats(f"Filament used: {filament_used}")
gc.stats(f"Z position: {z_pos}")
gc.stats(f"Layer info: {layer_info}")

filepath = 'Surviva_PLA_28m.gcode'
z_pos = 14


# Wait for 3 seconds before fetching the data again
time.sleep(3)
