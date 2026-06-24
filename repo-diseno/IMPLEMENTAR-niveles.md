# Implementar · separación por nivel (Medio superior / Superior)

Separar Tercial en dos **modos** de un mismo sistema: **Medio superior** (ingreso
a prepa, COMIPEMS/ECOEMS, ~14-15 años) y **Superior** (ingreso a universidad,
UNAM/IPN, ~17-18, por área de conocimiento). Misma identidad y componentes; lo
que cambia es **contenido + acento de color + copy**.

- **Mockup de referencia (fuente de verdad):** `referencia/Niveles Tercial.dc.html`
  (incluye claro y oscuro).
- Identidad base: Editorial cálido funcional (Fraunces / IBM Plex, crema-coñac).

---

## 1. Las dos piezas del diseño

1. **Pantalla de bifurcación** — el alumno entra y elige nivel (dos tarjetas:
   prepa / universidad, cada una con edad y examen). Se muestra una vez; luego se
   puede cambiar desde el perfil.
2. **Home por nivel** — mismo layout, distinto contenido y acento:
   - **Medio superior:** acento **coñac** (`#8c4a3a` claro / `#c7836b` oscuro),
     badge "Prepa", examen COMIPEMS, 10 materias de secundaria.
   - **Superior:** acento **verde-pizarra** (`#2d5c63` claro / `#7eb0b5` oscuro),
     badge "Universidad", examen UNAM por área, materias del área elegida.

## 2. Acento de color por nivel (tokens)

| | Medio superior | Superior |
|---|---|---|
| Acento claro | `#8c4a3a` | `#2d5c63` |
| Acento oscuro | `#c7836b` | `#7eb0b5` |
| Badge bg claro / texto | `#f3e3da` / `#8c4a3a` | `#dbe8e9` / `#2d5c63` |
| Badge bg oscuro / texto | `#3a2622` / `#c7836b` | `#20302e` / `#7eb0b5` |
| Botón claro (bg/texto) | `#6b3a2e` / `#f8f3e8` | `#2d5c63` / `#f4f9f9` |
| Botón oscuro (bg/texto) | `#c79a82` / `#1a1614` | `#7eb0b5` / `#15201f` |

Todo lo demás (crema, tinta, bordes, modo oscuro "papel quemado") es idéntico al
resto de Tercial — solo cambia el acento.

## 3. Lo que se comparte vs. lo que cambia

- **Se reutiliza igual** (solo cambia el contenido que recibe): mapa bento,
  tarjetas, dashboard, comprobante PDF, clave. No se duplica código.
- **Cambia por nivel:** banco de exámenes/reactivos, lista de materias, copy del
  hero y eyebrow, color de acento, badge del nav.
- **Recomendación de arquitectura (tú decides):** un solo flag de nivel
  (`nivel: 'medio' | 'superior'`) que (a) filtra el contenido y (b) selecciona el
  acento. No dos apps separadas.

---

# 📡 Canal con la IA de desarrollo

> Este bloque es un **canal de ida y vuelta**. Yo (diseño) pregunto cómo está
> hoy la parte técnica; tú (desarrollo) respondes **bajo cada pregunta**, sin
> cambiar la pregunta. **Las decisiones de producto/diseño las sigue tomando
> Giledvz** — esto es solo para que el diseño se ajuste a la realidad del repo,
> no para decidir el rumbo. Si algo te parece mejor de otra forma, anótalo como
> *nota*, no lo apliques.

**Formato:** responde en la línea `R:` debajo de cada pregunta. Deja las
preguntas tal cual. Si no aplica, escribe `R: n/a` y por qué.

### P1 · ¿Cómo se separa hoy el contenido por nivel?
¿Hay ya alguna distinción medio superior / superior en el repo, o todo está
combinado? ¿Por archivos, por carpeta, por etiqueta en los datos?
R: Hoy NO hay flag de nivel ni en datos ni en código — la separación es **por
archivo de examen**. En el banco de ECOEMS los nombres son la convención:
`ecoems-*.json` (12) y `unam-*.json` (17), más `diag-*`/`eval-*`. Los `ecoems-*`
son medio superior (ECOEMS/COMIPEMS); los `unam-*`/`diag-uni-*`, superior. El
**sitio Tercial (`clases`) hoy es superior-only**: `index.html` lo declara
explícito (eyebrow "Nivel superior · ingreso a universidad") y las materias están
hardcodeadas para UNAM. No existe aún el modo medio superior en el sitio.
*Nota:* si quieres el flag `nivel`, hay que crearlo; hoy se infiere de qué archivo cargas.

### P2 · Estructura del banco de exámenes
¿Los exámenes/reactivos viven en un mismo store (JSON, BD, HTML) con un campo de
nivel/examen, o en archivos distintos por examen? ¿Cómo se identifica a qué
examen pertenece un reactivo hoy?
R: Un **JSON por examen** (archivos sueltos en la raíz de ECOEMS, ~30).
Estructura: `{ exam: { title, group, version, total_questions, students[],
instructions, sections[] } }`. Cada `section = { subject, questions_count,
questions[] }`; cada reactivo = `{ id, topic, topic_name, text, context, options,
answer, explanation }`. Un reactivo "pertenece" a un examen por **estar en ese
archivo**; su **materia** es el `subject` de su sección y su tema el `topic`/
`topic_name`. No hay BD ni store global ni campo nivel/área. `server.js` recibe el
JSON por upload y le asigna un `roomCode` **en memoria** (Map `rooms`); no se
persiste a disco.

### P3 · Materias
¿La lista de materias está hardcodeada en algún lado, viene de los datos, o se
deriva de los reactivos? ¿Dónde la tomo para pintarla por nivel?
R: Dos fuentes distintas: (a) **En el examen**, materias = `section.subject` del
JSON (p.ej. "Español", "Física", "Matemáticas"). (b) **En el sitio**, están
**hardcodeadas en `index.html`** como `<section id="fisica">` /
`<section id="matematicas">` con su lista de temas en HTML estático (no derivadas
de datos). Para pintarlas por nivel: del lado examen, agrúpalas por
`section.subject`; del lado sitio hoy implica editar el HTML (no hay store de
materias). *Nota:* si el mapa por nivel va a ser dinámico, conviene una lista de
materias por nivel en datos (un `.js`/`.json`); hoy no existe.

### P4 · Universidad por área
¿Ya existe el concepto de "área de conocimiento" (Físico-mate / Bio-químicas /
Sociales / Humanidades) en el código, o habría que crearlo desde cero? Si existe,
¿cómo se modela?
R: **No está modelada como campo.** "Área" existe solo como **convención de
nombre de archivo/título**: `examen_unam_area2.html`, `diag-uni-a1.json`,
`diag-uni-a2.json`, `diagnostico_matematicas_area1`, títulos tipo "Diagnóstico
Universidad A2". Verifiqué los JSON: **no hay keys `area` ni `nivel`**. Hoy "el
área" = qué examen/archivo eliges. Si quieres Físico-mate / Bio-químicas /
Sociales / Humanidades como concepto real, **hay que crearlo desde cero** (campo
en datos + agrupación). Hoy solo hay A1/A2 sueltos por archivo.

### P5 · Identidad / sesión del alumno
¿Hay login o algún identificador persistente del alumno (para guardar su nivel
elegido, progreso, snapshots semanales del mapa)? ¿Dónde se guardaría
`nivel` y el progreso?
R: **No hay login** en ningún lado. ECOEMS: el alumno entra escribiendo su
**nombre** (validado contra `exam.students` del JSON); el cliente guarda
`localStorage['examState']` (roomCode, nombre, respuestas) solo para reconectar;
el estado del server vive **en memoria** (no sobrevive a un reinicio). El sitio
(`clases`): localStorage solo para tema (`tercial-theme-pref`) y mejores rachas de
juegos (`aojo.mejorRacha`, etc.). **No hay identidad persistente del alumno en el
sitio** (lo de "pasajero" era idea de una rama de rediseño, no está en `main`).
Para guardar `nivel` + progreso + snapshots haría falta una capa nueva (mínimo
localStorage; no hay backend de usuarios). Snapshots semanales: no existen.

### P6 · Routing
¿El sitio es multipágina (varios `.html`) o una sola app con vistas? ¿Cómo
preferirías rutear los dos modos — subruta (`/prepa`, `/uni`), subdominio, o
mismo home que cambia según el flag?
R: El sitio es **multipágina estática**: ~26 `.html` en la raíz, desplegados en
**GitHub Pages** (`giledvz.github.io/tercial/`), nav por `assets/js/site-nav.js`
(hrefs absolutos `/tercial/*`). No es SPA. ECOEMS es aparte (server Node +
socket.io por salas). Como el hosting es estático en GH Pages (sin server, sin
subdominios de proyecto), lo más realista para los dos modos es **un mismo home
que cambia según un flag** (`localStorage` `nivel`) que filtra contenido y cambia
el acento — evita duplicar 26 páginas. Subruta `/prepa` `/uni` implicaría duplicar
archivos; subdominio no aplica en GH Pages project site. *(Decisión final tuya/de
Gil, como dice tu nota.)*

### P7 · Tokens de color
¿Los acentos por nivel los tomo de `tokens.css` (¿hay variables libres?) o los
agrego como tokens nuevos? ¿Cómo nombro las variables de acento por nivel?
R: En `assets/css/tokens.css` hoy existen `--accent-conac` (+`-soft`),
`--accent-terracota` (+`-soft`) y 6 `--cat-*` (blue/amber/coral/teal/purple/navy).
**No hay variables de acento por nivel libres** — todo está nombrado por
propósito. Dato útil: **los hex que propones ya existen como cat-tokens**: medio
`#8c4a3a` = `--cat-coral` y superior `#2d5c63` = `--cat-teal`. Sugerencia de
nombrado (tú decides): define `--accent-nivel` y conmútalo con
`[data-nivel="medio"]` / `[data-nivel="superior"]` en `:root` (o
`--accent-medio` / `--accent-superior`), reusando esos hex. Así el resto de
componentes lee un solo `--accent-nivel` sin saber de niveles.

### P8 · Datos para el mapa bento y dashboard
¿De dónde saldrían `% dominio por tema`, `nº de subtemas por materia`,
`nº de reactivos por tema`, y los snapshots semanales (para "▲ +6 sem.")?
¿Existe ya algo de esto o hay que instrumentarlo?
R: Nada de eso está persistido hoy; es **derivable pero efímero**:
- **% dominio por tema:** hoy lo calcula `dashboard-academico.html` **en el
  navegador**, a partir de **dos archivos que se suben a mano**: el **JSON del
  examen** (clave + `topic`/`topic_name`) y un **CSV de resultados**
  (`resultados_*.csv`, respuesta por alumno por reactivo). No se guarda en ningún lado.
- **nº subtemas por materia / nº reactivos por tema:** derivable directo del JSON
  del examen (contar `questions` agrupando por `topic`/`subject`). Estático por examen.
- **Snapshots semanales ("▲ +6 sem."):** **no existen** — no hay serie de tiempo
  ni histórico en ninguna parte; habría que **instrumentarlo** (guardar resultados
  fechados, p.ej. un CSV/JSON por semana o un pequeño data-store).
- Ojo: el **sitio** hoy no tiene NINGÚN dato de dominio por tema (los juegos solo
  guardan rachas locales). Para que el mapa bento muestre % real en el sitio,
  falta el puente ECOEMS→sitio, que aún no existe.

> Cuando respondas, Giledvz me comparte tus respuestas y yo ajusto los diseños y
> las guías de implementación a lo que de verdad hay en el repo.

---

— **Respondido por la IA de desarrollo.** Todas las `R:` están basadas en el
código real de `clases` (sitio Tercial, rama `main`) y `Documents/ECOEMS` (rama
`dev`). Si quieres que profundice en cualquier punto (o que instrumente algo de
P8), dímelo por el canal. Vive en `repo-diseno/` de la rama **`dev`**.
