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
import sqlite3
import sys
import time
from datetime import datetime, timezone

# permitir importar el paquete pictobrix de la carpeta superior
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image

from pictobrix.processor import build_mosaic, render_preview, PLATE, PLATE_CM, PIECES_PER_PLATE
from pictobrix.pdf_builder import build_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB

# ---------------------------------------------------------------------------
# Base de datos de estadísticas
# ---------------------------------------------------------------------------
_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.db")


def _db():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        ts       TEXT    NOT NULL,
        action   TEXT    NOT NULL,
        ip       TEXT,
        user_agent TEXT,
        referer  TEXT,
        cols     INTEGER,
        rows     INTEGER,
        colors   INTEGER,
        boards   INTEGER,
        pieces   INTEGER,
        name     TEXT,
        size_cm  TEXT,
        elapsed  REAL
    )""")
    conn.commit()
    return conn


def _log_event(action, cols, rows, mosaic, name, elapsed):
    conn = _db()
    conn.execute(
        """INSERT INTO events
           (ts, action, ip, user_agent, referer,
            cols, rows, colors, boards, pieces, name, size_cm, elapsed)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            action,
            request.headers.get("X-Forwarded-For", request.remote_addr),
            request.headers.get("User-Agent", ""),
            request.headers.get("Referer", ""),
            cols, rows,
            mosaic.n_colors,
            mosaic.n_boards,
            mosaic.total_pieces,
            name,
            f"{mosaic.width_cm:.1f} x {mosaic.height_cm:.1f}",
            round(elapsed, 2),
        ),
    )
    conn.commit()
    conn.close()


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
    img, cols, rows, max_colors, name = _params(request)
    t0 = time.time()
    m = build_mosaic(img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True)
    prev = render_preview(m, block=8)
    elapsed = time.time() - t0
    _log_event("preview", cols, rows, m, name, elapsed)
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
    t0 = time.time()
    m = build_mosaic(img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True)
    buf = io.BytesIO()
    build_pdf(m, buf, name=name)
    elapsed = time.time() - t0
    _log_event("pdf", cols, rows, m, name, elapsed)
    buf.seek(0)
    fname = (name.replace(" ", "_") or "mosaico_pixel") + "_instructivo.pdf"
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name=fname)


# ---------------------------------------------------------------------------
# Panel de estadísticas (URL oculta)
# ---------------------------------------------------------------------------
@app.route("/mx-panel-2026")
def stats_panel():
    conn = _db()

    total_pdfs = conn.execute(
        "SELECT COUNT(*) FROM events WHERE action='pdf'"
    ).fetchone()[0]
    total_previews = conn.execute(
        "SELECT COUNT(*) FROM events WHERE action='preview'"
    ).fetchone()[0]
    unique_ips = conn.execute(
        "SELECT COUNT(DISTINCT ip) FROM events"
    ).fetchone()[0]
    avg_time = conn.execute(
        "SELECT COALESCE(AVG(elapsed),0) FROM events WHERE action='pdf'"
    ).fetchone()[0]
    total_pieces = conn.execute(
        "SELECT COALESCE(SUM(pieces),0) FROM events WHERE action='pdf'"
    ).fetchone()[0]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pdfs_today = conn.execute(
        "SELECT COUNT(*) FROM events WHERE action='pdf' AND ts LIKE ?",
        (today + "%",)
    ).fetchone()[0]

    top_configs = conn.execute(
        """SELECT cols||'x'||rows AS cfg, COUNT(*) AS n
           FROM events WHERE action='pdf'
           GROUP BY cfg ORDER BY n DESC LIMIT 5"""
    ).fetchall()

    recent = conn.execute(
        "SELECT * FROM events ORDER BY id DESC LIMIT 50"
    ).fetchall()

    conn.close()

    return render_template("stats.html",
                           total_pdfs=total_pdfs,
                           total_previews=total_previews,
                           unique_ips=unique_ips,
                           avg_time=round(avg_time, 2),
                           total_pieces=total_pieces,
                           pdfs_today=pdfs_today,
                           top_configs=top_configs,
                           recent=recent)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
