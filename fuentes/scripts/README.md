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

## padron-alumnos.py

    python3 fuentes/scripts/padron-alumnos.py

Reconstruye el padrón de alumnos recorriendo el historial de git. Ver
[fuentes/alumnos/](../alumnos/README.md).
