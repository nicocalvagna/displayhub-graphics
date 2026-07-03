import time
from contextlib import contextmanager
from pathlib import Path
from displayhub_graphics.icons.mdi import MDI_ICONS

import lgpio
from PIL import Image, ImageDraw, ImageFont
from displayhub_graphics.icons.mdi import MDI_ICONS


class ST7920:
    WIDTH = 128
    HEIGHT = 64
    BYTES_PER_ROW = 16

    def __init__(
        self,
        cs=17,
        sid=27,
        sclk=22,
        chip_id=0,
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        font_size=10,
        mdi_font_path=None,
        icon_size=12,
        auto_clear=True,
    ):
        self.cs = cs
        self.sid = sid
        self.sclk = sclk
        self.chip = lgpio.gpiochip_open(chip_id)
        lgpio.gpio_claim_output(self.chip, self.cs, 0)
        lgpio.gpio_claim_output(self.chip, self.sid, 0)
        lgpio.gpio_claim_output(self.chip, self.sclk, 0)

        self.previous = bytearray(self.WIDTH * self.HEIGHT // 8)
        self.image = Image.new("1", (self.WIDTH, self.HEIGHT), 1)
        self.draw = ImageDraw.Draw(self.image)

        self.font = self._load_font(font_path, font_size)
        self.small_font = self._load_font(font_path, 8)
        self.big_font = self._load_font(font_path, 16)
        

        self._init_lcd()
        if auto_clear:
            self.clear()
            self.show(partial=False)

    def _load_font(self, path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    def close(self):
        try:
            lgpio.gpiochip_close(self.chip)
        except Exception:
            pass

    def _write(self, pin, value):
        lgpio.gpio_write(self.chip, pin, value)

    def _pulse(self):
        self._write(self.sclk, 1)
        self._write(self.sclk, 0)

    def _send_byte(self, value):
        for _ in range(8):
            self._write(self.sid, 1 if value & 0x80 else 0)
            self._pulse()
            value <<= 1

    def _send(self, value, is_data=False):
        self._write(self.cs, 1)
        self._send_byte(0xFA if is_data else 0xF8)
        self._send_byte(value & 0xF0)
        self._send_byte((value << 4) & 0xF0)
        self._write(self.cs, 0)

    def _cmd(self, value):
        self._send(value, False)

    def _data(self, value):
        self._send(value, True)

    def _init_lcd(self):
        time.sleep(0.05)
        self._cmd(0x30); time.sleep(0.002)
        self._cmd(0x30); time.sleep(0.002)
        self._cmd(0x0C); time.sleep(0.002)
        self._cmd(0x01); time.sleep(0.02)
        self._cmd(0x06); time.sleep(0.002)
        self._cmd(0x34); time.sleep(0.002)
        self._cmd(0x36); time.sleep(0.002)

    def _set_gdram_address(self, y, x):
        if y < 32:
            self._cmd(0x80 | y)
            self._cmd(0x80 | x)
        else:
            self._cmd(0x80 | (y - 32))
            self._cmd(0x88 | x)

    def _image_to_buffer(self, image):
        raw = image.convert("1").tobytes()
        return bytearray(b ^ 0xFF for b in raw)

    def _update_full(self, buffer):
        for y in range(self.HEIGHT):
            self._set_gdram_address(y, 0)
            row = y * self.BYTES_PER_ROW
            for x_byte in range(self.BYTES_PER_ROW):
                self._data(buffer[row + x_byte])

    def _update_partial(self, buffer):
        changed_rows = 0
        changed_bytes = 0
        for y in range(self.HEIGHT):
            row_start = y * self.BYTES_PER_ROW
            row_end = row_start + self.BYTES_PER_ROW
            if buffer[row_start:row_end] != self.previous[row_start:row_end]:
                changed_rows += 1
                self._set_gdram_address(y, 0)
                for x_byte in range(self.BYTES_PER_ROW):
                    self._data(buffer[row_start + x_byte])
                    changed_bytes += 1
                self.previous[row_start:row_end] = buffer[row_start:row_end]
        return changed_rows, changed_bytes

    # Drawing API
    def clear(self):
        self.draw.rectangle((0, 0, self.WIDTH - 1, self.HEIGHT - 1), fill=1)

    def clear_region(self, x1, y1, x2, y2):
        self.draw.rectangle((x1, y1, x2, y2), fill=1)

    def text(self, x, y, value, font=None):
        self.draw.text((int(x), int(y)), str(value), font=font or self.font, fill=0)

    def text_size(self, value, font=None):
        bbox = self.draw.textbbox((0, 0), str(value), font=font or self.font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def center_text(self, y, value, font=None):
        w, _ = self.text_size(value, font)
        self.text(max(0, (self.WIDTH - w) // 2), y, value, font)

    def right_text(self, x_right, y, value, font=None):
        w, _ = self.text_size(value, font)
        self.text(int(x_right) - w, y, value, font)

    def line(self, x1, y1, x2, y2):
        self.draw.line((x1, y1, x2, y2), fill=0)

    def hline(self, y, x1=0, x2=None):
        self.line(x1, y, self.WIDTH - 1 if x2 is None else x2, y)

    def vline(self, x, y1=0, y2=None):
        self.line(x, y1, x, self.HEIGHT - 1 if y2 is None else y2)

    def rectangle(self, x1, y1, x2, y2, fill=None):
        self.draw.rectangle((x1, y1, x2, y2), outline=0, fill=fill)

    def filled_rectangle(self, x1, y1, x2, y2):
        self.draw.rectangle((x1, y1, x2, y2), fill=0)

    def progress_bar(self, x, y, width, height, value, max_value=100):
        value = max(0, min(float(value), float(max_value)))
        fill_width = int((width - 2) * value / max_value)
        self.rectangle(x, y, x + width - 1, y + height - 1)
        if fill_width > 0:
            self.filled_rectangle(x + 1, y + 1, x + fill_width, y + height - 2)

    def icon(self, x, y, name, size=None):
        img = self.icons.get(name, size=size)
        self.image.paste(img, (int(x), int(y)))

    def row(self, y, icon, label, value=None):
        self.icon(4, y, icon, size=12)
        self.text(19, y - 1, label)
        if value is not None:
            self.right_text(124, y - 1, value)

    def header(self, title, icon=None):
        self.clear_region(0, 0, 127, 13)
        if icon:
            self.icon(4, 1, icon, size=12)
            self.text(20, 1, title)
        else:
            self.center_text(1, title)
        self.hline(13)

    def footer(self, text, icon=None):
        self.clear_region(0, 53, 127, 63)
        self.hline(52)
        if icon:
            self.icon(4, 53, icon, size=10)
            self.text(17, 53, text, font=self.small_font)
        else:
            self.center_text(54, text, font=self.small_font)

    def label_value(self, y, label, value, x_label=4, x_value=124):
        self.text(x_label, y, label)
        self.right_text(x_value, y, value)

    def progress_bar(self, x, y, width, height, value, max_value=100):
        value = max(0, min(value, max_value))
        fill_width = int((width - 2) * value / max_value)

        self.rectangle(x, y, x + width - 1, y + height - 1)

        if fill_width > 0:
            self.filled_rectangle(x + 1, y + 1, x + fill_width, y + height - 2)


    def icon(self, x, y, name, scale=1):
        pattern = MDI_ICONS.get(name)
        if not pattern:
            return

        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "1":
                    px = x + col * scale
                    py = y + row * scale
                    if scale == 1:
                        if 0 <= px < self.WIDTH and 0 <= py < self.HEIGHT:
                            self.image.putpixel((px, py), 0)
                    else:
                        self.draw.rectangle(
                            (px, py, px + scale - 1, py + scale - 1),
                            fill=0,
                        )





    def show(self, partial=True):
        buffer = self._image_to_buffer(self.image)
        if partial:
            return self._update_partial(buffer)
        self._update_full(buffer)
        self.previous[:] = buffer
        return self.HEIGHT, len(buffer)

    @contextmanager
    def canvas(self, partial=True, clear=True):
        if clear:
            self.clear()
        yield self
        self.show(partial=partial)
