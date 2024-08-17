import gcodie as gc

gcode_path = 'test.gcode'  # Replace with your G-code file path
output_dir = 'frames'
#layer = 527  # Layer to visualize (0-indexed)
#count = 528

# Parse G-code to get the print path

x, y, z = gc.parse_gcode_silent(gcode_path)
# x, y, z = gc.parse_gcode(gcode_path)

if x.size == 0:
    print("Error: No valid G-code data to process.")

# Generate images of each layer
gc.last_layer(gcode_path)

#gc.generate_layer_img(layer ,x, y, z, output_dir, bg_color="#f8f8f8", layer_color="#000000")

#gc.generate_multiple_layers(count, x, y, z, output_dir, bg_color="#f8f8f8", layer_color="#000000")




# pridat detekci 0 point layeru na single image
#Last layer is 528
#Error: Layer 528 is out of range. The model has 528 layers.






