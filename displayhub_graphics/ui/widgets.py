class LabelValueWidget:
    def __init__(self, y, label, value):
        self.y = y
        self.label = label
        self.value = value

    def draw(self, display):
        display.label_value(self.y, self.label, self.value)


class ProgressWidget:
    def __init__(self, x, y, width, height, value, max_value=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.max_value = max_value

    def draw(self, display):
        display.progress_bar(
            self.x,
            self.y,
            self.width,
            self.height,
            self.value,
            self.max_value,
        )


class FooterWidget:
    def __init__(self, text):
        self.text = text

    def draw(self, display):
        display.footer(self.text)

from displayhub_graphics.icons.mdi import MDIIconManager

_mdi = MDIIconManager(size=12)


class EntityWidget:
    def __init__(self, y, icon, name, state, unit=None):
        self.y = y
        self.icon = icon
        self.name = name
        self.state = state
        self.unit = unit

    def draw(self, display):
        value = str(self.state)
        if self.unit:
            value += f" {self.unit}"

        icon_image = _mdi.get(self.icon)

        if hasattr(display, "bitmap"):
            display.bitmap(4, self.y, icon_image)

        display.text(20, self.y, self.name[:10])
        display.right_text(124, self.y, value)
