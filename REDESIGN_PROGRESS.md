# Rediseño ECOEMS — handoff entre máquinas

Documento para que cualquier IA que tome el trabajo pueda continuar sin contexto previo. Vive en el repo y viaja con git. No es para producción — es coordinación interna.

## Contexto

- **Branch de trabajo**: `dev`. **NUNCA** mergear a `main` sin confirmación explícita del usuario — la Mac mini corre el server en `main` durante exámenes activos y un merge accidental rompería UX a mitad de aplicación.
- **Spec fuente** (autosuficiente, leer entero antes de tocar nada):
  `https://raw.githubusercontent.com/Giledvz/clases/main/design/exporta-ecoems.md`
- **Sistema de diseño**: Editorial cálido funcional v1.0 (Tercial). Crema/coñac/terracota, Fraunces + IBM Plex Sans. Sin sombras (hairlines), italics en headings con accent coñac.
- **Stack ECOEMS**: Node.js + Express + Socket.io + HTML/CSS/JS plano. Estilos en `<style>` inline dentro de `public/index.html` (~2100 líneas).
- **Usuario**: profesor de secundaria, NO desarrollador experto. Pide acompañamiento paso a paso, sobre todo con git (regla guardada en memoria local).

## Etapas

Plan original de 6 etapas, cada una con su commit en `dev`. Entre etapas, pedir visto bueno antes de seguir.

| # | Etapa | Estado | Commits |
|---|---|---|---|
| 1 | Fundamentos (anti-flash, fonts, tokens :root + dark, reset) | ✅ | `3d6cd8b` |
| 2 | Migrar dark mode `body.dark` → `[data-theme="dark"]` + JS toggle | ✅ | `2055c57` |
| 3 | Componentes generales + roomScreen/joinScreen/waitingScreen | ✅ | `7c850d4` |
| 4 | Componentes de examen (status sticky, timer SVG, options) + examScreen | ✅ | en este commit |
| 5 | Limpieza + interacciones — **PENDIENTE** | ⏳ | — |
| 6 | teacher.html + comprobante PDF — **PENDIENTE** | ⏳ | — |

## Lo que se entregó en etapa 4

- `.exam-status` sticky full-width (con timer SVG circular cuyo anillo se vacía con el countdown)
- Barra de progreso lineal debajo (avance de preguntas respondidas)
- `.exam-question` full-width con padding lateral (sin container — pedido explícito del usuario)
- `.exam-question__context` (card crema para lecturas compartidas, borde-izq coñac)
- `.exam-options` con `.exam-option` y 4 estados: default, selected (borde coñac), correct (stripe verde + check), incorrect (stripe rojo + cross), neutral (review)
- `.exam-nav` sticky bottom con botones `.btn--ghost` / `.btn--primary`
- `.exam-grid` con celdas que muestran estado (answered=verde, marked=ámbar) y la actual con box-shadow inset coñac (no outline — evita clip por overflow)
- JS adaptado: `renderQuestion` (estructura nueva de opciones con `<li><button>`), `renderNavGrid` (clases `.is-answered`, `.is-marked`, `.is-current`), `startTimer` (texto compacto + actualiza `stroke-dashoffset` del SVG y agrega `.exam-timer--critical` en últimos 10 min)
- `review-banner` rediseñado en ámbar editorial, `legend-dot` con tokens, `explanation-box` con borde-izq coñac
- Borrado ~25 reglas dark legacy con hex hardcoded (#2c5282, #16213e, etc.)

## Etapa 5 — pendientes anotados durante etapa 4

Cosas que el usuario pidió o que detecté para limpieza:

1. **⌨️ Teclas 1/2/3/4 para seleccionar opciones** (pedido del usuario, fácil con `keydown` listener).
2. **`style=` inline restantes** (~45). Quitar todos y reemplazar por clases o atributos `data-state`.
3. **`onclick=` inline restantes** (~13). Migrar a `addEventListener` en un solo lugar.
4. **Pantalla `resultsScreen`** post-envío: rediseñar con `.card` + `.response--ok/err` + `.tag` para el breakdown de scores por tema. Usa selectores legacy `.topic-breakdown`, `.bar-green/amber/red`, `.divider`.
5. **Overlays** `submit-overlay`, `tab-warn-card`, `cancel-overlay` — refactorizar con tokens (border-top de categoría en lugar de sombras pesadas, color-mix de bg en lugar de rgba negros).
6. **Hex hardcoded restantes** (~80 líneas). El audit final del spec § 12 paso 10 cubre esto.
7. **`#qImage`**: tiene filtro `brightness(0.9)` en dark heredado. Decidir si conservar o migrar a un token de imagen.

## Etapa 6 — pendiente

1. **`public/teacher.html`** (651 líneas) — replicar el sistema completo: tokens, fuentes, componentes. Patrón: usar `.card` para info de salas, `.tag--ok/--warn` para estado de progreso, tabla con `font-variant-numeric: tabular-nums` y hairlines.
2. **Comprobante PDF** — agregar `@media print` con:
   - `body { background-image: none; background-color: #fff; color: #000; }`
   - Esconder `.exam-status`, `.exam-nav`, `.site-nav`
   - Mantener Fraunces para identidad visual
3. **Reglas de print** se aplican al iframe del comprobante (línea ~1700 de index.html, `buildComprobanteHTML`).

## Cómo retomar el trabajo

```bash
# 1. Confirmar máquina y branch
cd ~/ECOEMS                    # o donde esté el repo
git fetch
git checkout dev
git pull
git branch --show-current      # debe decir "dev"

# 2. Arrancar server localmente (NO en Mac mini si la Mac mini es producción)
node server.js

# 3. Probar
open http://localhost:3000/?review=1
```

## Reglas de oro para esta migración

1. **Cero merges a main** sin pedirle al usuario que confirme explícitamente.
2. **Una etapa por commit**, mensaje claro tipo `Etapa N/6 rediseño: ...`.
3. **Pedir luz verde entre etapas**. El usuario eligió cadencia "etapa por etapa con visto bueno".
4. **No tocar la lógica del examen** (socket events, save state, submit flow). Solo CSS + HTML estructural + ajustes mínimos de JS para clases nuevas.
5. **Lecturas compartidas** (regla heredada): si un bloque de preguntas comparte una lectura, el `context` debe estar en cada pregunta del bloque, no solo en la primera.
6. **Fuentes blacklist** del spec (cero Lora, DM Sans, Georgia, Arial, Helvetica, Inter, Roboto, system-ui). Solo Fraunces + IBM Plex.
7. **Cero hex hardcoded** — todo color pasa por tokens semánticos. Si falta uno, agregarlo primero a tokens.

## Memoria local importante

Estas viven en `/Users/giledvz/.claude/projects/-Users-giledvz-ECOEMS/memory/` (NO viajan con git, son por máquina). Reglas relevantes ya guardadas en la máquina anterior:

- `feedback-lecturas-arriba.md` — duplicar contexto en cada pregunta del bloque
- `feedback-checklist-post-examen.md` — qué revisar después de cada aplicación
- `feedback-git-guia-paso-a-paso.md` — acompañar al usuario en operaciones git
