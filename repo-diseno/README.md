# Diseño del comprobante ECOEMS — paquete para el repo

Identidad: **Editorial cálido funcional** (Fraunces / IBM Plex Sans / IBM Plex Mono,
crema-coñac-terracota). Todo reusa tus tokens y se integra a `server.js`.

> ## ⚠ Decisión tomada — NO volver a preguntar
> El dashboard va en **apagado + señales** (paleta cálida apagada, flechas
> ⬆/guión/⬇, etiquetas de estado, agrupación, acento **coñac**, sin azul).
> El tratamiento **"vivo" está descartado**. La fuente de verdad visual es
> **`referencia/Dashboard Tercial Completo.dc.html`**. Los mockups que muestran
> "vivo vs apagado" son solo el historial de la decisión.

## Qué hay aquí

| Archivo | Qué es | A dónde va en el repo |
|---|---|---|
| `IMPLEMENTAR-portada-pdf.md` | Guía paste-ready: **portada del PDF** (número editorial + materias + tarjetas) | Reemplaza `score-block` + `breakdown` en `buildComprobanteHTML()` |
| `IMPLEMENTAR-preguntas-pdf.md` | Guía paste-ready: rediseño de la **sección de reactivos** del comprobante **y** de la **clave de respuestas** | Se aplica sobre `buildComprobanteHTML()` y `buildAnswerKeyHTML()` en `server.js` |
| `comprobante-telegram.js` | Tarjeta **corta** del comprobante (código `buildPortadaCortaHTML`) + envío por **Telegram** (imagen PNG) | Cópialo a la raíz del repo (junto a `server.js`) y requiérelo desde ahí |
| `IMPLEMENTAR-dashboard-colores.md` | Guía paste-ready: legibilidad de colores del **dashboard académico** (apagados Tercial + señales redundantes) | Se aplica sobre `dashboard-academico.html` |
| `IMPLEMENTAR-dashboard-tercial.md` | Guía paste-ready: andamiaje para llevar el **dashboard al look Tercial** (fuentes, tarjetas crema, métricas, Chart.js) | Se aplica sobre `dashboard-academico.html` (+ el doc de colores) |
| `IMPLEMENTAR-mapa-bento.md` | Guía paste-ready + **explicación a detalle** del **"Tu mapa"** bento de dominio (2 niveles, escala de color, las 4 señales: acción / proyección / tendencia / cobertura). Responde cualquier "¿qué significa X?" | Home (o sección) de Tercial — vista nueva |
| `referencia/Mapa Tercial.dc.html` | **Mockup final del mapa bento** — dos pantallas (materias → temas), claro y oscuro, con las 4 señales. **Fuente de verdad.** | Solo referencia de diseño |
| `referencia/Dashboard Tercial Completo.dc.html` | **Mockup final del dashboard** — apagado+señales completo (radares, mapa de calor, detalle por pregunta). **Fuente de verdad.** | Solo referencia de diseño |
| `referencia/Dashboard Tercial.dc.html` | Mockup *histórico*: comparación vivo vs apagado (vivo descartado) | Solo referencia |
| `referencia/Portada Comprobante.dc.html` | Mockup visual: portada corta (Telegram) + completa (PDF) | Solo referencia de diseño (no va a producción) |
| `referencia/Preguntas PDF.dc.html` | Mockup visual: reactivos y clave — *Actual vs Propuesta* | Solo referencia de diseño |
| `referencia/Dashboard Colores.dc.html` | Mockup *histórico*: barras — vivo / apagado solo color / apagado+señales (decisión) | Solo referencia |

## Orden sugerido de implementación

1. **Portada del PDF** → `IMPLEMENTAR-portada-pdf.md` (CSS `p-*` + bloque
   `portadaHTML` que reemplaza `score-block` + `breakdown`).
2. **Reactivos del comprobante** → `IMPLEMENTAR-preguntas-pdf.md`, Pasos 1–3
   (CSS nuevo `q-*` en `TERCIAL_PDF_CSS`, render por materia con glifo ✓/✗ y
   kicker, y quitar el `<ol>` del template).
3. **Clave de respuestas** → mismo archivo, Pasos 4–5 (reusa las clases `q-*`,
   marca solo la correcta).
4. **(Opcional) limpieza** → borra las clases viejas `.exam-pdf__*`,
   `.score-block*` y `.breakdown*` cuando ya no las use ningún builder.
5. **Telegram** → `comprobante-telegram.js`: 3 pasos comentados al inicio del
   archivo (require, llamar `sendComprobanteTelegram(room, student, …)` donde hoy
   llamas `enqueueComprobantePDF`, y las env vars `TELEGRAM_BOT_TOKEN` /
   `TELEGRAM_CHAT_ID`). Pendiente de su lado: mapear cada alumno a su `chat_id`.
6. **Dashboard → look Tercial (apagado + señales, DECIDIDO)** sobre
   `dashboard-academico.html`: primero `IMPLEMENTAR-dashboard-tercial.md`
   (Pasos 1–2: fuentes + tarjetas crema + acento coñac), luego
   `IMPLEMENTAR-dashboard-colores.md` completo (paleta apagada + `levelMeta` +
   barras agrupadas), y de vuelta al tercial Pasos 4–7 (Chart.js, radares
   coñac/terracota, mapa de calor, detalle por pregunta). Reproduce
   `referencia/Dashboard Tercial Completo.dc.html`.
7. **"Tu mapa" (bento de dominio)** → `IMPLEMENTAR-mapa-bento.md`. Vista nueva
   para la home. Léelo completo: explica los 2 niveles (materias→temas), la
   escala de color, el mapeo tamaño→span del grid, y las 4 señales de valor con
   su fórmula y objetivo. Reproduce `referencia/Mapa Tercial.dc.html`.

## Notas

- Cero dependencias nuevas (Telegram usa `fetch`/`FormData` global de Node 18+).
- Todo es **aditivo**: las clases `q-*` no chocan con `.exam-pdf__*`, así que
  puedes migrar comprobante y clave sin romper nada intermedio.
- Colores por nivel en tono apagado del sistema, **dirección final** del
  dashboard: domina `#4a6b3f` · en proceso `#e6a829` (texto `#c2891a`) ·
  atención `#9c3525`. El "vivo" quedó descartado.
