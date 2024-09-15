import gcodie as gc
import time

printer_ip = "10.0.0.155"
port = 7125


# Fetch updated print status and progress
response, current_layer, total_layer, state, print_duration, filament_used, z_pos, filename = gc.get_moonraker_stats(printer_ip, port)
progress = gc.get_moonraker_progress(printer_ip, port)

# Clear previous status messages
#gc.tidy()

# Display the updated information
gc.stats(f"{filename} is {progress:.2f}% complete.")
gc.stats(f"State: {state}")
gc.stats(f"Print duration: {print_duration}")
gc.stats(f"Filament used: {filament_used}")
gc.stats(f"Z position: {z_pos}")
gc.stats(f"Layer info: {total_layer}, {current_layer}")

print("")

current_layer, layer_count = gc.get_moonraker_layer(printer_ip, port)

gc.stats(f"Current layer: {current_layer}")
gc.stats(f"Total layers: {layer_count}")

gc.get_current_file(printer_ip, port)


# Wait for 3 seconds before fetching the data again
time.sleep(3)
