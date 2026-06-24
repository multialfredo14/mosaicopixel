"""
pdf_builder.py
--------------
Genera el PDF del instructivo con el mismo formato del ejemplo PicToBrix:

  * Pagina 1 (portada): logo, vista del mosaico con las placas numeradas,
    leyenda global (simbolo + conteo total) y cuadro de datos
    (Nombre, Placas, BRIX/piezas, Colores, Paginas).
  * Paginas 2..N: una por placa. Cuadricula 32x32 con numeros de columna
    (1..32) arriba y de fila (1..32) a la izquierda; cada celda lleva el
    color de fondo + su simbolo. Debajo, la leyenda de esa placa.

El mismo simbolo representa siempre al mismo color en TODO el documento.
"""

from __future__ import annotations
import math
import os
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from PIL import Image as PILImage

from . import symbols as sym
from .processor import Mosaic, render_preview, PLATE

PAGE_W, PAGE_H = A4
BOARD_PAGE_W, BOARD_PAGE_H = A3
BOARD_CELL = 0.8 * cm
MARGIN = 32

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo_mosaico_pixel.jpeg")


def _ink_for(rgb) -> colors.Color:
    """Color de trazo con buen contraste sobre el fondo dado."""
    r, g, b = [int(v) for v in rgb]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return colors.Color(1, 1, 1) if lum < 0.5 else colors.Color(0, 0, 0)


def _rl_color(rgb) -> colors.Color:
    r, g, b = [int(v) for v in rgb]
    return colors.Color(r / 255, g / 255, b / 255)


def _spaced_centred(c, cx, baseline, text, font, size, char_space):
    """Texto centrado con espaciado entre caracteres (letter-spacing)."""
    total = c.stringWidth(text, font, size) + char_space * (len(text) - 1)
    to = c.beginText(cx - total / 2, baseline)
    to.setFont(font, size)
    to.setCharSpace(char_space)
    to.textOut(text)
    c.drawText(to)


def _logo(c, top_y, page_w=None) -> float:
    """Dibuja el logo de Mosaico Pixel centrado; devuelve la Y inferior del bloque."""
    if page_w is None:
        page_w = PAGE_W
    logo_h = 100
    with PILImage.open(_LOGO_PATH) as img:
        aspect = img.width / img.height
    logo_w = logo_h * aspect
    x = (page_w - logo_w) / 2
    y = top_y - logo_h
    c.drawImage(ImageReader(_LOGO_PATH), x, y, logo_w, logo_h, mask='auto')
    return y


def _draw_swatch(c, x, y, size, rgb, drawer):
    """Cuadro de color con su simbolo, esquina inferior-izq en (x, y)."""
    c.saveState()
    c.setFillColor(_rl_color(rgb))
    c.setStrokeColor(colors.Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.4)
    c.rect(x, y, size, size, stroke=1, fill=1)
    drawer(c, x + size / 2, y + size / 2, size * 0.34, _ink_for(rgb))
    c.restoreState()


def _legend(c, entries, drawers, sym_order, pal_rgb, x, y_top, width,
            ncols, swatch=18, font=12, row_h=24):
    """
    entries  : lista de (palette_index, count)
    Devuelve la Y inferior usada.
    """
    col_w = width / ncols
    for k, (pidx, count) in enumerate(entries):
        col = k % ncols
        row = k // ncols
        cx = x + col * col_w
        cy = y_top - row * row_h - swatch
        _draw_swatch(c, cx, cy, swatch, pal_rgb[pidx], drawers[sym_order[pidx]])
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", font)
        c.drawString(cx + swatch + 5, cy + (swatch - font) / 2 + 1, f"{count}")
    rows = math.ceil(len(entries) / ncols)
    return y_top - rows * row_h


def _footer(c, left_text, right_text, page_w=None):
    if page_w is None:
        page_w = PAGE_W
    c.saveState()
    c.setFillColor(colors.Color(0.25, 0.25, 0.25))
    c.setFont("Helvetica", 9)
    if left_text:
        c.drawString(MARGIN, MARGIN - 8, left_text)
    c.drawRightString(page_w - MARGIN, MARGIN - 8, right_text)
    c.restoreState()


# ----------------------------------------------------------------------------
# PAGINA 1: portada
# ----------------------------------------------------------------------------
def _overview_page(c, m: Mosaic, drawers, sym_order, total_pages, name):
    y = _logo(c, PAGE_H - MARGIN)

    # Pildora "Instructions sheet"
    label = "Instructions sheet"
    c.setFont("Helvetica", 9)
    w = c.stringWidth(label, "Helvetica", 9) + 18
    c.saveState()
    c.setFillColor(colors.Color(0.85, 0.85, 0.85))
    c.roundRect(PAGE_W / 2 - w / 2, y - 18, w, 15, 4, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.drawCentredString(PAGE_W / 2, y - 14, label)
    c.restoreState()
    y -= 26

    # --- Vista del mosaico con placas numeradas ---
    content_w = PAGE_W - 2 * MARGIN
    # reservar espacio inferior para leyenda + cuadro de datos
    n_entries = len(m.used)
    leg_cols = 5
    leg_rows = math.ceil(n_entries / leg_cols)
    legend_h = leg_rows * 22 + 10
    bottom_block_h = max(legend_h, 120)        # leyenda o cuadro de datos
    avail_h = y - (MARGIN + bottom_block_h + 18)

    aspect = m.width_px / m.height_px
    img_w = content_w
    img_h = img_w / aspect
    if img_h > avail_h:
        img_h = avail_h
        img_w = img_h * aspect
    img_x = (PAGE_W - img_w) / 2
    img_y = y - img_h

    preview = render_preview(m, block=10)
    c.drawImage(ImageReader(preview), img_x, img_y, img_w, img_h)

    # rejilla de placas + numeros
    cw = img_w / m.cols
    ch = img_h / m.rows
    c.setStrokeColor(colors.white)
    c.setLineWidth(1.4)
    for i in range(1, m.cols):
        c.line(img_x + i * cw, img_y, img_x + i * cw, img_y + img_h)
    for j in range(1, m.rows):
        c.line(img_x, img_y + j * ch, img_x + img_w, img_y + j * ch)
    c.setStrokeColor(colors.Color(0.4, 0.4, 0.4))
    c.setLineWidth(0.8)
    c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)
    # numero de placa en la esquina sup-izq de cada placa
    bn = 1
    for row in range(m.rows):
        for col in range(m.cols):
            bx = img_x + col * cw + 3
            by = img_y + img_h - row * ch - 14
            c.setFillColor(colors.Color(0.12, 0.12, 0.12))
            c.roundRect(bx, by, 16, 12, 2, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(bx + 8, by + 3, str(bn))
            bn += 1

    # --- Bloque inferior: leyenda (izq) + cuadro de datos (der) ---
    block_top = img_y - 14
    leg_w = content_w * 0.62
    info_w = content_w * 0.34
    info_x = MARGIN + content_w - info_w

    entries = [(p, m.counts[p]) for p in m.used]
    _legend(c, entries, drawers, sym_order, m.palette_rgb,
            MARGIN, block_top, leg_w, ncols=leg_cols,
            swatch=16, font=11, row_h=22)

    # cuadro de datos
    info_h = 118
    info_y = block_top - info_h + 16
    c.saveState()
    c.setFillColor(colors.Color(0.85, 0.85, 0.85))
    c.rect(info_x, info_y, info_w, info_h, stroke=0, fill=1)
    c.setFillColor(colors.Color(0.15, 0.15, 0.15))
    c.setFont("Helvetica", 11)
    lines = [
        f"Nombre: {name or ''}",
        f"Placas: {m.n_boards}  ({m.cols} x {m.rows})",
        f"BRIX (piezas): {m.total_pieces}",
        f"Colores: {m.n_colors}",
        f"Paginas: {total_pages}",
        f"Medidas: {m.width_cm:.1f} x {m.height_cm:.1f} cm",
    ]
    ly = info_y + info_h - 18
    for ln in lines:
        c.drawString(info_x + 10, ly, ln)
        ly -= 17
    c.restoreState()

    _footer(c, "", f"PAGE 1/{total_pages}")
    c.showPage()


# ----------------------------------------------------------------------------
# PAGINAS DE PLACA
# ----------------------------------------------------------------------------
def _board_page(c, m: Mosaic, col, row, board_no, drawers, sym_order,
                total_pages, page_no):
    c.setPageSize(A3)
    bpw, bph = BOARD_PAGE_W, BOARD_PAGE_H
    cell = BOARD_CELL

    y = _logo(c, bph - MARGIN, page_w=bpw)
    board_grid = m.board_grid(col, row)

    # colores usados en esta placa (orden desc por conteo en la placa)
    vals, cts = np.unique(board_grid, return_counts=True)
    board_entries = sorted(
        [(int(v), int(cc)) for v, cc in zip(vals, cts)],
        key=lambda t: t[1], reverse=True
    )
    leg_cols = 5
    content_w = bpw - 2 * MARGIN

    grid_top = y - 8
    grid_w = cell * 33
    x_left = (bpw - grid_w) / 2

    # encabezados (numeros de columna y fila)
    c.setFont("Helvetica", max(4.5, cell * 0.42))
    c.setStrokeColor(colors.Color(0.75, 0.75, 0.75))
    c.setLineWidth(0.3)

    def cell_xy(i, j):
        x = x_left + j * cell
        ytop = grid_top - i * cell
        return x, ytop - cell

    # encabezado de columnas
    for j in range(1, 33):
        x, yb = cell_xy(0, j)
        c.setFillColor(colors.Color(0.93, 0.93, 0.93))
        c.rect(x, yb, cell, cell, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.drawCentredString(x + cell / 2, yb + cell * 0.32, str(j))
    # encabezado de filas
    for i in range(1, 33):
        x, yb = cell_xy(i, 0)
        c.setFillColor(colors.Color(0.93, 0.93, 0.93))
        c.rect(x, yb, cell, cell, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.drawCentredString(x + cell / 2, yb + cell * 0.32, str(i))
    # esquina
    x, yb = cell_xy(0, 0)
    c.setFillColor(colors.Color(0.85, 0.85, 0.85))
    c.rect(x, yb, cell, cell, stroke=1, fill=1)

    # celdas de datos
    r = cell * 0.34
    for i in range(1, 33):
        for j in range(1, 33):
            pidx = int(board_grid[i - 1, j - 1])
            rgb = m.palette_rgb[pidx]
            x, yb = cell_xy(i, j)
            c.setFillColor(_rl_color(rgb))
            c.setStrokeColor(colors.Color(0.55, 0.55, 0.55))
            c.setLineWidth(0.25)
            c.rect(x, yb, cell, cell, stroke=1, fill=1)
            drawer = drawers[sym_order[pidx]]
            drawer(c, x + cell / 2, yb + cell / 2, r, _ink_for(rgb))

    # leyenda de la placa
    leg_top = grid_top - 33 * cell - 12
    _legend(c, board_entries, drawers, sym_order, m.palette_rgb,
            MARGIN, leg_top, content_w, ncols=leg_cols,
            swatch=18, font=12, row_h=24)

    _footer(c, f"BOARD {board_no}/{m.n_boards}", f"PAGE {page_no}/{total_pages}",
            page_w=bpw)
    c.showPage()


# ----------------------------------------------------------------------------
# API principal
# ----------------------------------------------------------------------------
def build_pdf(mosaic: Mosaic, output, name: str = ""):
    """output: file path (str) or writable file-like object (e.g. BytesIO)."""
    drawers = sym.assign_symbols(len(mosaic.palette_rgb))
    sym_order = mosaic.symbol_order()
    total_pages = 1 + mosaic.n_boards

    c = canvas.Canvas(output, pagesize=A4)
    c.setTitle("Mosaico Pixel - Instructivo")

    _overview_page(c, mosaic, drawers, sym_order, total_pages, name)

    page_no = 2
    board_no = 1
    for row in range(mosaic.rows):
        for col in range(mosaic.cols):
            _board_page(c, mosaic, col, row, board_no, drawers,
                        sym_order, total_pages, page_no)
            board_no += 1
            page_no += 1

    c.save()
    return output
