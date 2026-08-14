from __future__ import annotations

import base64
import io
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from PIL import Image

from pictobrix.processor import PLATE, PLATE_CM, PIECES_PER_PLATE, build_mosaic, render_preview
from pictobrix.pdf_builder import build_pdf
from pictobrix import icons, inventory as inv, palette as pal


_DATA_DIR = os.environ.get("DATA_DIR")
if _DATA_DIR:
    os.makedirs(_DATA_DIR, exist_ok=True)
    _DB_PATH = os.path.join(_DATA_DIR, "stats.db")
else:
    _DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webapp", "stats.db")


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


def _client_ip(request):
    return request.headers.get("X-Forwarded-For", request.META.get("REMOTE_ADDR", ""))


def _log_event(request, action, cols, rows, mosaic, name, elapsed):
    conn = _db()
    conn.execute(
        """INSERT INTO events
           (ts, action, ip, user_agent, referer,
            cols, rows, colors, boards, pieces, name, size_cm, elapsed)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            action,
            _client_ip(request),
            request.headers.get("User-Agent", ""),
            request.headers.get("Referer", ""),
            cols,
            rows,
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
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _params(request):
    d = json.loads(request.body.decode("utf-8"))
    cols = max(1, int(d.get("cols", 3)))
    rows = max(1, int(d.get("rows", 3)))
    colors = int(d.get("colors", 26))
    max_colors = None if colors <= 0 else colors
    name = (d.get("name") or "").strip()
    img = _decode_dataurl(d["image"])
    return img, cols, rows, max_colors, name


# El generador es publico: cualquiera puede usarlo sin cuenta. ensure_csrf_cookie
# garantiza la cookie csrftoken que el JS de la pagina manda en /preview y
# /generate (antes venia "de rebote" del formulario de salir, que ya no se
# dibuja para visitantes anonimos).
@ensure_csrf_cookie
def index(request):
    return render(
        request,
        "generator/index.html",
        {"plate_cm": PLATE_CM, "plate": PLATE, "pieces_per_plate": PIECES_PER_PLATE},
    )


@require_POST
def preview(request):
    img, cols, rows, max_colors, name = _params(request)
    t0 = time.time()
    capacities = inv.get_capacities()
    mosaic = build_mosaic(
        img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True, capacities=capacities
    )
    prev = render_preview(mosaic, block=8)
    elapsed = time.time() - t0
    _log_event(request, "preview", cols, rows, mosaic, name, elapsed)

    buf = io.BytesIO()
    prev.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return JsonResponse(
        {
            "preview": "data:image/png;base64," + b64,
            "boards": mosaic.n_boards,
            "pieces": mosaic.total_pieces,
            "colors": mosaic.n_colors,
            "width_cm": round(mosaic.width_cm, 1),
            "height_cm": round(mosaic.height_cm, 1),
            "pages": 1 + mosaic.n_boards,
            "stock_limited": not inv.is_empty(),
            "stock_colors": len(inv.available_stock()),
            "stock_missing": sum(inv.shortage_for(mosaic.counts).values()),
        }
    )


@require_POST
def generate_pdf(request):
    img, cols, rows, max_colors, name = _params(request)
    t0 = time.time()
    capacities = inv.get_capacities()
    mosaic = build_mosaic(
        img, cols=cols, rows=rows, max_colors=max_colors, pre_cropped=True, capacities=capacities
    )
    buf = io.BytesIO()
    build_pdf(mosaic, buf, name=name)
    missing = sum(inv.shortage_for(mosaic.counts).values())
    inv.deduct_for_mosaic(mosaic.counts, reason="venta", note=name)
    elapsed = time.time() - t0
    _log_event(request, "pdf", cols, rows, mosaic, name, elapsed)
    buf.seek(0)
    fname = (name.replace(" ", "_") or "mosaico_pixel") + "_instructivo.pdf"
    response = FileResponse(buf, as_attachment=True, filename=fname, content_type="application/pdf")
    response["X-Stock-Missing"] = str(missing)
    return response


@staff_member_required
def stats_panel(request):
    conn = _db()
    total_pdfs = conn.execute("SELECT COUNT(*) FROM events WHERE action='pdf'").fetchone()[0]
    total_previews = conn.execute("SELECT COUNT(*) FROM events WHERE action='preview'").fetchone()[0]
    unique_ips = conn.execute("SELECT COUNT(DISTINCT ip) FROM events").fetchone()[0]
    avg_time = conn.execute("SELECT COALESCE(AVG(elapsed),0) FROM events WHERE action='pdf'").fetchone()[0]
    total_pieces = conn.execute("SELECT COALESCE(SUM(pieces),0) FROM events WHERE action='pdf'").fetchone()[0]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pdfs_today = conn.execute(
        "SELECT COUNT(*) FROM events WHERE action='pdf' AND ts LIKE ?", (today + "%",)
    ).fetchone()[0]
    top_configs = [
        {"cfg": row["cfg"], "n": row["n"]}
        for row in conn.execute(
        """SELECT cols||'x'||rows AS cfg, COUNT(*) AS n
           FROM events WHERE action='pdf'
           GROUP BY cfg ORDER BY n DESC LIMIT 5"""
        ).fetchall()
    ]
    recent = [dict(row) for row in conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 50").fetchall()]
    conn.close()

    return render(
        request,
        "generator/stats.html",
        {
            "total_pdfs": total_pdfs,
            "total_previews": total_previews,
            "unique_ips": unique_ips,
            "avg_time": round(avg_time, 2),
            "total_pieces": total_pieces,
            "pdfs_today": pdfs_today,
            "top_configs": top_configs,
            "recent": recent,
        },
    )


@staff_member_required
def inventory_panel(request):
    stock = inv.get_all_stock()
    names = pal.palette_names()
    rgb = pal.palette_rgb()
    colors = [
        {
            "index": i,
            "name": names[i],
            "rgb": f"{rgb[i][0]},{rgb[i][1]},{rgb[i][2]}",
            "quantity": stock.get(i),
            "managed": i in stock,
            "available": stock.get(i, 0) > 0,
            "icon_url": reverse("inventory_icon", args=[i]) + f"?v={icons.icon_version(i)}",
        }
        for i in range(len(names))
    ]
    movements = [
        {
            "ts": row["ts"],
            "color_name": names[row["color_index"]],
            "delta": row["delta"],
            "reason": row["reason"],
            "note": row["note"],
        }
        for row in inv.recent_movements(50)
    ]

    return render(
        request,
        "generator/inventory.html",
        {
            "colors": colors,
            "movements": movements,
            "names": names,
            "empty": inv.is_empty(),
            "n_available": sum(1 for c in colors if c["available"]),
            "total_pieces": sum(stock.values()),
        },
    )


@staff_member_required
def inventory_icon(request, idx):
    try:
        png = icons.icon_png(idx, size=96)
    except ValueError:
        return HttpResponse("Not found", status=404)
    return HttpResponse(
        png,
        content_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


def _stock_form(request):
    try:
        return (
            int(request.POST["color_index"]),
            int(request.POST["quantity"]),
            (request.POST.get("note") or "").strip(),
        )
    except (KeyError, ValueError):
        return None


@staff_member_required
@require_POST
def inventory_add(request):
    data = _stock_form(request)
    if data is None:
        return HttpResponse("Datos invalidos", status=400)
    color_index, quantity, note = data
    if quantity <= 0:
        return HttpResponse("La cantidad a agregar debe ser mayor a 0", status=400)
    try:
        inv.add_stock(color_index, quantity, note=note)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    return redirect("inventory_panel")


@staff_member_required
@require_POST
def inventory_remove(request):
    data = _stock_form(request)
    if data is None:
        return HttpResponse("Datos invalidos", status=400)
    color_index, quantity, note = data
    if quantity <= 0:
        return HttpResponse("La cantidad a quitar debe ser mayor a 0", status=400)
    try:
        inv.remove_stock(color_index, quantity, note=note)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    return redirect("inventory_panel")


@staff_member_required
@require_POST
def inventory_set(request):
    data = _stock_form(request)
    if data is None:
        return HttpResponse("Datos invalidos", status=400)
    color_index, quantity, note = data
    try:
        inv.set_stock(color_index, quantity, note=note)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    return redirect("inventory_panel")
