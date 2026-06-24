"""
processor.py
------------
Convierte una imagen en un mosaico de "brix".

Patron base: cada PLACA = 32 x 32 pixeles = 25.6 cm x 25.6 cm = 1024 piezas.
El usuario elige el arreglo de placas (columnas x filas), por ejemplo:
    1x1, 1x2, 2x1, 2x2, 3x2, 2x3, 3x3, ...
La resolucion final del mosaico es (cols*32) de ancho x (rows*32) de alto,
por lo que el encuadre puede ser vertical u horizontal.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from PIL import Image, ImageOps

from . import palette as pal

PLATE = 32                      # pixeles por lado de una placa
PLATE_CM = 25.6                 # cm por lado de una placa
PIECES_PER_PLATE = PLATE * PLATE  # 1024


@dataclass
class Mosaic:
    grid: np.ndarray                 # (H, W) indices de paleta
    cols: int                        # placas a lo ancho
    rows: int                        # placas a lo alto
    used: list[int]                  # indices de paleta usados, orden desc por conteo
    counts: dict[int, int]           # indice de paleta -> conteo total
    palette_rgb: np.ndarray = field(default_factory=pal.palette_rgb)

    @property
    def width_px(self) -> int:
        return self.cols * PLATE

    @property
    def height_px(self) -> int:
        return self.rows * PLATE

    @property
    def n_boards(self) -> int:
        return self.cols * self.rows

    @property
    def total_pieces(self) -> int:
        return self.width_px * self.height_px

    @property
    def n_colors(self) -> int:
        return len(self.used)

    @property
    def width_cm(self) -> float:
        return self.cols * PLATE_CM

    @property
    def height_cm(self) -> float:
        return self.rows * PLATE_CM

    def symbol_order(self) -> dict[int, int]:
        """indice de paleta -> indice de simbolo (fijo, cada color tiene su icono)."""
        return {pidx: pidx for pidx in self.used}

    def board_grid(self, col: int, row: int) -> np.ndarray:
        """Subcuadricula 32x32 de la placa (col, row), ambos 0-based."""
        r0, c0 = row * PLATE, col * PLATE
        return self.grid[r0:r0 + PLATE, c0:c0 + PLATE]


def _crop_to_aspect(img: Image.Image, cols: int, rows: int, mode: str = "cover") -> Image.Image:
    target_ratio = cols / rows
    if mode == "cover":
        # Recorta centrado para cubrir exactamente la proporcion destino.
        return ImageOps.fit(
            img, (cols * PLATE * 10, rows * PLATE * 10),
            method=Image.LANCZOS, centering=(0.5, 0.5)
        )
    # mode == "contain": agrega bordes (relleno) para no recortar.
    return ImageOps.pad(
        img, (cols * PLATE * 10, rows * PLATE * 10),
        method=Image.LANCZOS, color=(255, 255, 255), centering=(0.5, 0.5)
    )


def build_mosaic(
    img: Image.Image,
    cols: int,
    rows: int,
    max_colors: int | None = 26,
    crop_mode: str = "cover",
    pre_cropped: bool = False,
) -> Mosaic:
    """
    img        : imagen PIL de origen (RGB).
    cols, rows : placas a lo ancho y alto.
    max_colors : limite de colores en la leyenda (None = sin limite).
    crop_mode  : 'cover' (recorta) o 'contain' (rellena). Ignorado si pre_cropped.
    pre_cropped: True si la imagen ya viene encuadrada con la proporcion correcta
                 (p.ej. recortada en la interfaz web). Solo se reescala.
    """
    img = img.convert("RGB")
    if not pre_cropped:
        img = _crop_to_aspect(img, cols, rows, crop_mode)

    W, H = cols * PLATE, rows * PLATE
    small = img.resize((W, H), Image.LANCZOS)
    arr = np.asarray(small, dtype=np.uint8).reshape(-1, 3)

    idx = pal.nearest_palette_indices(arr).reshape(H, W)

    if max_colors is not None:
        idx = _limit_colors(idx, max_colors)

    counts = _count(idx)
    used = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
    return Mosaic(grid=idx, cols=cols, rows=rows, used=used, counts=counts)


def _count(idx: np.ndarray) -> dict[int, int]:
    vals, cts = np.unique(idx, return_counts=True)
    return {int(v): int(c) for v, c in zip(vals, cts)}


def _limit_colors(idx: np.ndarray, max_colors: int) -> np.ndarray:
    """
    Reduce el numero de colores fusionando los menos usados con su vecino mas
    cercano (en Lab) entre los colores que se conservan. Remapea la cuadricula.
    """
    lab = pal.palette_lab()
    while True:
        counts = _count(idx)
        used = list(counts.keys())
        if len(used) <= max_colors:
            return idx
        # color menos usado
        victim = min(used, key=lambda k: counts[k])
        survivors = [u for u in used if u != victim]
        # vecino mas cercano en Lab
        d = np.linalg.norm(lab[survivors] - lab[victim], axis=1)
        target = survivors[int(np.argmin(d))]
        idx = np.where(idx == victim, target, idx)


def render_preview(mosaic: Mosaic, block: int = 12, grid_lines: bool = False) -> Image.Image:
    """Imagen PIL del mosaico final (cada pixel ampliado a 'block' px)."""
    pal_rgb = mosaic.palette_rgb
    rgb = pal_rgb[mosaic.grid]                      # (H, W, 3)
    im = Image.fromarray(rgb.astype(np.uint8), "RGB")
    im = im.resize((mosaic.width_px * block, mosaic.height_px * block), Image.NEAREST)
    return im
