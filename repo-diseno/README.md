# Diseño del comprobante ECOEMS — paquete para el repo

Identidad: **Editorial cálido funcional** (Fraunces / IBM Plex Sans / IBM Plex Mono,
crema-coñac-terracota). Todo reusa tus tokens y se integra a `server.js`.

## Qué hay aquí

| Archivo | Qué es | A dónde va en el repo |
|---|---|---|
| `IMPLEMENTAR-portada-pdf.md` | Guía paste-ready: **portada del PDF** (número editorial + materias + tarjetas) | Reemplaza `score-block` + `breakdown` en `buildComprobanteHTML()` |
| `IMPLEMENTAR-preguntas-pdf.md` | Guía paste-ready: rediseño de la **sección de reactivos** del comprobante **y** de la **clave de respuestas** | Se aplica sobre `buildComprobanteHTML()` y `buildAnswerKeyHTML()` en `server.js` |
| `comprobante-telegram.js` | Tarjeta **corta** del comprobante (código `buildPortadaCortaHTML`) + envío por **Telegram** (imagen PNG) | Cópialo a la raíz del repo (junto a `server.js`) y requiérelo desde ahí |
| `referencia/Portada Comprobante.dc.html` | Mockup visual: portada corta (Telegram) + completa (PDF) | Solo referencia de diseño (no va a producción) |
| `referencia/Preguntas PDF.dc.html` | Mockup visual: reactivos y clave — *Actual vs Propuesta* | Solo referencia de diseño |

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

## Notas

- Cero dependencias nuevas (Telegram usa `fetch`/`FormData` global de Node 18+).
- Todo es **aditivo**: las clases `q-*` no chocan con `.exam-pdf__*`, así que
  puedes migrar comprobante y clave sin romper nada intermedio.
- Colores por nivel en tono apagado del sistema (`#4a6b3f` / `#8a5208` / `#9c3525`).
  Si prefieres los vivos de tus dashboards, cambia esos 3 hex.
