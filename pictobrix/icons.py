"""
icons.py
--------
Imagen real de cada pieza ("pixel") del sistema: los 40 iconos originales de
PicToBrix que viven en la carpeta iconos/ del repositorio -- sombrilla,
calabaza, pato, etc.

Cada archivo se llama `NN-nombre.jpeg`, donde NN es el indice del color en
pictobrix/palette.py (00-calabaza.jpeg, 01-paraguas.jpeg, ...). Ese numero es
lo unico que importa para la busqueda: se puede cambiar la parte descriptiva
del nombre o la extension sin romper nada.

Si la carpeta de iconos no esta disponible, se cae al simbolo vectorial que
dibuja el PDF (pictobrix/icon_render.py), asi que el panel de inventario
siempre muestra algo.
"""

from __future__ import annotations
import functools
import glob
import io
import os

from PIL import Image

from . import icon_render
from . import palette as pal

_ICON_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "iconos"
)


def _check_index(color_index: int) -> None:
    if not (0 <= color_index < len(pal.PALETTE)):
        raise ValueError(f"Indice de color invalido: {color_index}")


@functools.lru_cache(maxsize=64)
def icon_path(color_index: int) -> str | None:
    """Ruta del archivo `NN-*` del color, o None si no esta en disco."""
    _check_index(color_index)
    matches = sorted(glob.glob(os.path.join(_ICON_DIR, f"{color_index:02d}-*")))
    return matches[0] if matches else None


@functools.lru_cache(maxsize=64)
def icon_version(color_index: int) -> str:
    """
    Token corto que cambia cuando se reemplaza el archivo del icono. Va como
    `?v=` en la URL de la imagen: al cambiar la URL, el navegador vuelve a
    pedirla en vez de servir la version vieja que tenga en cache.
    """
    path = icon_path(color_index)
    if path is None:
        return "sym"
    st = os.stat(path)
    return f"{int(st.st_mtime):x}-{st.st_size:x}"


@functools.lru_cache(maxsize=128)
def icon_png(color_index: int, size: int = 96) -> bytes:
    """PNG (bytes) cuadrado con la foto de la pieza, listo para la web."""
    path = icon_path(color_index)
    if path is None:
        return icon_render.render_icon(color_index, size=size)

    with Image.open(path) as im:
        im = im.convert("RGB")
        side = min(im.size)
        left = (im.width - side) // 2
        top = (im.height - side) // 2
        im = im.crop((left, top, left + side, top + side))
        im = im.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
    return buf.getvalue()
