#!/usr/bin/env python3
"""
app.py — Interfaz web del sistema PicToBrix.

Flujo:
  1. Subes una foto (jpg/png).
  2. La encuadras (recorte interactivo) con la proporcion de las placas elegidas.
  3. Eliges el arreglo de placas (1x1, 1x2, 2x2, 3x3, ...) y el numero de colores.
  4. Ves la vista previa del mosaico.
  5. Descargas el PDF del instructivo (portada + una pagina por placa).

Ejecutar:
    pip install flask pillow numpy reportlab
    python webapp/app.py
    -> abre http://127.0.0.1:5000
"""

import base64
import io
import os
import sys

# permitir importar el paquete pictobrix de la carpeta superior
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image

from pictobrix.processor import build_mosaic, render_preview, PLATE, PLATE_CM, PIECES_PER_PLATE
from pictobrix.pdf_builder import build_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB


def _decode_dataurl(data_url: str) -> Image.Image:
    """Convierte un dataURL (base64) en una imagen PIL RGB."""
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _params(req):
    d = req.get_json(force=True)
    cols = max(1, int(d.get("cols", 3)))
    rows = max(1, int(d.get("rows", 3)))
    colors = int(d.get("colors", 26))
    max_colors = None if colors <= 0 else colors
    name = (d.get("name") or "").strip()
    img = _decode_dataurl(d["image"])
    return img, cols, rows, max_colors, name


@app.route("/")
def index():
    return render_template("index.html", plate_cm=PLATE_CM, plate=PLATE,
                           pieces_per_plate=PIECES_PER_PLATE)


@app.route("/preview", methods=["POST"])
def preview():
    img, cols, rows, max_colors, _ = _params(request)
    m = build_mosaic(img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True)
    prev = render_preview(m, block=8)
    buf = io.BytesIO()
    prev.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({
        "preview": "data:image/png;base64," + b64,
        "boards": m.n_boards,
        "pieces": m.total_pieces,
        "colors": m.n_colors,
        "width_cm": round(m.width_cm, 1),
        "height_cm": round(m.height_cm, 1),
        "pages": 1 + m.n_boards,
    })


@app.route("/generate", methods=["POST"])
def generate_pdf():
    img, cols, rows, max_colors, name = _params(request)
    m = build_mosaic(img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True)
    buf = io.BytesIO()
    build_pdf(m, buf, name=name)
    buf.seek(0)
    fname = (name.replace(" ", "_") or "pictobrix") + "_instructivo.pdf"
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name=fname)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
