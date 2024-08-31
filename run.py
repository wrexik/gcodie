import gcodie as gc
import random

gcode_path = 'gcode/dolp.gcode'  # Replace with your G-code file path
output_dir = 'frames'

#gc.print_status(args=False)

#layer = 0
#count = 10

#clears the screen

#gc.tidy()


# Parse G-code to get the print path
x, y, z = gc.parse_gcode(gcode_path)
# x, y, z = gc.parse_gcode(gcode_path)

if x.size == 0:
    print("Error: No valid G-code data to process.")

# Generate images of each layer
#gc.last_layer(gcode_path)

first = gc.first_layer(gcode_path)
last = gc.last_layer(gcode_path)

#layer = random.randint(first, last)
#layer = 150

count = 10



#gc.generate_layer_img(layer ,x, y, z, output_dir, bg_color="#f8f8f8", layer_color="#000000", image_size=(400, 400))

#gc.generate_multiple_layers(count, x, y, z, output_dir, bg_color="#000000", layer_color="#ffffff", image_size=(800, 800))

gc.generate_all_layers(x, y, z, output_dir, bg_color="#000000", layer_color="#ff007b", image_size=(800, 800), make_animation=True)

#gc.generate_all_layers(x, y, z, output_dir, bg_color="#000000", layer_color="#ff007b", image_size=(800, 800), make_animation=False)






