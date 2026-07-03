# DisplayHub ST7920 graphics prototype

Driver gráfico ST7920 128x64 para Raspberry Pi con:

- lgpio
- actualización parcial automática
- canvas Pillow
- iconos con nombres MDI (`mdi:home`, `mdi:thermometer`, etc.)
- dashboard configurable por YAML
- animaciones básicas

## Instalar

```bash
sudo apt install python3-lgpio python3-pil python3-yaml fonts-dejavu-core
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar demo

```bash
cd displayhub_st7920
python3 test_dashboard.py
```

## MDI reales

El sistema usa iconos fallback 12x12 incluidos. Para usar Material Design Icons reales, copiá `MaterialDesignIconsDesktop.ttf` en la carpeta del proyecto o pasá `mdi_font_path` al crear `ST7920()`.
