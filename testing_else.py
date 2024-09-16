import gcodie as gc

printer_ip = "10.0.0.155"
port = 7125

extruder_temp, heater_bed_temp = gc.get_current_temps(printer_ip, port)
extruder_power, heater_bed_power = gc.get_current_powers(printer_ip, port)

#gc.stats(gc.colored(f"""\nExtruder: {extruder_temp}\nBed: {heater_bed_temp}""", "cyan"))

gc.stats(gc.colored("Job done!", "green"))