#!/usr/bin/env python3
import random
import time

from displayhub_graphics import ST7920, DashboardRenderer

lcd = ST7920()
renderer = DashboardRenderer.from_yaml(lcd, "dashboard_example.yaml")

try:
    while True:
        data = {
            "sensor.living_temperature": f"{24 + random.random():.1f}",
            "sensor.living_humidity": random.randint(50, 65),
            "sensor.signal": random.randint(40, 100),
            "sensor.cpu": random.randint(5, 80),
            "sensor.ram": random.randint(30, 70),
        }
        renderer.render(data)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    lcd.close()
