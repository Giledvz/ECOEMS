# Instrucciones para trabajar en este repo

Empieza por [README.md](README.md), que explica qué es el proyecto y cómo corre.
Aquí van solo las cosas que se aprendieron a golpes y que no se deducen del código.

## Idioma

Todo en español de México: mensajes de commit, comentarios, documentación y, por
supuesto, lo que ve el alumno. Gil es hombre; el trato es de tú.

## Datos de alumnos — nunca se comitean

`resultados_*.csv`, `clave_respuestas_*.csv` y `comprobantes/` traen nombres y
calificaciones de menores de edad. Están en `.gitignore` y ahí se quedan. Si
alguna vez `git status` los muestra como sin rastrear, es correcto: déjalos así.

Tampoco se versionan `gencubos.js` ni `gencubos_cab.js`, por decisión de Gil.

## Antes de reiniciar el servidor, guarda

Las salas viven en memoria. Reiniciar sin guardar borra el trabajo de los alumnos,
y un examen son dos horas de cada uno. **Siempre** revisa primero:

    curl -s http://localhost:3000/api/rooms

Si alguna sala tiene alumnos, baja su CSV y su clave antes de tocar nada. Los
endpoints escriben en disco solitos. Esto ya estuvo a punto de costar dos exámenes
completos.

## Cómo trabaja Gil

- **Una opción, no un menú.** Propón UNA cosa concreta y deja que diga sí o no.
- **No ve la terminal.** Todo lo visual va como URL servida: las imágenes en
  `http://localhost:3000/_preview/…`, los PDF en `…/_pdf/…`. Si es para otro
  aparato, usa la IP de la LAN (`192.168.100.10`), no `localhost`.
- **Para reconstruir una figura**: propón la figura y la URL de la fuente; él dice
  sí o no y luego decide cómo hacerla.
- **Cuando insiste, tiene razón.** Pasó con la línea negra bajo el punteado del
  cuadernillo: dos veces dije que no existía, y sí existía. Antes de decirle que
  se equivoca, agota la verificación —convierte el PDF a vectores, revisa el
  stream, mira los datos crudos— en vez de mirar un render.

## Umbrales de calificación

Al reportar resultados: **≥70% verde, 50-69% amarillo, <50% rojo**. Da el número
grande y luego el desglose por materia, que es donde se ve qué estudiar.

## Verificar, no confiar

Las respuestas y las claves las va a usar un alumno que se juega su lugar. Todo lo
que se pueda comprobar de forma determinista, se comprueba:

- `fuentes/unam-2025/armar.py` valida cada respuesta contra la clave oficial
  extraída del PDF, y se niega a escribir si algo no cuadra.
- `fuentes/explicaciones/fusionar.py` valida las explicaciones antes de meterlas.
- `fuentes/ets/verificar.py` vuelve a resolver los 184 ejercicios por otro camino.

Cuando dos archivos necesitan los mismos parámetros, que uno los importe del otro.
Si cada quien tiene su copia, se desincronizan — ya pasó, y salió un ejercicio con
la diagonal equivocada.

**Lee la salida de la validación antes de comitear.** También ya pasó lo contrario.

## Las guías oficiales tienen erratas

No son pocas: hay 90 reactivos marcados en
[fuentes/explicaciones/revisar.md](fuentes/explicaciones/revisar.md) donde el
modelo no coincidió con la clave. Algunos son de verdad errores de la guía.

Cuando haya que corregir una clave, va con su motivo escrito en
`fuentes/unam-2025/claves/correcciones.json`, nunca suelta en el JSON del examen:
así rearmar no la borra y siempre se puede auditar. El id 2 del Área 1 es el
ejemplo a seguir.

## Las correcciones van en la fuente, no en el resultado

Los `*.json` de la raíz son **generados**. Si arreglas algo ahí y no en
`fuentes/`, el arreglo se pierde al rearmar. Pasó con una lectura del Área 4 que
volvió a su versión truncada.

Mismo principio con las figuras: se registran en
`fuentes/unam-2025/figuras/figuras.json` para que sobrevivan.

## Lo que el alumno ve

- El renderizador solo entiende LaTeX entre `$…$`, negritas, cursivas y tablas.
  **Cualquier otra etiqueta HTML sale literal en pantalla.**
- Los campos que empiezan con `_` son internos y nunca se muestran.
- En las figuras de los exámenes usa `fill="currentColor"`, que se adaptan al tema
  claro y oscuro. **Pero en un `<line>` con solo `stroke`, declara `fill="none"`
  explícito**: si hereda el relleno, Chrome lo emite al PDF como un trazo negro
  aunque en pantalla no se vea.

## Fuentes de reactivos

Para candidatas de ECOEMS, usa COMIPEMS y diagnóstico de bachillerato. **No** uses
los `sim_unam*`: ésos son de universidad y no corresponden.

Respalda siempre las guías originales (PDF, .tex, imágenes) en el repo, salvo que
pesen demasiado; en ese caso, documenta en un README de dónde bajarlas.
