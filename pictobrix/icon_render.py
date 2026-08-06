"""
icon_render.py
---------------
Renderiza los simbolos de pictobrix/symbols.py como imagenes PNG para
mostrarlos en el panel de inventario. Reutiliza exactamente las mismas
funciones de dibujo que usa el PDF (pictobrix/pdf_builder.py), asi que el
icono que se ve en la web es el mismo diseno que aparece en el instructivo
-- solo que rasterizado con Pillow en vez de reportlab.
"""

from __future__ import annotations
import functools
import io

from PIL import Image, ImageDraw

from . import palette as pal
from . import symbols as sym


def _flatten_cubic(p0, p1, p2, p3, steps: int = 14) -> list[tuple[float, float]]:
    pts = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3 * p0[0] + 3*mt**2*t * p1[0] + 3*mt*t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3*mt**2*t * p1[1] + 3*mt*t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


class _Path:
    """Imita el objeto Path de reportlab.pdfgen.canvas.Canvas.beginPath()."""

    def __init__(self):
        self._pts: list[tuple[float, float]] = []
        self._cur = (0.0, 0.0)
        self.closed = False

    def moveTo(self, x, y):
        self._pts = [(x, y)]
        self._cur = (x, y)

    def lineTo(self, x, y):
        self._pts.append((x, y))
        self._cur = (x, y)

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self._pts.extend(_flatten_cubic(self._cur, (x1, y1), (x2, y2), (x3, y3)))
        self._cur = (x3, y3)

    def close(self):
        self.closed = True


class _PilCanvas:
    """
    Adaptador minimo: implementa el subconjunto de la API de
    reportlab.pdfgen.canvas.Canvas que usan las funciones de symbols.py
    (ellipse, circle, rect, roundRect, line, beginPath/drawPath,
    setLineWidth, setFillColor, setStrokeColor, saveState/restoreState),
    pero dibujando sobre un lienzo de Pillow en lugar de un PDF.
    """

    def __init__(self, draw: ImageDraw.ImageDraw, height: int):
        self._draw = draw
        self._h = height
        self._fill = (0, 0, 0)
        self._stroke = (0, 0, 0)
        self._lw = 1.0

    def _y(self, y):
        return self._h - y

    def saveState(self):
        pass

    def restoreState(self):
        pass

    def setFillColor(self, rgb):
        self._fill = rgb

    def setStrokeColor(self, rgb):
        self._stroke = rgb

    def setLineWidth(self, w):
        self._lw = w

    def _fill_outline_width(self, stroke, fill):
        return (
            self._fill if fill else None,
            self._stroke if stroke else None,
            max(1, round(self._lw)),
        )

    def ellipse(self, x1, y1, x2, y2, stroke=0, fill=0):
        bbox = [x1, self._y(y2), x2, self._y(y1)]
        f, o, w = self._fill_outline_width(stroke, fill)
        self._draw.ellipse(bbox, fill=f, outline=o, width=w)

    def circle(self, cx, cy, r, stroke=0, fill=0):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, stroke=stroke, fill=fill)

    def rect(self, x, y, w, h, stroke=0, fill=0):
        bbox = [x, self._y(y + h), x + w, self._y(y)]
        f, o, lw = self._fill_outline_width(stroke, fill)
        self._draw.rectangle(bbox, fill=f, outline=o, width=lw)

    def roundRect(self, x, y, w, h, radius, stroke=0, fill=0):
        bbox = [x, self._y(y + h), x + w, self._y(y)]
        f, o, lw = self._fill_outline_width(stroke, fill)
        self._draw.rounded_rectangle(bbox, radius=radius, fill=f, outline=o, width=lw)

    def line(self, x1, y1, x2, y2):
        self._draw.line([(x1, self._y(y1)), (x2, self._y(y2))],
                        fill=self._stroke, width=max(1, round(self._lw)))

    def beginPath(self):
        return _Path()

    def drawPath(self, path: _Path, stroke=0, fill=0):
        pts = [(x, self._y(y)) for x, y in path._pts]
        if len(pts) < 2:
            return
        if fill:
            self._draw.polygon(pts, fill=self._fill)
        if stroke:
            line_pts = pts + [pts[0]] if path.closed else pts
            self._draw.line(line_pts, fill=self._stroke,
                            width=max(1, round(self._lw)), joint="curve")


@functools.lru_cache(maxsize=64)
def render_icon(color_index: int, size: int = 64, supersample: int = 4) -> bytes:
    """PNG (bytes) del cuadro de color + simbolo, tal como aparece en el PDF."""
    names = pal.palette_names()
    if not (0 <= color_index < len(names)):
        raise ValueError(f"Indice de color invalido: {color_index}")

    rgb = tuple(int(v) for v in pal.palette_rgb()[color_index])
    lum = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255.0
    ink = (255, 255, 255) if lum < 0.5 else (0, 0, 0)

    big = size * supersample
    img = Image.new("RGB", (big, big), rgb)
    draw = ImageDraw.Draw(img)
    canvas = _PilCanvas(draw, big)

    drawer = sym.assign_symbols(len(names))[color_index]
    cx = cy = big / 2
    r = big * 0.34
    drawer(canvas, cx, cy, r, ink)

    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
