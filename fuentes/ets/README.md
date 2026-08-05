# ETS de Geometría y Trigonometría — cuadernillo de práctica

IPN, CECyT 1 "Lic. Gonzalo Vázquez Vela", segundo semestre, materias básicas.
Son exámenes de **respuesta abierta** (no de opción múltiple): 10 problemas, dos
horas, y se califica el desarrollo, no nada más el resultado.

## Qué hay aquí

    originales/        los ocho ETS que tenemos: 2009, 2010, 2017, 2018, 2019,
                       2023, 2025 y enero de 2026
    generar.py         arma los 184 ejercicios, con su procedimiento
    verificar.py       vuelve a resolverlos por otro camino y compara
    armar-html.py      arma cuadernillo.html
    armar-pdf.js       lo imprime a PDF con los hipervínculos vivos

Para rehacerlo:

    python3 fuentes/ets/verificar.py && \
    python3 fuentes/ets/armar-html.py && \
    NODE_PATH=$PWD/node_modules node fuentes/ets/armar-pdf.js

Sale `ETS-Geometria-y-Trigonometria-practica.pdf` en la raíz.

## Por qué está armado por tipos y no por examen

Comparando los ocho exámenes, los **números** cambian año con año pero los **tipos
de problema son casi los mismos**. El de sombras y el de paralelas cortadas por una
secante aparecen en los ocho; el de Pitágoras con lados en $x$, el de polígonos y el
de ecuaciones trigonométricas, en casi todos. Practicar por tipo rinde mucho más que
resolver los ocho exámenes completos.

## Por qué las respuestas se calculan y no se escriben

Escribir 184 respuestas a mano es la forma segura de colar tres o cuatro mal. Aquí
`generar.py` despeja cada ejercicio con su fórmula y `verificar.py` hace lo contrario:
toma el número que va a leer el alumno y lo **sustituye en la ecuación original** para
ver si la cumple. Son dos caminos distintos, así que un error tendría que aparecer en
los dos a la vez y de la misma forma.

Además comprueba cosas que no son "¿da el mismo número?": que los polígonos den un
número entero de lados, que los triángulos cumplan la desigualdad triangular, que las
ecuaciones logarítmicas no dejen argumentos negativos, que las trigonométricas traigan
**todas** las soluciones del intervalo (el error clásico de dividir entre $\mathrm{sen}\,\theta$
y perder la mitad), y que no quede LaTeX sin cerrar. Son 916 comprobaciones.

Los parámetros de cada bloque viven en constantes al principio de `generar.py` y
`verificar.py` las importa de ahí. No es un detalle de estilo: cuando cada archivo
tenía su copia, se desincronizaron y un ejercicio salió con la diagonal equivocada.

## Un reactivo que viene mal en la guía

El bloque R incluye la identidad
$\dfrac{\tan\theta\cos\theta}{\mathrm{sen}\,\theta} = \sec\theta\cot\theta$ tal como
aparece en los ETS de 2019 y 2025. **No es identidad**: el lado izquierdo vale 1 y el
derecho vale $\csc\theta$, así que solo coinciden en $\theta = 90^\circ$. La respuesta
lo dice y explica qué contestar si se lo ponen.
