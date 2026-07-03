class Page:
    def __init__(self, title):
        self.title = title
        self.widgets = []

    def add(self, widget):
        self.widgets.append(widget)
        return self

    def render(self, display, partial=True):
        with display.canvas(partial=partial, clear=True) as d:
            d.rectangle(0, 0, 127, 63)
            d.header(self.title)

            for widget in self.widgets:
                widget.draw(d)
