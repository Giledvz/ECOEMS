# Utilidades sueltas

Scripts que operan sobre los exámenes ya armados y no pertenecen a ninguna
tubería en particular.

## extraer-lecturas.py

Cuando varios reactivos comparten una lectura, el texto a veces viene pegado
dentro del enunciado del primero. Este script lo mueve al campo `context`, que
es el que la plataforma dibuja en su propio recuadro, y de paso quita el renglón
de instrucción ("Lee el siguiente texto…"), que dentro del recuadro sobra.

    python3 fuentes/scripts/extraer-lecturas.py --dry    # reporta, no escribe
    python3 fuentes/scripts/extraer-lecturas.py          # aplica

Importa porque un reactivo sin su lectura llega ilegible al alumno. Ya pasó: en
los IPN, cuatro reactivos de probabilidad se aplicaron sin su tabla de
frecuencias — "calcular la media" sin datos.

## temas-flojos.py

    python3 fuentes/scripts/temas-flojos.py                    # todo
    python3 fuentes/scripts/temas-flojos.py Universidad        # solo un grupo
    python3 fuentes/scripts/temas-flojos.py Universidad Dana   # y un alumno

Qué temas se les están atorando, para saber qué dar en clase. Cruza cada
`resultados_CODIGO_*.csv` con su `clave_respuestas_CODIGO_*.csv` —que trae el
tema de cada reactivo— y agrega los fallos **por tema**, no por pregunta.

Dos cosas que hace y que importan:

- **Separa lo que alcanza para diagnosticar.** Un tema suele traer un reactivo
  por examen, así que con un solo examen el dato no dice nada. Solo reporta los
  que llevan al menos 3 alumnos-intento y avisa cuántos quedaron fuera.
- **Avisa cuando el reactivo es sospechoso.** Cruza contra
  `fuentes/explicaciones/revisar.md`: si un tema salió en cero pero su clave está
  en duda, puede que el error sea de la guía y los alumnos tuvieran razón. Dar
  clase sobre eso sería corregirles algo que contestaron bien.

## padron-alumnos.py

    python3 fuentes/scripts/padron-alumnos.py

Reconstruye el padrón de alumnos recorriendo el historial de git. Ver
[fuentes/alumnos/](../alumnos/README.md).
