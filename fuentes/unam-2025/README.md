# Exámenes UNAM 2025

Los cuatro `unam-a{1..4}-5.json` salen de aquí. La Guía UNAM 2025 incluye un
**examen muestra completo** por área —120 reactivos con su clave—, así que a
diferencia del IPN no hay que seleccionar nada: se transcribe y se ensambla.

## Cómo se arma

    python3 fuentes/unam-2025/armar.py 1     # área 1, 2, 3 o 4

Lee los tramos transcritos (`a{N}-2025-*.json`), valida y escribe
`unam-a{N}-5.json` en la raíz. **Si algo no cuadra no escribe nada.**

## La validación es determinista

La clave de cada guía tiene capa de texto, así que se extrae con `pdftotext` a
`claves/clave-a{N}-2025.json` y `armar.py` compara reactivo por reactivo: la
respuesta **y** la asignatura. Eso descubrió que la clave del PDF también sirve
para saber a qué materia pertenece cada reactivo, lo que quitó 32 lecturas de
imagen por área y volvió la verificación una comparación de Python en vez de un
segundo modelo revisando.

## Correcciones de clave

Cuando la clave oficial está mal, la corrección va en
`claves/correcciones.json` **con su motivo escrito**, y `armar.py` valida contra
la clave ya corregida, dejando constancia en el reactivo (`_correccion`).

Nunca a mano sobre el JSON de la raíz: eso se pierde al rearmar. Ya pasó con la
lectura "La mente colectiva" del Área 4, que volvió a su versión truncada.

Hoy hay una sola corrección: el **id 2 del Área 1**. Su figura se contradice
(dibuja el vector de 9 N a unos 20° y lo rotula 75°) y la clave marca un valor
inalcanzable: probadas las 192 combinaciones de cuadrante y eje de referencia con
la tabla de la propia guía, ninguna da √101.1. El único valor alcanzable es
√75.8, y sale midiendo los 30° del vector de 8 N desde el eje vertical.

## Figuras

    figuras/comun.py           piezas compartidas (svg, zigzag, flecha, rótulos)
    figuras/gen_a1_*.py        generadores por área y tanda
    figuras/figuras.json       registro de las ya dibujadas

Se dibujan como SVG generados por script, no a mano, para poder corregirlas. Las
que ya existen se registran en `figuras.json` con su archivo; `armar.py` las
conecta al examen y se niega a escribir si alguna registrada no está en disco.
Los reactivos con figura pendiente conservan su descripción en
`_figura_pendiente`, fuera de lo que ve el alumno.

Un valor del registro puede ser un archivo suelto o un dict con `enunciado` y
`opciones`, para los reactivos que llevan una figura por opción.

Convenciones de dibujo: trazo en `currentColor` para que la figura se adapte al
tema claro/oscuro, rellenos tintados con `fill-opacity` baja, y en los circuitos
el cable **interrumpido** donde va la pila o un resistor, nunca pasando por
detrás.

## Las guías

No están en el repo: pesan demasiado para GitHub. Viven en
`fuentes/unam-guias/`, que documenta de dónde bajarlas.
