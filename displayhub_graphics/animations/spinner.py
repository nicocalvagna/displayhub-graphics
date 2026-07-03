class Spinner:
    def __init__(self):
        self.frame = 0

    def draw(self, display, x, y, size=10):
        patterns = [
            [(0,-4),(3,-3),(4,0),(3,3),(0,4),(-3,3),(-4,0),(-3,-3)],
            [(3,-3),(4,0),(3,3),(0,4),(-3,3),(-4,0),(-3,-3),(0,-4)],
            [(4,0),(3,3),(0,4),(-3,3),(-4,0),(-3,-3),(0,-4),(3,-3)],
            [(3,3),(0,4),(-3,3),(-4,0),(-3,-3),(0,-4),(3,-3),(4,0)],
        ]
        points = patterns[self.frame % len(patterns)]
        for i, (dx, dy) in enumerate(points):
            if i < 3:
                display.draw.point((x + dx, y + dy), fill=0)
            else:
                display.draw.rectangle((x + dx, y + dy, x + dx + 1, y + dy + 1), fill=0)
        self.frame += 1
