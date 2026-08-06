# Explicaciones

Lo que el alumno lee al terminar el examen: por qué la respuesta correcta es la
correcta, y con qué error se llega al distractor que se antoja. Las escribe el
modelo **Fable**, que es el más pesado; ahí no se ahorra.

## La tubería

    1. preparar-lotes.py    parte en lotes lo que no tiene explicación
    2. workflow-explicaciones.js   un agente Fable por lote
    3. fusionar.py          valida y las mete en los exámenes

Corrida completa para un grupo de exámenes:

    python3 fuentes/explicaciones/preparar-lotes.py unam     # ipn | ecoems | diagnosticos | todos

Eso deja los lotes en `lotes/`. Después, desde Claude Code:

    Workflow({scriptPath: 'fuentes/explicaciones/workflow-explicaciones.js',
              args: ['unam-a1-5__g01', 'unam-a1-5__g02', …]})

Cada agente escribe su archivo en `salida/`. Al terminar:

    python3 fuentes/explicaciones/fusionar.py --dry    # revisa y reporta
    python3 fuentes/explicaciones/fusionar.py          # escribe los exámenes

`--dry` primero, siempre. Y **lee lo que reporta antes de comitear**.

## Carpetas

| | |
|---|---|
| `lotes/` | Entrada: reactivos con enunciado, opciones y clave |
| `salida/` | Lo que escribió cada agente |
| `lotes-en-espera/` | Lotes que **no** hay que correr todavía |
| `revisar.md` | Reactivos donde el modelo no coincidió con la clave oficial |

En `lotes-en-espera/` están hoy los de `ecoems-4` y `ecoems-5`: sus figuras siguen
siendo marcadores de texto (`[Imagen: …]`), y explicar un reactivo cuya figura no
existe da explicaciones malas. Se corren cuando estén las figuras.

## Las notas REVISAR

Al modelo se le dice que la clave oficial se asume correcta, pero que si al
resolver le da otra cosa lo diga en un renglón que empiece con `REVISAR:`.

`fusionar.py` recorta esos renglones —**el alumno nunca los ve**— y los junta en
`revisar.md`. Hoy hay 90, y varios son erratas reales de las guías. Ese archivo es
para revisar a mano, no para creerle a ciegas.

## Qué valida fusionar.py

De forma determinista, sobre todos los lotes juntos:

- que el JSON sea válido y los ids sean los del lote;
- que ningún examen quede con reactivos sin explicación;
- que no haya etiquetas HTML fuera de las que el renderizador entiende;
- que el LaTeX no quede sin cerrar;
- que ninguna empiece con "la respuesta correcta es" (el alumno ya la ve marcada);
- que ninguna se pase de largo.

Dos detalles que costaron falsos positivos: una etiqueta HTML de verdad **cierra
con `>`** (si no, `$Sc<Be<Cr<As<Cl$` se lee como cuatro etiquetas), y al contar
signos de pesos hay que descontar los `\$` de dinero.

## Sobre el costo

La primera corrida salió en 12 104 tokens por explicación. Hoy va en **~1 040**,
sin tocar la calidad del prompt. Lo que sirvió, en orden de impacto:

- **Quitarle la autovalidación al agente.** Volvía a abrir su archivo y a contar;
  cada turno rearrastra todo el contexto. Y era peor que `fusionar.py`, que revisa
  el conjunto entero de forma determinista.
- **Prohibirle Bash.** Escribir con heredoc costaba el doble que `Write`.
- **Quitar el StructuredOutput**, que costaba un turno más.
- **Deduplicar las lecturas compartidas**: en los IPN, el 84% del texto era la
  misma lectura repetida en cada pregunta, y ese peso se relee en cada turno.
- **Lotes grandes** (40 reactivos): el costo lo domina el arranque del agente, no
  el tamaño del contexto.

Quedan ~3 turnos por agente: leer el lote, escribir la salida, responder.
