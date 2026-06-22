# Implementar · "Tu mapa" — bento de dominio (home Tercial)

Vista de progreso del alumno en formato **bento / treemap** (como un mapa de
calor de finanzas). Pensada como home (o sección destacada) de Tercial: el
alumno la abre y sabe en segundos **dónde está parado y qué hacer hoy**.

- **Mockup de referencia (fuente de verdad visual):** `referencia/Mapa Tercial.dc.html`
- Identidad: Editorial cálido funcional (Fraunces / IBM Plex, crema-coñac).
- Estados de color = los mismos del dashboard apagado+señales.

> Este documento es exhaustivo a propósito: si alguien pregunta "¿qué significa
> ▲ +6 sem.?" o "¿por qué Matemáticas es el azulejo más grande?", la respuesta
> está aquí. Léelo completo antes de implementar.

---

## 1. Concepto: un mapa de dos niveles (zoom)

Es **una sola idea vista a dos escalas**. No son dos pantallas en paralelo: la
segunda es el *drill-down* de la primera.

| Nivel | Pantalla | Cada azulejo es… | El **tamaño** del azulejo = | El **color** = | El **número grande** = |
|---|---|---|---|---|---|
| 1 | **Materias** | una materia (Física, Matemáticas…) | **nº de subtemas** que abarca esa materia | tu dominio de la materia | tu % de dominio |
| 2 | **Temas** (de una materia) | un tema (Termodinámica, Óptica…) | **peso en el examen** (nº de reactivos del tema) | tu dominio del tema | tu % de dominio |

**Interacción:** el alumno toca una materia en el nivel 1 → entra al nivel 2 de
esa materia. Un "← Examen" arriba regresa al nivel 1. **Esa transición la
implementas tú** (mostrar/ocultar, ruteo, o animación); el diseño entrega las
dos pantallas como estados. En el mockup se muestran lado a lado solo para
revisarlas juntas — en producción se ve **una a la vez**.

### ¿Por qué el tamaño cambia de significado entre niveles?

Es intencional y responde a la pregunta útil de cada nivel:

- **Nivel 1 (materias):** "¿cuánto territorio tengo que cubrir en cada materia?"
  → el tamaño = nº de subtemas (amplitud del temario). Por eso **Matemáticas**
  (9 subtemas) es el bloque más grande y **Razon. verbal** (4 subtemas) es chico.
- **Nivel 2 (temas):** "¿qué tanto pesa este tema en mi calificación?" → el
  tamaño = nº de reactivos que caen de ese tema en el examen. Por eso
  **Termodinámica** (18 reactivos) domina el grid de Física.

> Tensión deliberada que el diseño deja ver: en el nivel 1, **Razon. verbal** y
> **Razon. matemático** tienen pocos subtemas (azulejo chico) PERO 16 preguntas
> cada uno (las que más pesan del examen). Por eso esos dos azulejos muestran el
> dato extra **"4 · 16 preg"**: 4 subtemas, 16 preguntas. Así el alumno no cree
> que son irrelevantes solo porque el azulejo es pequeño. Es información honesta,
> no un bug.

---

## 2. Escala de color (idéntica al dashboard apagado+señales)

El color del azulejo sale del % de dominio del alumno en ese tema/materia:

| Estado | Umbral | Claro (fondo) | Claro (texto) | Oscuro (fondo) | Oscuro (texto) |
|---|---|---|---|---|---|
| Dominas | ≥ 70% | `#4a6b3f` | `#fff` / `#cdddbf` | `#45663a` | `#fff` / `#bccfae` |
| En proceso | 50–69% | `#e6a829` | `#3a2c08` / `#5a4410` | `#d4a04a` | `#241b06` / `#4a3608` |
| A reforzar | < 50% | `#9c3525` | `#fff` / `#f1d3ca` | `#c25a44` | `#fff` / `#f1d9cf` |
| Sin empezar | sin datos | `#e6dcc4` | `#8c7556` / `#a89880` | `#3a3229` | `#a89880` / `#8a7861` |

Regla JS de color de fondo:
```js
function tileBg(pct, dark) {
  if (pct == null)  return dark ? '#3a3229' : '#e6dcc4'; // sin empezar
  if (pct >= 70)    return dark ? '#45663a' : '#4a6b3f'; // dominas
  if (pct >= 50)    return dark ? '#d4a04a' : '#e6a829'; // en proceso
  return                 dark ? '#c25a44' : '#9c3525';   // a reforzar
}
// Texto: sobre ámbar usa tinta oscura (#3a2c08 claro / #241b06 oscuro);
// sobre verde/terracota usa blanco. Sobre "sin empezar" usa gris cálido.
```

---

## 3. Las 4 señales de valor (qué son, qué significan, su objetivo)

Estas se agregaron para que el mapa no solo **diagnostique** sino que **mueva a
la acción**, sin saturar (criterio minimalista del proyecto: *reemplazar texto
existente, no añadir cajas de explicación*). Viven en la pantalla de **temas**
(nivel 2), en el azulejo de máxima prioridad y en el encabezado.

### 3.1 · Acción directa — botón "Practicar 10 reactivos →"
- **Qué es:** un CTA dentro del azulejo rojo de mayor prioridad (Termodinámica),
  en lugar de una descripción pasiva.
- **Significa:** "empieza a practicar este tema ahora mismo, con N reactivos."
- **Objetivo:** cerrar el ciclo *ver que voy mal → hacer algo*. El mapa
  diagnostica; el botón convierte el diagnóstico en un clic. El "10" es el
  tamaño de sesión sugerido (ajústalo a tu lógica de práctica).
- **Implementación:** enlaza al flujo de práctica del tema
  (`/practicar/{materia}/{tema}?n=10` o equivalente). El número puede ser fijo
  (10) o calculado.

### 3.2 · "Empieza aquí" (badge) + cuál es la prioridad
- **Qué es:** etiqueta en el azulejo prioritario.
- **Significa:** "de todo tu examen, este es el mejor lugar para invertir tu
  tiempo **hoy**."
- **Cómo se elige la prioridad (regla recomendada):** el tema que maximiza
  *impacto* = combinación de **peso en examen** (reactivos) × **qué tan bajo
  vas** (100 − %). Es decir: importante **y** débil. En el ejemplo,
  Termodinámica (18 reactivos, 42%) gana. Si prefieres algo más simple: el tema
  de menor % entre los de mayor peso. **Solo un azulejo** lleva este badge.

### 3.3 · Proyección de puntaje — "Faltan 6 días — subir Termodinámica suma ~5 aciertos"
- **Qué es:** una sola línea de texto bajo el título de la pantalla.
- **Significa:** dos cosas unidas — (a) **cuántos días faltan** para el examen
  del alumno (viene del mismo dato que el contador de la home / el comprobante),
  y (b) **cuántos aciertos ganaría** si sube el tema prioritario a un nivel meta.
- **Objetivo:** darle urgencia y propósito al mapa. Deja de ser una foto del
  estado y se vuelve una **palanca**: "si haces esto, en los días que te quedan,
  tu calificación sube esto."
- **Cómo se calcula "~5 aciertos":**
  ```
  aciertos_ganables = reactivos_del_tema × (pct_meta − pct_actual)
  // ejemplo Termodinámica: 18 × (70% − 42%) = 18 × 0.28 ≈ 5 aciertos
  ```
  `pct_meta` = el umbral de "dominas" (70%) por defecto. Redondea y antepón "~".
  Los "6 días" salen de `fechaExamen − hoy` (mismo origen que el contador).

### 3.4 · Tendencia — "▲ +6 sem."
- **Qué es:** micro-indicador en la esquina superior del azulejo prioritario.
- **Significa textualmente:** "tu dominio de este tema **subió 6 puntos
  porcentuales en la última semana**" (▲ = subió; sería ▼ y color de alerta si
  bajó). "sem." = *esta semana* / *vs. semana pasada*.
- **Objetivo:** motivación. Un mapa de dominio engancha mucho más cuando muestra
  **movimiento**, no solo estado. Un alumno en 42% solo ve rojo; con "▲ +6 sem."
  ve "rojo, pero avanzando" — y eso sostiene el hábito.
- **Cómo se calcula:** `pct_actual − pct_hace_7_dias` (en puntos porcentuales,
  no relativo). Si no hay snapshot de hace una semana, **oculta la señal** (no
  muestres "+0"). Se pone **solo en el azulejo prioritario** a propósito: ponerlo
  en todos satura y rompe el minimalismo. Si más adelante lo quieres en más
  azulejos, úsalo como glifo direccional pequeño sin número.

### 3.5 · Cobertura — "8 de 11 temas vistos"
- **Qué es:** reemplaza al subtítulo "7 temas" en el eyebrow de la pantalla.
- **Significa:** "has trabajado 8 de los 11 temas de esta materia" (los 3
  restantes están en estado *sin empezar* — los azulejos crema/grafito).
- **Objetivo:** empujar a cerrar el temario. Los azulejos "sin empezar" son
  **deuda silenciosa**; este contador la hace visible sin regañar.
- **Cómo se calcula:** `temas_con_algún_intento / temas_totales_de_la_materia`.

---

## 4. Estructura HTML/CSS (cópiala del mockup)

El grid es CSS puro, sin librerías. Clases base (únicas que el componente usa):

```css
.bento { display:grid; grid-template-columns:repeat(4,1fr); grid-auto-rows:82px; gap:9px; grid-auto-flow:dense; }
.tile  { border-radius:9px; padding:11px 13px; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; position:relative; }
.tile .pct { font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums; line-height:1; }
.tile .nm  { line-height:1.12; }
```

- **Tamaño de azulejo = spans de grid.** `grid-column:span N` y `grid-row:span M`
  sobre la celda base de 82px. Mapea el "tamaño" (subtemas o reactivos) a un span:
  - muy grande / prioridad → `span 2` × `span 2` (2×2)
  - grande → `span 2` (2×1) o `span 1`×`span 2` (1×2, vertical)
  - normal → 1×1
- `grid-auto-flow:dense` rellena huecos automáticamente. **Ordena los azulejos
  de mayor a menor tamaño** en el HTML para un empaque limpio (en el mockup:
  Matemáticas 2×2 → Física 1×2 → dos 1×1 → dos 2×1 → cuatro 1×1).
- La materia con la que se hace *drill-down* (Física) lleva un `outline` de 1.5px
  (`#1f1a16` claro / `#efe4cf` oscuro) + el texto "ver temas →" para señalar que
  es navegable.

> Sugerencia de mapeo tamaño→span (nivel 1, por subtemas), para que sea
> determinista en código:
> ```js
> function spanForSubtemas(n) {
>   if (n >= 9) return {c:2, r:2};
>   if (n >= 7) return {c:1, r:2};   // alto
>   if (n >= 8) return {c:2, r:1};   // ancho (ajusta a tu gusto)
>   return {c:1, r:1};
> }
> ```
> No tiene que ser exacto como un treemap matemático; es un bento (rejilla), la
> proporción es aproximada y prioriza que se vea ordenado.

---

## 5. Datos de ejemplo usados en el mockup (alumna "Sofía", examen ECOEMS)

Para que reconozcas de dónde sale cada número del mockup. Son datos de ejemplo;
en producción vienen del progreso real del alumno (los mismos que alimentan el
dashboard y el comprobante).

**Nivel 1 · materias** (`% dominio · subtemas · preguntas en examen`):
| Materia | % | Subtemas (tamaño) | Preguntas |
|---|---|---|---|
| Matemáticas | 75 | 9 (2×2) | 12 |
| Física | 71 | 7 (1×2, navegable) | 12 |
| Química | 75 | 7 | 12 |
| Biología | 67 | 8 (2×1) | 12 |
| Español | 67 | 8 (2×1) | 12 |
| Historia | 58 | 7 | 12 |
| Geografía | 75 | 6 | 12 |
| F. cívica y ética | 75 | 5 | 12 |
| Razon. verbal | 81 | 4 | **16** |
| Razon. matemático | 63 | 4 | **16** |

**Nivel 2 · temas de Física** (`% dominio · reactivos = tamaño`):
| Tema | % | Reactivos |
|---|---|---|
| Termodinámica | 42 | 18 (2×2, prioridad) |
| Física moderna | 48 | 12 (2×1) |
| Electromagnetismo | 79 | 14 (1×2) |
| Cinemática | 88 | — |
| Dinámica | 82 | — |
| Trabajo y energía | 76 | — |
| Óptica | 73 | — |
| Mov. ondulatorio | 64 | — |
| Ondas | 61 | — |
| Fluidos | 58 | — |
| Magnetismo | sin empezar | — |

Dominio global (71%) = promedio ponderado por reactivos. "8 de 11 temas vistos" =
10 con dato + Magnetismo sin empezar → ajusta a tu conteo real (el mockup usa 11
temas, Magnetismo sin empezar).

---

## 6. Resumen de objetivos (para responder "¿por qué está esto aquí?")

- **Bento en vez de cuadrícula uniforme:** la jerarquía visual *es* la jerarquía
  de estudio — lo grande+rojo grita "prioridad", lo chico+verde se ignora solo.
- **Dos niveles:** el alumno entra por lo general ("¿cómo voy?") y baja a lo
  accionable ("¿qué tema toco?").
- **Las 4 señales:** convierten un diagnóstico bonito en un entrenador — qué
  hacer (3.1), dónde (3.2), por qué urge (3.3), que vas avanzando (3.4) y qué
  falta por cubrir (3.5).
- **Minimalismo:** cada señal **reemplazó** algo que ya estaba (descripción →
  botón, "7 temas" → cobertura) o es un glifo de pocos caracteres. Cero texto de
  ayuda en pantalla. Toda la explicación vive en este documento, no en la UI.
