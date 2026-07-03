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
