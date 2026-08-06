"""
inventory.py
------------
Inventario fisico de piezas "brix". Cada color de la paleta (ver palette.py)
representa una pieza distinta (color + simbolo), asi que el inventario se
gestiona por indice de color de paleta.

Un color sin registro en la tabla `stock` se considera "sin gestionar"
(sin limite): el sistema no restringe su uso hasta que se le agregue una
cantidad explicita por primera vez. A partir de ahi, su stock se descuenta
automaticamente cada vez que se concreta una venta (ver generate() en
pictobrix/__init__.py) y el armador de mosaicos evita usarlo mas alla de lo
disponible.
"""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime, timezone

from . import palette as pal

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS stock (
        color_index INTEGER PRIMARY KEY,
        quantity    INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS movements (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ts          TEXT    NOT NULL,
        color_index INTEGER NOT NULL,
        delta       INTEGER NOT NULL,
        reason      TEXT    NOT NULL,
        note        TEXT
    )""")
    conn.commit()
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _check_index(color_index: int) -> None:
    if not (0 <= color_index < len(pal.PALETTE)):
        raise ValueError(f"Indice de color invalido: {color_index}")


def add_stock(color_index: int, quantity: int, note: str = "") -> int:
    """Suma `quantity` piezas al color dado (crea el registro si no existia).
    Devuelve la cantidad disponible resultante."""
    _check_index(color_index)
    if quantity == 0:
        return get_stock(color_index) or 0
    conn = _conn()
    conn.execute(
        """INSERT INTO stock (color_index, quantity) VALUES (?, ?)
           ON CONFLICT(color_index) DO UPDATE SET quantity = quantity + excluded.quantity""",
        (color_index, quantity),
    )
    conn.execute(
        "INSERT INTO movements (ts, color_index, delta, reason, note) VALUES (?,?,?,?,?)",
        (_now(), color_index, quantity, "add", note),
    )
    conn.commit()
    row = conn.execute("SELECT quantity FROM stock WHERE color_index=?", (color_index,)).fetchone()
    conn.close()
    return row["quantity"]


def get_stock(color_index: int) -> int | None:
    """Cantidad disponible del color, o None si no esta gestionado (sin limite)."""
    conn = _conn()
    row = conn.execute("SELECT quantity FROM stock WHERE color_index=?", (color_index,)).fetchone()
    conn.close()
    return row["quantity"] if row else None


def get_all_stock() -> dict[int, int]:
    """Solo los colores gestionados explicitamente (con registro en la tabla)."""
    conn = _conn()
    rows = conn.execute("SELECT color_index, quantity FROM stock ORDER BY color_index").fetchall()
    conn.close()
    return {r["color_index"]: r["quantity"] for r in rows}


def get_capacities() -> dict[int, int | None]:
    """pidx -> cantidad disponible, para los 40 colores de la paleta.
    None significa sin limite (color no gestionado todavia)."""
    managed = get_all_stock()
    return {i: managed.get(i) for i in range(len(pal.PALETTE))}


def deduct_for_mosaic(counts: dict[int, int], reason: str = "venta", note: str = "") -> None:
    """
    Descuenta del inventario las piezas usadas por un mosaico ya construido.
    counts: pidx -> cantidad de piezas de ese color usadas en el mosaico.
    Los colores no gestionados (sin registro) se ignoran, ya que se
    consideran de existencia ilimitada.
    """
    conn = _conn()
    ts = _now()
    for pidx, used in counts.items():
        if used <= 0:
            continue
        row = conn.execute("SELECT quantity FROM stock WHERE color_index=?", (pidx,)).fetchone()
        if row is None:
            continue
        new_qty = max(0, row["quantity"] - used)
        conn.execute("UPDATE stock SET quantity=? WHERE color_index=?", (new_qty, pidx))
        conn.execute(
            "INSERT INTO movements (ts, color_index, delta, reason, note) VALUES (?,?,?,?,?)",
            (ts, pidx, -used, reason, note),
        )
    conn.commit()
    conn.close()


def recent_movements(limit: int = 50) -> list[sqlite3.Row]:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM movements ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows
