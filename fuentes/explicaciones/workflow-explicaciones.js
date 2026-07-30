// Escribe con Fable las explicaciones de un grupo de lotes.
//
// Se invoca con Workflow({scriptPath: este archivo, args: ["lote-a", "lote-b", ...]}).
// Los nombres de lote son los archivos de fuentes/explicaciones/lotes/ sin .json.
//
// Diseño pensado para gastar poco SIN bajar la calidad. En la primera corrida cada
// agente daba 11-14 turnos y el 95% del gasto se fue en releer el contexto acumulado,
// no en escribir. Lo que se quitó:
//
//   - La autovalidación del agente ("vuelve a abrir tu archivo y comprueba…"). Era un
//     Read completo más uno o dos Bash, cada uno arrastrando todo el contexto. Y era
//     redundante: fusionar.py valida JSON, ids, vacíos, HTML y LaTeX de forma
//     determinista sobre el conjunto entero, que es más confiable.
//   - El StructuredOutput, que costaba un turno más. Las notas REVISAR: van dentro de
//     la explicación y fusionar.py las recorta y las junta en revisar.md.
//   - La lectura compartida repetida en cada pregunta (ver preparar-lotes.py).
//
// Quedan ~3 turnos por agente: leer el lote, escribir la salida, responder.

export const meta = {
  name: 'explicaciones-fable',
  description: 'Escribe con Fable las explicaciones de un grupo de lotes',
  phases: [{ title: 'Explicar', detail: 'un agente Fable por lote' }],
}

const DIR = '/Users/giledvz/Documents/ECOEMS/fuentes/explicaciones'
const LOTES = Array.isArray(args) ? args : []

const ESTILO = `
CÓMO DEBE SER CADA EXPLICACIÓN (este patrón ya lo aprobó el profesor, respétalo):

- En español de México, tuteando al alumno, tono de profesor que explica en el
  pizarrón: directo y cálido, sin ser condescendiente.
- Explica POR QUÉ la respuesta correcta es correcta. Si el reactivo se resuelve con
  un procedimiento (una sucesión, un cálculo, una regla gramatical), muestra el
  procedimiento paso a paso, no solo el resultado.
- Cuando haya un distractor que se antoja mucho, cierra diciendo en una línea por qué
  NO es, y si se puede, qué error lleva a él ("si te dio 799, calculaste $a_{19}$").
  No hace falta desmenuzar las cuatro opciones.
- Extensión: de 2 a 5 renglones para los de definición; hasta 8 si hay desarrollo
  matemático. Que se pueda leer de un vistazo.
- Matemáticas en LaTeX entre signos de pesos: $a_n = 2n^2+4n+1$. Para una fórmula en
  renglón aparte usa $$...$$. Usa \\mathrm{sen} para seno, nunca \\sin. Un signo de
  pesos de dinero se escribe \\\\$.
- NO uses etiquetas HTML de ningún tipo (nada de <sup>, <br>, <span>, <p>). El
  renderizador solo entiende **negritas**, *cursivas*, saltos de línea y LaTeX;
  cualquier otra etiqueta sale literal en pantalla y se ve como un error.
- No empieces con "La respuesta correcta es..." — el alumno ya la ve marcada en
  pantalla. Entra directo a la explicación.
- No inventes datos, no cites fuentes, no te dirijas al profesor.

EJEMPLO del tono buscado (reactivo de sucesiones, clave 881):

  Fíjate en cómo crece la sucesión: las diferencias entre términos consecutivos son
  $10, 14, 18, 22, \\ldots$ y aumentan de 4 en 4. Cuando las segundas diferencias son
  constantes, el término general es cuadrático, con coeficiente principal
  $4 \\div 2 = 2$. Propones $a_n = 2n^2 + bn + c$ y con los primeros términos
  ($a_1 = 7$, $a_2 = 17$) obtienes $b = 4$ y $c = 1$:

  $$a_n = 2n^2 + 4n + 1$$

  Comprueba con uno de la lista: $a_3 = 18 + 12 + 1 = 31$. Ya con la fórmula,
  $a_{20} = 2(400) + 80 + 1 = 881$.

  Si te dio 799 (opción B), calculaste $a_{19}$: el clásico error de quedarse un
  término corto.

SOBRE LA CLAVE: el campo "clave" de cada pregunta es la respuesta oficial de la guía
y se asume correcta. Si al resolverlo te da otra cosa, NO acomodes la explicación
para forzar la clave. Escribe la explicación de la clave oficial y agrega al final,
en un renglón aparte que empiece exactamente con "REVISAR:", en qué no coincides.
Ese renglón se recorta después y nunca lo ve el alumno; sirve para cazar erratas.

SI LA PREGUNTA TRAE "lectura", el lote incluye un diccionario "lecturas" con el texto
bajo esa clave. La explicación debe apoyarse en él: señala dónde está la evidencia.

SI TRAE "figura" o "figuras_opciones" (rutas a archivos SVG), ábrelas con Read —son
SVG, o sea código que puedes leer— para entender qué muestran antes de explicar.`

phase('Explicar')

const resultados = await pipeline(
  LOTES,
  (lote) => agent(
    `Eres profesor de preparación para examen de admisión. Vas a escribir las
explicaciones que un alumno lee DESPUÉS de entregar su examen, cuando revisa sus
respuestas y quiere entender en qué se equivocó.

Lee este archivo, que trae un lote de reactivos con su enunciado, sus cuatro opciones
y la clave correcta:

  ${DIR}/lotes/${lote}.json

Escribe una explicación para CADA pregunta del lote, sin omitir ninguna.

${ESTILO}

Escribe el resultado con Write en:

  ${DIR}/salida/${lote}.json

Con esta forma exacta, JSON válido y nada más — un objeto por pregunta, en el mismo
orden y con el mismo "id":

[ { "id": 1, "explanation": "..." }, { "id": 2, "explanation": "..." } ]

IMPORTANTE PARA NO GASTAR DE MÁS: después de escribir el archivo, TERMINA. No lo
vuelvas a abrir, no lo valides, no corras Bash para revisarlo, no resumas lo que
hiciste. De validar el JSON, los ids, los vacíos y el HTML se encarga otro proceso
determinista que corre sobre todos los lotes juntos. Tu único trabajo es escribir
buenas explicaciones y guardarlas.

Responde con una sola línea: cuántas escribiste.`,
    { label: lote.replace(/__/g, ' · '), phase: 'Explicar', model: 'fable' }
  )
)

const ok = resultados.filter(Boolean)
log(`${ok.length}/${LOTES.length} lotes terminados`)
return {
  lotes_ok: ok.length,
  lotes_totales: LOTES.length,
  fallidos: LOTES.filter((l, i) => !resultados[i]),
}
