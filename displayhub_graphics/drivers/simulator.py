from PIL import Image, ImageDraw, ImageFont


class Simulator:
    WIDTH = 128
    HEIGHT = 64

    def __init__(
        self,
        output_path="simulator_output.png",
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        font_size=10,
    ):
        self.output_path = output_path
        self.image = Image.new("1", (self.WIDTH, self.HEIGHT), 1)
        self.draw = ImageDraw.Draw(self.image)

        try:
            self.font = ImageFont.truetype(font_path, font_size)
        except Exception:
            self.font = ImageFont.load_default()

    def close(self):
        pass

    def clear(self):
        self.draw.rectangle((0, 0, self.WIDTH - 1, self.HEIGHT - 1), fill=1)

    def clear_region(self, x1, y1, x2, y2):
        self.draw.rectangle((x1, y1, x2, y2), fill=1)

    def text(self, x, y, value, font=None):
        self.draw.text((x, y), str(value), font=font or self.font, fill=0)

    def text_size(self, value, font=None):
        font = font or self.font
        bbox = self.draw.textbbox((0, 0), str(value), font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def center_text(self, y, value, font=None):
        w, _ = self.text_size(value, font)
        self.text(max(0, (self.WIDTH - w) // 2), y, value, font)

    def right_text(self, x_right, y, value, font=None):
        w, _ = self.text_size(value, font)
        self.text(x_right - w, y, value, font)

    def line(self, x1, y1, x2, y2):
        self.draw.line((x1, y1, x2, y2), fill=0)

    def hline(self, y, x1=0, x2=None):
        self.line(x1, y, self.WIDTH - 1 if x2 is None else x2, y)

    def rectangle(self, x1, y1, x2, y2, fill=None):
        self.draw.rectangle((x1, y1, x2, y2), outline=0, fill=fill)

    def filled_rectangle(self, x1, y1, x2, y2):
        self.draw.rectangle((x1, y1, x2, y2), fill=0)

    def progress_bar(self, x, y, width, height, value, max_value=100):
        value = max(0, min(value, max_value))
        fill_width = int((width - 2) * value / max_value)
        self.rectangle(x, y, x + width - 1, y + height - 1)

        if fill_width > 0:
            self.filled_rectangle(x + 1, y + 1, x + fill_width, y + height - 2)

    def header(self, title):
        self.clear_region(0, 0, self.WIDTH - 1, 13)
        self.center_text(1, title)
        self.hline(13)

    def footer(self, text):
        self.clear_region(0, 53, self.WIDTH - 1, 63)
        self.hline(52)
        self.center_text(54, text)

    def label_value(self, y, label, value, x_label=4, x_value=124):
        self.text(x_label, y, label)
        self.right_text(x_value, y, value)

    def bitmap(self, x, y, image):
        img = image.convert("1")
        self.image.paste(img, (x, y))

    def show(self, partial=True):
        self.image.save(self.output_path)
        return self.HEIGHT, self.WIDTH * self.HEIGHT // 8

    def canvas(self, partial=True, clear=True):
        simulator = self

        class CanvasContext:
            def __enter__(self):
                if clear:
                    simulator.clear()
                return simulator

            def __exit__(self, exc_type, exc, tb):
                simulator.show(partial=partial)

        return CanvasContext()
