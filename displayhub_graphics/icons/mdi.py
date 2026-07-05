import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class MDIIconManager:
    def __init__(self, size=12):
        base = Path(__file__).parent
        self.size = size
        self.font_path = base / "fonts" / "materialdesignicons-webfont.ttf"
        self.css_path = base / "fonts" / "materialdesignicons.min.css"
        self.cache_dir = base / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        self.font = ImageFont.truetype(str(self.font_path), 16)
        self.codes = self._load_codes()

    def _load_codes(self):
        css = self.css_path.read_text(errors="ignore")
        pattern = r"\.mdi-([a-z0-9\-]+)::before\s*\{content:\"\\([A-Fa-f0-9]+)\"\}"
        return {
            f"mdi:{name}": int(code, 16)
            for name, code in re.findall(pattern, css)
        }

    def get(self, icon_name):
        if icon_name not in self.codes:
            icon_name = "mdi:help-circle-outline"

        cache_file = self.cache_dir / f"{icon_name.replace(':', '_')}_{self.size}.png"

        if cache_file.exists():
            return Image.open(cache_file).convert("1")

        char = chr(self.codes[icon_name])

        img = Image.new("L", (24, 24), 0)
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), char, font=self.font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        x = (24 - w) // 2 - bbox[0]
        y = (24 - h) // 2 - bbox[1]

        draw.text((x, y), char, font=self.font, fill=255)

        img = img.resize((self.size, self.size), Image.LANCZOS)
        img = img.point(lambda p: 0 if p < 80 else 255).convert("1")

        cache_file.parent.mkdir(exist_ok=True)
        img.save(cache_file)

        return img
