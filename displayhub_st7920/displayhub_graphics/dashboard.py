import time
from pathlib import Path

import yaml

from displayhub_graphics.animations.spinner import Spinner


class DashboardRenderer:
    def __init__(self, display, config):
        self.display = display
        self.config = config
        self.spinner = Spinner()
        self.page_index = 0
        self.last_switch = time.monotonic()

    @classmethod
    def from_yaml(cls, display, path):
        with open(path, "r", encoding="utf-8") as f:
            return cls(display, yaml.safe_load(f))

    def current_page(self):
        pages = self.config.get("pages", [])
        if not pages:
            return {"title": "DISPLAYHUB", "cards": []}
        now = time.monotonic()
        interval = float(self.config.get("page_interval", 8))
        if now - self.last_switch >= interval:
            self.page_index = (self.page_index + 1) % len(pages)
            self.last_switch = now
        return pages[self.page_index]

    def render(self, data=None):
        data = data or {}
        page = self.current_page()
        with self.display.canvas(partial=True, clear=True) as d:
            d.rectangle(0, 0, 127, 63)
            d.header(page.get("title", "DISPLAYHUB"), icon=page.get("icon"))
            cards = page.get("cards", [])
            for card in cards:
                self._draw_card(d, card, data)

    def _value(self, item, data):
        if "value" in item:
            return item["value"]
        entity = item.get("entity")
        if not entity:
            return ""
        state = data.get(entity, item.get("default", "--"))
        unit = item.get("unit", "")
        return f"{state}{unit}"

    def _draw_card(self, d, card, data):
        typ = card.get("type", "entities")
        if typ == "entities":
            y = int(card.get("y", 17))
            step = int(card.get("step", 13))
            for item in card.get("items", []):
                d.row(y, item.get("icon", "mdi:alert-circle"), item.get("name", ""), self._value(item, data))
                y += step
        elif typ == "progress":
            value = float(card.get("value", data.get(card.get("entity", ""), 0)))
            d.progress_bar(int(card.get("x", 4)), int(card.get("y", 54)), int(card.get("width", 120)), int(card.get("height", 7)), value, float(card.get("max", 100)))
            if card.get("label"):
                d.right_text(124, int(card.get("label_y", 43)), f"{value:.0f}%")
        elif typ == "spinner":
            self.spinner.draw(d, int(card.get("x", 106)), int(card.get("y", 48)))
