import gcodie as gc

printer_ip = "10.0.0.155"
port = 7125

gc.request("get_moonraker_layer", printer_ip, port)