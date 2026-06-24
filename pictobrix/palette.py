"""
palette.py
----------
Paleta de 40 colores extraidos directamente de los iconos PicToBrix.
Cada color es el fondo exacto (pixel corner) de su icono correspondiente.
"""

from __future__ import annotations
import numpy as np

# (nombre, (R, G, B))  -- valores 0..255, extraidos de las imagenes originales
PALETTE: list[tuple[str, tuple[int, int, int]]] = [
    ("Calabaza",         (255, 100,   0)),     # 0
    ("Paraguas",         ( 90, 166, 244)),     # 1
    ("Pina",             (255, 254, 146)),     # 2
    ("Pato",             (240, 217, 149)),     # 3
    ("Foco",             (203, 171, 150)),     # 4
    ("Sobre",            (255, 218, 199)),     # 5
    ("Fresa",            (170,   0,   0)),     # 6
    ("Nota musical",     ( 88,  62, 150)),     # 7
    ("Regalo",           (180, 116,  91)),     # 8
    ("Camara",           ( 31,  54, 106)),     # 9
    ("Diamante",         ( 69, 208, 229)),     # 10
    ("Uvas",             (162, 133, 189)),     # 11
    ("Cerezas",          (228,  79,  99)),     # 12
    ("Oso",              ( 89,  28,   7)),     # 13
    ("Trofeo",           (175, 150,  84)),     # 14
    ("Rayo",             (193, 144, 137)),     # 15
    ("Ventilador",       ( 92,  73,  69)),     # 16
    ("Bicicleta",        ( 18,  16,  19)),     # 17
    ("Lampara",          (121, 114,  85)),     # 18
    ("Camion",           (  1, 109, 181)),     # 19
    ("Platano",          (255, 223,   0)),     # 20
    ("Globo",            (186, 255, 234)),     # 21
    ("Helicoptero",      (249, 190, 150)),     # 22
    ("Camello",          (140,  72,  53)),     # 23
    ("Carrito",          (251, 172, 131)),     # 24
    ("Alcancia",         (255, 198, 230)),     # 25
    ("Gota",             (193, 113,  50)),     # 26
    ("Raton",            (229, 155, 128)),     # 27
    ("Sol",              (255, 167,  67)),     # 28
    ("Helado",           (134,  15,  71)),     # 29
    ("Dona",             (199,  84, 161)),     # 30
    ("Mano",             (100, 129,  99)),     # 31
    ("Hueso",            (254, 254, 254)),     # 32
    ("Reloj",            (  0, 176,  75)),     # 33
    ("Campana",          (240, 134, 110)),     # 34
    ("Ojo",              (173, 255, 173)),     # 35
    ("Pez",              ( 94,  94,  94)),     # 36
    ("Balanza",          (237, 185, 161)),     # 37
    ("Avion",            (156, 156, 156)),     # 38
    ("Aguacate",         (  0,  79,  50)),     # 39
]


# ----------------------------------------------------------------------------
# Conversion sRGB -> CIE Lab (vectorizada con numpy, blanco de referencia D65)
# ----------------------------------------------------------------------------
def _srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    rgb = rgb / 255.0
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """rgb: array (..., 3) en 0..255  ->  Lab (..., 3)."""
    rgb = np.asarray(rgb, dtype=np.float64)
    lin = _srgb_to_linear(rgb)
    m = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = lin @ m.T
    ref = np.array([0.95047, 1.00000, 1.08883])
    xyz = xyz / ref
    eps = 216 / 24389
    kappa = 24389 / 27
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


_PALETTE_RGB = np.array([c for _, c in PALETTE], dtype=np.float64)
_PALETTE_LAB = rgb_to_lab(_PALETTE_RGB)


def palette_rgb() -> np.ndarray:
    return _PALETTE_RGB.astype(np.uint8)


def palette_names() -> list[str]:
    return [n for n, _ in PALETTE]


def nearest_palette_indices(pixels_rgb: np.ndarray) -> np.ndarray:
    lab = rgb_to_lab(pixels_rgb.reshape(-1, 3))
    d = np.linalg.norm(lab[:, None, :] - _PALETTE_LAB[None, :, :], axis=2)
    return np.argmin(d, axis=1)


def palette_lab() -> np.ndarray:
    return _PALETTE_LAB
