#!/usr/bin/env python3
"""
cli.py — Interfaz de linea de comandos del sistema PicToBrix.

Ejemplos:
    python cli.py foto.jpg salida.pdf --cols 3 --rows 3
    python cli.py foto.jpg salida.pdf --cols 2 --rows 3 --colors 24 --name "Familia"
    python cli.py foto.jpg salida.pdf --cols 1 --rows 1 --crop contain

Patron base: cada placa = 32x32 pixeles = 25.6 x 25.6 cm = 1024 piezas.
El arreglo cols x rows define la forma (vertical u horizontal).
"""

import argparse
import sys
from pictobrix import generate, PLATE_CM, PIECES_PER_PLATE


def main():
    ap = argparse.ArgumentParser(
        description="Convierte una foto JPG en un mosaico de brix y genera el PDF de instructivo."
    )
    ap.add_argument("imagen", help="Ruta de la imagen de entrada (jpg/png).")
    ap.add_argument("salida", help="Ruta del PDF de salida.")
    ap.add_argument("--cols", type=int, default=3, help="Placas a lo ancho (default 3).")
    ap.add_argument("--rows", type=int, default=3, help="Placas a lo alto (default 3).")
    ap.add_argument("--colors", type=int, default=26,
                    help="Maximo de colores en la leyenda (default 26; 0 = sin limite).")
    ap.add_argument("--crop", choices=["cover", "contain"], default="cover",
                    help="cover = recorta centrado; contain = rellena sin recortar.")
    ap.add_argument("--name", default="", help="Nombre que aparece en el cuadro de datos.")
    args = ap.parse_args()

    max_colors = None if args.colors <= 0 else args.colors
    try:
        m = generate(
            args.imagen, args.salida,
            cols=args.cols, rows=args.rows,
            max_colors=max_colors, crop_mode=args.crop, name=args.name,
        )
    except FileNotFoundError:
        print(f"No se encontro la imagen: {args.imagen}", file=sys.stderr)
        sys.exit(1)

    print(f"PDF generado: {args.salida}")
    print(f"  Placas:  {m.n_boards}  ({m.cols} x {m.rows})")
    print(f"  Piezas:  {m.total_pieces}  ({PIECES_PER_PLATE} por placa)")
    print(f"  Colores: {m.n_colors}")
    print(f"  Medidas: {m.width_cm:.1f} x {m.height_cm:.1f} cm  ({PLATE_CM} cm por placa)")
    print(f"  Paginas: {1 + m.n_boards}")


if __name__ == "__main__":
    main()
