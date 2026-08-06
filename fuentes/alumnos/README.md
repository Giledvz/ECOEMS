# Padrón de alumnos

`padron.json` y `PADRON.md`: quién ha presentado exámenes, en qué generación y
para qué destino.

Se reconstruye con:

    python3 fuentes/scripts/padron-alumnos.py

## Por qué existe

Cada examen lleva su lista en `exam.students`, pero esa lista solo dice quién
podía entrar a esa aplicación. Cuando se limpiaron las listas de exámenes viejos,
se perdió el registro de quién había estudiado con nosotros — y el problema
apareció al empezar a regresar alumnos a repetir el examen, algo que antes nunca
había pasado.

El script recorre los commits y recupera los nombres de todas las versiones
históricas de cada examen, con el año en que aparecieron.

## Ajustes a mano

El script no puede adivinar todo, así que lleva dos diccionarios explícitos:

- `ALIAS`, para nombres escritos de dos formas (Oscar / Óscar, Danna / Dana).
- `AJUSTES`, para lo que el historial no dice: que Gil es el profesor y no un
  alumno, o que Danna Belem es del proceso 2027 aunque aparezca en exámenes de
  2026.

Si aparece un caso nuevo, se agrega ahí y se vuelve a correr.
