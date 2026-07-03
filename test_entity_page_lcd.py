import time

from displayhub_graphics.drivers.st7920 import ST7920
from displayhub_graphics.ui import Page, EntityWidget, ProgressWidget

display = ST7920()

try:
    counter = 0

    while True:
        page = Page("HOME")
        page.add(EntityWidget(18, "mdi:thermometer", "Temp", f"{24.0 + counter / 10:.1f}", "C"))
        page.add(EntityWidget(31, "mdi:water-percent", "Humedad", 55 + counter % 10, "%"))
        page.add(EntityWidget(44, "mdi:wifi", "MQTT", "OK"))
        page.add(ProgressWidget(4, 55, 120, 7, counter % 100))

        page.render(display)

        counter += 1
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

finally:
    display.close()
