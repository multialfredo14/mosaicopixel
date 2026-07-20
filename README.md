# PicToBrix — Sistema generador de instructivos

Convierte una **foto** en un **mosaico de "brix"** y genera automáticamente un
**PDF de instructivo** con el mismo formato del ejemplo PicToBrix:

- **Portada**: logo, vista del mosaico con las placas numeradas, leyenda global
  (un símbolo por color + conteo total) y cuadro de datos (Nombre, Placas, BRIX,
  Colores, Páginas, Medidas).
- **Una página por placa**: cuadrícula de **32×32** con números de columna (1–32)
  arriba y de fila (1–32) a la izquierda. Cada celda lleva su **color de fondo +
  un símbolo** que se sigue como patrón. Abajo, la leyenda de esa placa.

El mismo símbolo representa siempre al mismo color en **todo** el documento.

---

## Patrón base

| Concepto | Valor |
|---|---|
| 1 placa | 32 × 32 píxeles |
| 1 placa | 25.6 × 25.6 cm |
| 1 placa | 1,024 piezas |

El arreglo de placas (columnas × filas) define la forma. Ejemplos:
`1×1`, `2×1`, `1×2`, `2×2`, `3×2`, `2×3`, `3×3`, `4×3`… así puedes hacer cuadros
**verticales u horizontales**. Un `3×3` = 9 placas = **9,216 piezas** = 76.8 × 76.8 cm
(igual que el ejemplo que diste).

---

## Instalación

```bash
pip install -r requirements.txt
```

(o bien: `pip install Pillow numpy reportlab Flask`)

---

## Uso 1 — Interfaz web (recomendado)

Permite **encuadrar la foto** de forma interactiva con la proporción exacta de las
placas, ver la vista previa del mosaico y descargar el PDF.

```bash
python webapp/app.py
```

Abre **http://127.0.0.1:5000** y:

1. Sube una foto (JPG/PNG).
2. Elige el arreglo de placas (botones de placa u opciones de columnas/filas y
   orientación). El recorte se ajusta solo a esa proporción.
3. Encuadra la foto, fija el número de colores y un nombre (opcional).
4. **Vista previa** para ver el mosaico final.
5. **Generar PDF** para descargar el instructivo.

> La librería de recorte (Cropper.js) ya viene incluida en `webapp/static/`, así
> que la app funciona sin internet. Las tipografías se descargan de Google Fonts;
> si no hay conexión, se usan las del sistema sin problema.

---

## Uso 2 — Línea de comandos

```bash
# 3x3 placas (9216 piezas), 26 colores
python cli.py foto.jpg salida.pdf --cols 3 --rows 3 --colors 26 --name "Familia"

# vertical 2x3 (50x75 cm aprox), 24 colores
python cli.py foto.jpg salida.pdf --cols 2 --rows 3 --colors 24

# un solo cuadro sin recortar (rellena bordes)
python cli.py foto.jpg salida.pdf --cols 1 --rows 1 --crop contain
```

Opciones:

| Opción | Descripción | Default |
|---|---|---|
| `--cols` | placas a lo ancho | 3 |
| `--rows` | placas a lo alto | 3 |
| `--colors` | máximo de colores en la leyenda (`0` = sin límite) | 26 |
| `--crop` | `cover` (recorta centrado) o `contain` (rellena) | cover |
| `--name` | nombre en el cuadro de datos | — |

---

## Uso 3 — Como librería de Python

```python
from pictobrix import generate

m = generate("foto.jpg", "instructivo.pdf",
             cols=3, rows=3, max_colors=26, name="Familia")

print(m.n_boards, m.total_pieces, m.n_colors, m.width_cm, m.height_cm)
```

---

## Estructura

```
pictobrix_system/
├── pictobrix/                 # motor (paquete Python)
│   ├── palette.py             # paleta de colores + emparejamiento Lab
│   ├── symbols.py             # símbolos vectoriales por color
│   ├── processor.py           # recorte / reescala / cuantización a mosaico
│   └── pdf_builder.py         # generación del PDF (portada + placas)
├── webapp/
│   ├── app.py                 # servidor Flask
│   ├── templates/index.html   # interfaz (subir, encuadrar, previsualizar)
│   └── static/                # Cropper.js incluido
├── cli.py                     # interfaz de línea de comandos
├── requirements.txt
└── README.md
```

---

## Personalización rápida

- **Colores disponibles**: edita la lista `PALETTE` en `pictobrix/palette.py`
  (nombre + RGB). Si conoces los colores exactos de tu proveedor de placas,
  ponlos ahí y el sistema emparejará cada pixel al color real más cercano.
- **Símbolos**: se asignan automáticamente. Hay ~33 símbolos dibujados; si una
  imagen usa más colores, se completan con letras/números. Puedes agregar más en
  `pictobrix/symbols.py` (lista `SYMBOLS`).
- **Tamaño de placa**: `PLATE` (32) y `PLATE_CM` (25.6) en `pictobrix/processor.py`.
