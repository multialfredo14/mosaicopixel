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
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre **http://127.0.0.1:8000** y:

1. Sube una foto (JPG/PNG).
2. Elige el arreglo de placas (botones de placa u opciones de columnas/filas y
   orientación). El recorte se ajusta solo a esa proporción.
3. Encuadra la foto, fija el número de colores y un nombre (opcional).
4. **Vista previa** para ver el mosaico final.
5. **Generar PDF** para descargar el instructivo.

> La librería de recorte (Cropper.js) ya viene incluida en `webapp/static/`, así
> que la app funciona sin internet. Las tipografías se descargan de Google Fonts;
> si no hay conexión, se usan las del sistema sin problema.

### Login y administración

La web corre sobre **Django** y todo el generador exige sesión iniciada; los
paneles internos (`/mx-panel-2026*`) además exigen usuario **staff**.

- Login: `/accounts/login/`
- Crear cuenta (con Gmail o usuario/contraseña): `/accounts/registro/`
- Administración por defecto de Django: `/admin/` (usuarios, permisos, staff)

Primer usuario administrador:

```bash
python manage.py createsuperuser          # local
railway run python manage.py createsuperuser   # en producción
```

Para el acceso con Google define estas variables de entorno:

```bash
GOOGLE_OAUTH2_KEY=tu-client-id
GOOGLE_OAUTH2_SECRET=tu-client-secret
```

Mientras no existan, las pantallas ocultan el botón de Google y explican que
falta configurarlo (en vez de mandar a un error). En Google Cloud Console, los
**URI de redirección autorizados** deben ser exactamente:

```
http://127.0.0.1:8000/oauth/complete/google-oauth2/          (local)
https://TU-DOMINIO/oauth/complete/google-oauth2/             (producción)
```

Variables opcionales: `DJANGO_SECRET_KEY` (obligatoria en producción),
`DJANGO_DEBUG=1` para desarrollo, `DJANGO_ALLOWED_HOSTS` y
`DJANGO_CSRF_TRUSTED_ORIGINS` si el dominio no es el de Railway (el de Railway
se autoriza solo con `RAILWAY_PUBLIC_DOMAIN`).

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
| `--sell` | descuenta del inventario las piezas usadas | off |
| `--ignore-stock` | usa la paleta completa, sin limitarse al inventario | off |

---

## Uso 3 — Como librería de Python

```python
from pictobrix import generate

m = generate("foto.jpg", "instructivo.pdf",
             cols=3, rows=3, max_colors=26, name="Familia")

print(m.n_boards, m.total_pieces, m.n_colors, m.width_cm, m.height_cm)
```

---

## Inventario de piezas

El sistema lleva un inventario físico de piezas por color/símbolo
(`pictobrix/inventory.py`, respaldado en SQLite).

- **Agregar piezas**: panel web en `/mx-panel-2026/inventario` (misma URL
  oculta del panel de estadísticas), o por código con
  `pictobrix.inventory.add_stock(color_index, cantidad)`. Cada renglón muestra
  la **imagen real de la pieza** (sombrilla, calabaza, pato, …), tomada de
  `iconos/NN-nombre.jpeg` — ver `pictobrix/icons.py`.
- **Corregir a mano**: cada renglón trae "− Quitar" para descontar piezas
  (`inventory.remove_stock`, nunca baja de 0) y la tarjeta lateral agrega
  "= Fijar", que deja el color en una cantidad exacta sin importar lo que
  tuviera (`inventory.set_stock`) — la forma rápida de arreglar una captura
  equivocada. Ambos quedan registrados como movimiento `ajuste`.
- **Sólo se usa lo que existe**: si un color no está en el inventario (o se
  quedó en 0), no se usa en el mosaico ni aparece en el PDF; sus pixeles se
  pintan con el color disponible más parecido. Un color con stock tampoco se
  usa más allá de las piezas que tenga.
- **Descuento automático**: cada vez que se genera el PDF final desde la web
  (botón "Generar PDF") o con `cli.py ... --sell`, se considera que la venta
  del mosaico se concretó: se descuentan del inventario las piezas usadas.
- **Sin stock suficiente**: si las piezas disponibles no alcanzan para todo el
  mosaico, se arma igual con lo que hay (nunca falla) y la vista previa avisa
  cuántas piezas faltan.
- **Inventario vacío**: mientras no se haya cargado ningún color se usan los 40
  colores de la paleta, para poder trabajar desde el primer día.
- Protección opcional: si defines la variable de entorno `ADMIN_PASSWORD`,
  los paneles `/mx-panel-2026*` piden usuario/contraseña (HTTP Basic Auth).
  Sin esa variable, quedan abiertos como antes (solo por URL oculta).

---

## Estructura

```
pictobrix_system/
├── pictobrix/                 # motor (paquete Python)
│   ├── palette.py             # paleta de colores + emparejamiento Lab
│   ├── symbols.py             # símbolos vectoriales por color
│   ├── processor.py           # recorte / reescala / cuantización a mosaico
│   ├── inventory.py           # inventario de piezas (SQLite)
│   ├── icons.py               # imagen real de cada pieza (carpeta iconos/)
│   ├── icon_render.py         # respaldo: símbolo del PDF rasterizado
│   └── pdf_builder.py         # generación del PDF (portada + placas)
├── iconos/                    # NN-nombre.jpeg, un icono por color de paleta
├── webapp/
│   ├── app.py                 # servidor Flask anterior (referencia)
│   ├── templates/index.html   # interfaz (subir, encuadrar, previsualizar)
│   ├── templates/inventory.html  # panel de inventario
│   └── static/                # Cropper.js incluido
├── cli.py                     # interfaz de línea de comandos
├── manage.py                  # servidor Django
├── mosaicopixel/              # configuración Django + URLs
├── accounts/                  # registro manual
├── generator/                 # vistas Django del generador y paneles
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
