import time

from displayhub_graphics.drivers.st7920 import ST7920
from displayhub_graphics.ui import Page, LabelValueWidget, ProgressWidget

display = ST7920()

try:
    counter = 0

    while True:
        page = Page("LIVING")
        page.add(LabelValueWidget(18, "TEMP", f"{24.0 + counter / 10:.1f} C"))
        page.add(LabelValueWidget(31, "HUM", f"{55 + counter % 10} %"))
        page.add(LabelValueWidget(44, "MQTT", "OK"))
        page.add(ProgressWidget(4, 55, 120, 7, counter % 100))

        page.render(display)

        counter += 1
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

finally:
    display.close()
