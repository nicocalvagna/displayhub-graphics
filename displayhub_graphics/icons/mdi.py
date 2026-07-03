from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Fallback 12x12 icons. Names match Home Assistant MDI names when possible.
FALLBACK = {
    "mdi:home": [
        "000001100000","000011110000","000111111000","001111111100",
        "011111111110","000111111000","000111111000","000110011000",
        "000110011000","000111111000","000111111000","000000000000"],
    "mdi:thermometer": [
        "000011000000","000100100000","000100100000","000100100000",
        "000100100000","000100100000","001100110000","011111111000",
        "011111111000","001111110000","000111100000","000000000000"],
    "mdi:water-percent": [
        "000001000000","000011100000","000111110000","001111111000",
        "011111111100","011011011100","011111111100","001101101000",
        "000111110000","000011100000","000001000000","000000000000"],
    "mdi:water": [
        "000001000000","000011100000","000111110000","001111111000",
        "011111111100","011111111100","011111111100","001111111000",
        "000111110000","000011100000","000001000000","000000000000"],
    "mdi:wifi": [
        "000000000000","001111111100","010000000010","000111111000",
        "001000000100","000011110000","000100001000","000001100000",
        "000010010000","000001100000","000000000000","000000000000"],
    "mdi:wifi-off": [
        "100000000000","010111111100","001000000010","000111111000",
        "001010000100","000011110000","000101001000","000001100000",
        "000010010000","000001110000","000000001000","000000000100"],
    "mdi:mqtt": [
        "000111111000","001000000100","010011110010","100100001001",
        "101001100101","101010010101","101001100101","100100001001",
        "010011110010","001000000100","000111111000","000000000000"],
    "mdi:check-circle": [
        "000111100000","001000010000","010000001000","100000000100",
        "100000100100","100001100100","010011001000","001110010000",
        "000100100000","000001000000","000000000000","000000000000"],
    "mdi:alert-circle": [
        "000111100000","001111110000","011111111000","111001111100",
        "111001111100","111001111100","111111111100","111001111100",
        "011111111000","001111110000","000111100000","000000000000"],
    "mdi:flash": [
        "000001100000","000011000000","000110000000","001111100000",
        "011111000000","000110000000","001100000000","011000000000",
        "110000000000","100000000000","000000000000","000000000000"],
    "mdi:clock-outline": [
        "000111100000","001000010000","010000001000","100001000100",
        "100001000100","100001000100","100001100100","100000010100",
        "010000001000","001000010000","000111100000","000000000000"],
    "mdi:server": [
        "001111111100","001000000100","001010010100","001000000100",
        "001111111100","000000000000","001111111100","001000000100",
        "001010010100","001000000100","001111111100","000000000000"],
}

ALIASES = {
    "home": "mdi:home",
    "temp": "mdi:thermometer",
    "temperature": "mdi:thermometer",
    "humidity": "mdi:water-percent",
    "water": "mdi:water",
    "wifi": "mdi:wifi",
    "mqtt": "mdi:mqtt",
    "ok": "mdi:check-circle",
    "alert": "mdi:alert-circle",
}

# Common MDI codepoints. Works only if MaterialDesignIconsDesktop.ttf is installed/provided.
CODEPOINTS = {
    "mdi:home": "\U000F02DC",
    "mdi:thermometer": "\U000F050F",
    "mdi:water-percent": "\U000F058E",
    "mdi:water": "\U000F058C",
    "mdi:wifi": "\U000F05A9",
    "mdi:wifi-off": "\U000F05AA",
    "mdi:mqtt": "\U000F086B",
    "mdi:check-circle": "\U000F05E0",
    "mdi:alert-circle": "\U000F0028",
    "mdi:flash": "\U000F0241",
    "mdi:clock-outline": "\U000F0150",
    "mdi:server": "\U000F048B",
}


class MDIIconManager:
    def __init__(self, mdi_font_path=None, default_size=12):
        self.default_size = default_size
        self.mdi_font_path = mdi_font_path or self._find_mdi_font()
        self._font_available = bool(self.mdi_font_path and Path(self.mdi_font_path).exists())

    def _find_mdi_font(self):
        candidates = [
            "./MaterialDesignIconsDesktop.ttf",
            "./materialdesignicons-webfont.ttf",
            "/usr/local/share/fonts/MaterialDesignIconsDesktop.ttf",
            "/usr/share/fonts/truetype/materialdesignicons/MaterialDesignIconsDesktop.ttf",
        ]
        for path in candidates:
            if Path(path).exists():
                return path
        return None

    def normalize(self, name):
        if not name:
            return "mdi:alert-circle"
        name = str(name).strip()
        if not name.startswith("mdi:"):
            name = ALIASES.get(name, f"mdi:{name}")
        return name

    @lru_cache(maxsize=512)
    def get(self, name, size=None):
        name = self.normalize(name)
        size = int(size or self.default_size)
        if self._font_available and name in CODEPOINTS:
            return self._from_font(name, size)
        return self._from_bitmap(name, size)

    def _from_font(self, name, size):
        # Render bigger and fit into requested square for better antialias thresholding.
        font = ImageFont.truetype(self.mdi_font_path, max(12, size + 2))
        tmp = Image.new("L", (size * 3, size * 3), 0)
        draw = ImageDraw.Draw(tmp)
        glyph = CODEPOINTS[name]
        bbox = draw.textbbox((0, 0), glyph, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((tmp.width - w) // 2 - bbox[0], (tmp.height - h) // 2 - bbox[1]), glyph, font=font, fill=255)
        bbox = tmp.getbbox()
        if bbox:
            tmp = tmp.crop(bbox)
        tmp.thumbnail((size, size), Image.Resampling.LANCZOS)
        img = Image.new("1", (size, size), 1)
        mono = tmp.point(lambda p: 0 if p > 80 else 1, mode="1")
        img.paste(mono, ((size - mono.width) // 2, (size - mono.height) // 2))
        return img

    def _from_bitmap(self, name, size):
        pattern = FALLBACK.get(name) or FALLBACK["mdi:alert-circle"]
        base_h = len(pattern)
        base_w = len(pattern[0])
        img = Image.new("1", (base_w, base_h), 1)
        px = img.load()
        for y, line in enumerate(pattern):
            for x, bit in enumerate(line):
                if bit == "1":
                    px[x, y] = 0
        if size != base_w or size != base_h:
            img = img.resize((size, size), Image.Resampling.NEAREST)
        return img
