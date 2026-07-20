"""
pictobrix
=========
Sistema para convertir una foto en un mosaico de "brix" y generar el PDF
de instructivo (formato PicToBrix).

Uso rapido:
    from pictobrix import generate
    generate("foto.jpg", "instructivo.pdf", cols=3, rows=3, max_colors=26)
"""

from __future__ import annotations
from PIL import Image

from .processor import build_mosaic, render_preview, Mosaic, PLATE, PLATE_CM, PIECES_PER_PLATE
from .pdf_builder import build_pdf

__all__ = [
    "generate", "build_mosaic", "build_pdf", "render_preview",
    "Mosaic", "PLATE", "PLATE_CM", "PIECES_PER_PLATE",
]


def generate(
    image_path: str,
    out_pdf: str,
    cols: int = 3,
    rows: int = 3,
    max_colors: int | None = 26,
    crop_mode: str = "cover",
    name: str = "",
    pre_cropped: bool = False,
) -> Mosaic:
    """
    Convierte image_path en mosaico (cols x rows placas) y escribe out_pdf.
    Devuelve el objeto Mosaic (por si quieres datos o vista previa).
    """
    img = Image.open(image_path)
    mosaic = build_mosaic(
        img, cols=cols, rows=rows, max_colors=max_colors,
        crop_mode=crop_mode, pre_cropped=pre_cropped,
    )
    build_pdf(mosaic, out_pdf, name=name)
    return mosaic
