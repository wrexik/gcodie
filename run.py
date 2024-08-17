import gcodie as gc

gcode_path = 'test.gcode'  # Replace with your G-code file path
output_dir = 'frames'
layer = 500  # Layer to visualize (0-indexed)

# Parse G-code to get the print path

x, y, z = gc.parse_gcode_silent(gcode_path)
# x, y, z = gc.parse_gcode(gcode_path)

if x.size == 0:
    print("Error: No valid G-code data to process.")

# Generate images of each layer
gc.last_layer(gcode_path)

gc.generate_layer_img(layer ,x, y, z, output_dir)

gc.generate_multiple_layers(10, x, y, z, output_dir)




