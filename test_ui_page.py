from displayhub_graphics.drivers.simulator import Simulator
from displayhub_graphics.ui import Page, LabelValueWidget, ProgressWidget, FooterWidget

display = Simulator("page_preview.png")

page = Page("LIVING")
page.add(LabelValueWidget(18, "TEMP", "24.5 C"))
page.add(LabelValueWidget(31, "HUM", "55 %"))
page.add(LabelValueWidget(44, "MQTT", "OK"))
page.add(ProgressWidget(4, 55, 120, 7, 72))

page.render(display)

print("Preview generado: page_preview.png")
