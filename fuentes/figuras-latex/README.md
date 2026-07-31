# Fuentes LaTeX de las figuras del diagnóstico de bachillerato

Recuperadas del commit inicial (32814ec), donde vivían en la raíz del repo y se
borraron en 4721346 ("Limpieza de archivos LaTeX, PDFs e imágenes que ya no se
usan"). Son el TikZ con el que se dibujaron las once figuras que hoy están como
`public/figura_1.svg` … `figura_11.svg` y que usa `diag-bach.json` (ids 4 al 14).

| Archivo | Qué trae |
|---|---|
| `figuras_individuales.tex` | las once figuras, una por página: cadena de óvalos, series espaciales, conteo de triángulos y de rectángulos, rotaciones, triángulos con números, tabla |
| `habilidad_mate_v1.tex` | el examen completo de habilidad matemática, con la respuesta y el razonamiento anotados en comentarios |
| `nuevas_q5q6.tex` | versiones alternas de las preguntas 5 y 6, con la opción correcta marcada en los comentarios |
| `figuras_individuales.pdf` | el render de `figuras_individuales.tex` |

Se conservan porque son la única forma de re-dibujar esas figuras con la geometría
exacta si algún día hay que cambiarles algo; el SVG ya compilado no dice cuál era la
regla del patrón ni por qué una opción es la correcta.

NO son fuente de ECOEMS 4 ni 5: sus números no coinciden (la cadena de aquí es
7, 12, 10, 15, 13, 18, 16 y la de ECOEMS 4 es 20, 15, 19, 18, 17, 24, 14).
