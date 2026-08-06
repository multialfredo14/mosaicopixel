"""
inventory.py
------------
Inventario fisico de piezas "brix". Cada color de la paleta (ver palette.py)
representa una pieza distinta (color + simbolo), asi que el inventario se
gestiona por indice de color de paleta.

Regla del sistema: el mosaico (y por lo tanto el PDF) se arma UNICAMENTE con
los legos que existen en el inventario. Un color sin registro en la tabla
`stock`, o con 0 piezas, no se usa: los pixeles que le corresponderian se
reasignan al color disponible mas parecido. El stock se descuenta
automaticamente cada vez que se concreta una venta (ver generate() en
pictobrix/__init__.py).

Excepcion: mientras el inventario este completamente vacio (ningun color
cargado todavia) no se restringe nada y se usa la paleta completa, para que
el generador funcione desde el primer dia sin tener que capturar stock.
"""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime, timezone

from . import palette as pal

# Si se define DATA_DIR (p.ej. un volumen persistente de Railway), el
# inventario vive ahi y sobrevive a los redeploys. Sin esa variable
# (desarrollo local) se guarda junto al paquete, como antes.
_DATA_DIR = os.environ.get("DATA_DIR")
if _DATA_DIR:
    os.makedirs(_DATA_DIR, exist_ok=True)
    _DB_PATH = os.path.join(_DATA_DIR, "inventory.db")
else:
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


def remove_stock(color_index: int, quantity: int, note: str = "") -> int:
    """
    Quita piezas a mano: correccion de una captura equivocada, piezas rotas,
    perdidas, etc. Nunca deja el stock en negativo -- si se piden mas piezas
    de las que hay, se quitan solo las que existan.
    Devuelve la cantidad disponible resultante.
    """
    _check_index(color_index)
    if quantity <= 0:
        return get_stock(color_index) or 0
    conn = _conn()
    row = conn.execute(
        "SELECT quantity FROM stock WHERE color_index=?", (color_index,)
    ).fetchone()
    if row is None or row["quantity"] <= 0:
        conn.close()
        raise ValueError(f"{pal.PALETTE[color_index][0]} no tiene piezas que quitar.")
    removed = min(quantity, row["quantity"])
    new_qty = row["quantity"] - removed
    conn.execute("UPDATE stock SET quantity=? WHERE color_index=?", (new_qty, color_index))
    conn.execute(
        "INSERT INTO movements (ts, color_index, delta, reason, note) VALUES (?,?,?,?,?)",
        (_now(), color_index, -removed, "ajuste", note),
    )
    conn.commit()
    conn.close()
    return new_qty


def set_stock(color_index: int, quantity: int, note: str = "") -> int:
    """
    Deja el color exactamente en `quantity` piezas, sin importar lo que
    hubiera antes (la forma mas directa de corregir una cantidad mal
    capturada). Registra el movimiento con la diferencia.
    """
    _check_index(color_index)
    if quantity < 0:
        raise ValueError("La cantidad no puede ser negativa.")
    conn = _conn()
    row = conn.execute(
        "SELECT quantity FROM stock WHERE color_index=?", (color_index,)
    ).fetchone()
    delta = quantity - (row["quantity"] if row else 0)
    conn.execute(
        """INSERT INTO stock (color_index, quantity) VALUES (?, ?)
           ON CONFLICT(color_index) DO UPDATE SET quantity = excluded.quantity""",
        (color_index, quantity),
    )
    if delta:
        conn.execute(
            "INSERT INTO movements (ts, color_index, delta, reason, note) VALUES (?,?,?,?,?)",
            (_now(), color_index, delta, "ajuste", note),
        )
    conn.commit()
    conn.close()
    return quantity


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


def is_empty() -> bool:
    """True si todavia no se ha cargado ningun color al inventario."""
    return not get_all_stock()


def available_stock() -> dict[int, int]:
    """Solo los colores que hoy tienen piezas para armar (cantidad > 0)."""
    return {i: q for i, q in get_all_stock().items() if q > 0}


def get_capacities() -> dict[int, int | None]:
    """
    pidx -> piezas disponibles para armar, para los 40 colores de la paleta.

    Un color que no existe en el inventario (sin registro) o que se quedo en
    0 devuelve 0: no se usa en el mosaico ni aparece en el PDF. Si el
    inventario esta vacio por completo se devuelve None en todos los colores
    (sin limite), que es como se comportaba el sistema antes de cargar stock.
    """
    managed = get_all_stock()
    if not managed:
        return {i: None for i in range(len(pal.PALETTE))}
    return {i: managed.get(i, 0) for i in range(len(pal.PALETTE))}


def shortage_for(counts: dict[int, int]) -> dict[int, int]:
    """
    pidx -> piezas que le faltarian al inventario para cubrir `counts`.
    Vacio si alcanza (o si el inventario todavia no se usa como limite).
    """
    capacities = get_capacities()
    missing = {}
    for pidx, used in counts.items():
        cap = capacities.get(pidx)
        if cap is not None and used > cap:
            missing[pidx] = used - cap
    return missing


def deduct_for_mosaic(counts: dict[int, int], reason: str = "venta", note: str = "") -> None:
    """
    Descuenta del inventario las piezas usadas por un mosaico ya construido.
    counts: pidx -> cantidad de piezas de ese color usadas en el mosaico.
    Los colores sin registro se ignoran: solo aparecen en un mosaico cuando
    el inventario esta vacio y no hay nada que descontar.
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
