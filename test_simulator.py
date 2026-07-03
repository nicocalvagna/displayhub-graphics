from displayhub_graphics.drivers.simulator import Simulator

display = Simulator("preview.png")

with display.canvas() as d:
    d.rectangle(0, 0, 127, 63)
    d.header("DISPLAYHUB")
    d.label_value(18, "TEMP", "24.5 C")
    d.label_value(31, "HUM", "55 %")
    d.label_value(44, "MQTT", "OK")
    d.progress_bar(4, 55, 120, 7, 72)

print("Preview generado: preview.png")
