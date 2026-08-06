# Correcciones a las guías oficiales

Reactivos donde la guía oficial está mal y lo corregimos a conciencia. Cada
entrada trae su motivo: **si no se puede justificar, no se corrige.** La clave
oficial se asume correcta mientras no haya una razón sólida en contra.

De dónde salen: al escribir las explicaciones, el modelo resuelve cada reactivo
por su cuenta y marca los que no le cuadran con la clave. Esas notas se juntan en
[fuentes/explicaciones/revisar.md](fuentes/explicaciones/revisar.md) —hoy hay 87—
y de ahí se revisan a mano. Lo de este documento es lo que ya se revisó y se
decidió cambiar.

Los reactivos corregidos llevan un campo `_correccion` dentro del propio JSON,
con el motivo. Es un campo interno: **el alumno nunca lo ve**. Y su explicación
se reescribe, porque la vieja explicaba la clave equivocada.

---

## unam-a1-1 · id 76 — Ingeniería genética

**Clave oficial B → A.**

> Al conjunto de técnicas que hacen posible el aislamiento, estudio, modificación
> y transferencia de genes de un organismo a otro se le llama…
>
> A) ingeniería genética  ·  B) recombinación genética  ·  C) proyecto genoma  ·
> D) terapia génica

La definición del enunciado es la de **ingeniería genética**. La recombinación
genética designa el intercambio natural de material genético en la meiosis, no un
conjunto de técnicas de laboratorio. Además, el propio reactivo declara su tema
como "Ingeniería genética": la guía se contradice sola.

Óscar contestó A y se le contó como error.

## unam-a2-1 · id 71 — Ciclo de Krebs

**Clave oficial D → A.**

> De la glucólisis se producen 2 moléculas de ácido pirúvico, las cuales deben ser
> transformadas químicamente a ______ para ingresar al ciclo de Krebs.
>
> A) acetil-CoA  ·  B) NADH  ·  C) FADH₂  ·  D) ácido oxalacético

El piruvato se convierte en **acetil-CoA** por descarboxilación oxidativa antes de
entrar al ciclo. El oxalacetato es el aceptor de cuatro carbonos que ya circula
dentro del ciclo y se condensa con el acetil-CoA para formar citrato; no proviene
del piruvato en ese paso.

Lupita contestó A y se le contó como error.

## unam-a1-2 · id 51 — Ecuaciones e identidades

**No era la clave: era el reactivo.** Se cambió la opción B.

> Selecciona la expresión que corresponde a una ecuación.
>
> A) sen(x) = ½  ·  ~~B) sen(x) = ½x~~ → **1 + cot²(x) = csc²(x)**  ·
> C) sen²(x) + cos²(x) = 1  ·  D) sec²(x) − tan²(x) = 1

Tal como venía, había **dos** ecuaciones: la clave A y también la B, que es una
igualdad condicional (se cumple en x = 0 y en otros dos puntos). Se sustituyó B
por una identidad pitagórica para que quede una sola respuesta correcta.

Óscar y Dana eligieron B y se les contó como error.

## unam-a1-5 · id 2 — Suma de vectores

Vive aparte, en
[fuentes/unam-2025/claves/correcciones.json](fuentes/unam-2025/claves/correcciones.json),
porque ese examen sí lo arma un script y la corrección tiene que aplicarse cada
vez que se rearma. Resumen: la clave marca √101.1, un valor al que no se llega de
ninguna manera —probadas las 192 combinaciones de cuadrante y eje de referencia
con la tabla de la propia guía—, y el único alcanzable es √75.8.

---

## Calificaciones afectadas

| Alumno | Examen | Antes | Después |
|---|---|---|---|
| Óscar | unam-a1-1 (sala FELK22) | 81/120 | **82/120** |
| Óscar | unam-a1-1 (sala CYQLMZ) | 102/120 | **103/120** |
| Óscar | unam-a1-2 (sala HX6U2K) | 100/120 | **101/120** |
| Dana | unam-a1-2 (sala HX6U2K) | 81/120 | **82/120** |
| Lupita | unam-a2-1 (sala M867NQ) | 84/120 | **85/120** |

Los CSV ya guardados **no se reescriben**: son el registro de lo que pasó ese día.
Para recalcular con las claves corregidas, `fuentes/scripts/temas-flojos.py` lee
siempre los JSON vigentes.

## Un caso que NO se corrigió

`unam-a1-2` id 68, definición de derivada. El modelo señaló —con razón— que la
opción D, el cociente "hacia atrás", también converge a f'(3) = 27, así que el
reactivo tiene dos respuestas válidas.

No se tocó porque **ningún alumno eligió la D**: los tres pusieron B (que da −27)
o C (que diverge). Ahí el defecto del reactivo no le costó aciertos a nadie, y ese
tema sí hay que estudiarlo. Queda anotado por si en una aplicación futura alguien
elige la D.
