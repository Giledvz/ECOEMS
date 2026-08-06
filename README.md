# ECOEMS

Plataforma para aplicar simulacros de examen de admisión y un repositorio de los
exámenes mismos. Los alumnos entran desde su celular a una sala, contestan, y al
terminar ven su calificación y **por qué** cada respuesta era la correcta.

Dos destinos:

- **Ingreso a bachillerato** — COMIPEMS (los `ecoems-*.json`).
- **Ingreso a licenciatura** — UNAM por área, e IPN por rama (los `unam-*.json`,
  `ipn-*.json`).

## Levantar la plataforma

El servidor corre como servicio de macOS (`com.giledvz.ecoems-server`) en el
puerto 3000. Para reiniciarlo:

    launchctl kickstart -k gui/$(id -u)/com.giledvz.ecoems-server

Las salas viven **en memoria**: al reiniciar se borran todas. Antes de reiniciar,
guarda los resultados de las salas que tengan alumnos (ver abajo).

Direcciones:

| | |
|---|---|
| Alumno | `http://192.168.100.10:3000/?sala=CODIGO` |
| Profesor | `http://192.168.100.10:3000/teacher.html` |

La IP de la LAN sirve para cualquier aparato en el mismo WiFi. `localhost` solo
funciona en esta máquina.

### Crear una sala

    curl -X POST http://localhost:3000/api/upload-exam \
      -H 'Content-Type: application/json' \
      -H 'x-exam-filename: unam-a1-1.json' \
      --data-binary @unam-a1-1.json

Devuelve el código de sala. Con `-H 'x-mode: practice'` la sala es de práctica
guiada (el profesor lleva el ritmo); sin ese encabezado es examen normal.

### Guardar resultados

    curl -s "http://localhost:3000/api/download-csv?room=CODIGO" -o /dev/null
    curl -s "http://localhost:3000/api/download-key?room=CODIGO" -o /dev/null

Los dos endpoints **escriben el archivo en el disco** además de devolverlo, así
que basta llamarlos. Sin esto, reiniciar el servidor pierde el trabajo de los
alumnos.

### API

| Endpoint | Qué hace |
|---|---|
| `GET /api/rooms` | Salas vivas, con su fase y cuántos alumnos |
| `POST /api/upload-exam` | Crea una sala a partir de un JSON de examen |
| `GET /api/download-csv?room=` | Respuestas de los alumnos (y lo guarda en disco) |
| `GET /api/download-key?room=` | Clave del examen (y la guarda en disco) |
| `GET /api/comprobante-pdf?room=&name=` | Comprobante en PDF de un alumno |
| `GET /api/qr?...` | Código QR para entrar a la sala |
| `POST /api/dev-reload/:sala` | Recarga el examen sin recrear la sala. Bloqueado si ya arrancó, y **no** actualiza la lista de alumnos |

Fases de una sala: `waiting` → `active` → `finished` / `closed`. Las de práctica
usan además `answering` y `revealed`.

El servidor **baraja materias y opciones para cada alumno**. Es a propósito: dos
alumnos sentados juntos no ven el mismo orden.

## Los exámenes

Cada examen es un JSON en la raíz. Hoy hay **43**, con 5 012 reactivos:

| Grupo | Exámenes | Qué son |
|---|---|---|
| Universidad | 25 | 20 UNAM (4 áreas × 5), el especial y 4 diagnósticos |
| Ingreso a bachillerato | 12 | Los `ecoems-N` y los especiales |
| IPN | 3 | Uno por rama: IyCFM, CMB, CSyA |
| Otros | 3 | Diagnóstico de bachillerato y dos evaluaciones de mate-física |

Todos tienen sus explicaciones escritas **salvo `ecoems-4` y `ecoems-5`**, que
siguen esperando 24 figuras (sus guías COMIPEMS 2019 y 2021 no están en el repo).

De dónde salió cada uno: [ORIGEN_EXAMENES.md](ORIGEN_EXAMENES.md).

### Formato

```jsonc
{"exam": {
  "title": "UNAM Área 1 - 1",
  "group": "Universidad",
  "students": ["Óscar", "Alfredo", "Dana"],   // quién puede entrar a la sala
  "sections": [{
    "subject": "Matemáticas",
    "questions": [{
      "id": 1,
      "topic_name": "Matemáticas",
      "text": "…",                  // markdown + LaTeX entre $…$
      "context": "…",               // lectura compartida, opcional
      "image": "/imagenes_x/q1.svg",        // figura del enunciado, opcional
      "option_images": {"A": "…"},          // una figura por opción, opcional
      "options": {"A": "…", "B": "…", "C": "…", "D": "…"},
      "answer": "B",
      "explanation": "…"            // lo que el alumno lee al terminar
    }]
  }]
}}
```

Los campos que empiezan con `_` (`_figura_pendiente`, `_correccion`,
`_nota_lectura`) son internos: documentan algo para nosotros y **el alumno nunca
los ve**.

El renderizador (`public/shared/markdown-render.js`) entiende LaTeX entre `$…$`,
negritas, cursivas, tablas con `|` y poco más. **Cualquier etiqueta HTML que no
sea `u/b/i/strong/em/br/img` sale literal en pantalla.**

## Cómo se arma un examen

Las guías oficiales vienen en PDF y hay dos formas de trabajarlas, según lo que
traigan:

- **UNAM** — la guía incluye un examen muestra completo. Se transcribe por tramos
  a `fuentes/unam-2025/` y `armar.py` lo ensambla, validando cada respuesta
  contra la clave oficial extraída del propio PDF. Ver
  [fuentes/unam-2025/](fuentes/unam-2025/README.md).
- **IPN** — la guía es un banco de reactivos, no un examen. Hay que seleccionar y
  balancear. Ver [fuentes/ipn/](fuentes/ipn/README.md).

Las figuras se dibujan como SVG generados por script, no a mano: así se pueden
corregir y rehacer. Cada área tiene su generador en
`fuentes/unam-2025/figuras/`, y las ya dibujadas se registran en `figuras.json`
para que rearmar el examen no las borre.

## Cómo se escriben las explicaciones

Las escribe el modelo Fable, en lotes, con un verificador determinista encima.
Ver [fuentes/explicaciones/](fuentes/explicaciones/README.md).

## Otros materiales

- [fuentes/ets/](fuentes/ets/README.md) — cuadernillo de práctica para el ETS de
  Geometría y Trigonometría del CECyT 1 (184 ejercicios, PDF con hipervínculos).
- [fuentes/alumnos/](fuentes/alumnos/README.md) — padrón de alumnos por
  generación, reconstruido del historial de git.
- [fuentes/unam-aciertos/](fuentes/unam-aciertos/README.md) — aciertos mínimos
  históricos de ingreso a la UNAM.

## Qué NO se versiona

Nunca, por ningún motivo:

- `resultados_*.csv` y `clave_respuestas_*.csv` — **datos de alumnos**.
- `comprobantes/` — sus PDF con nombre y calificación.
- `public/_preview/`, `public/_pdf/`, `public/_fuente/` — copias servidas y
  temporales.
- `gencubos.js`, `gencubos_cab.js` — por decisión de Gil.

Las guías oficiales en PDF tampoco: pesan demasiado para GitHub. Viven en disco y
cada carpeta documenta de dónde bajarlas.

## Convenciones

Las de autoría y diseño de los exámenes están en
[CONVENCIONES.md](CONVENCIONES.md). Las de trabajo con IA, en
[CLAUDE.md](CLAUDE.md).
