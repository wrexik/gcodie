import gcodie as gc
import random

gcode_path = 'dragon.gcode'  # Replace with your G-code file path
output_dir = 'frames'

#gc.echo(args=False)

#layer = 0
#count = 10

# Parse G-code to get the print path

x, y, z = gc.parse_gcode_silent(gcode_path)
# x, y, z = gc.parse_gcode(gcode_path)

if x.size == 0:
    print("Error: No valid G-code data to process.")

# Generate images of each layer
#gc.last_layer(gcode_path)

first = gc.first_layer(gcode_path)
last = gc.last_layer(gcode_path)

#layer = random.randint(first, last)
layer = 150

#calculates all layers
for count in range(first, last):
    count = count

#gc.generate_layer_img(layer ,x, y, z, output_dir, bg_color="#f8f8f8", layer_color="#000000", image_size=(400, 400))

gc.generate_multiple_layers(count, x, y, z, output_dir, bg_color="#000000", layer_color="#ffffff", image_size=(800, 800))

# pridat detekci 0 point layeru na single image
#Last layer is 528
#Error: Layer 528 is out of range. The model has 528 layers.






