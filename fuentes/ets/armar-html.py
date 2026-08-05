# Arma el HTML del cuadernillo. Después armar-pdf.js lo imprime a PDF.
#
# Cada ejercicio lleva un enlace a su respuesta al final del documento, y cada
# respuesta un enlace de regreso al ejercicio. Chrome conserva esos anclajes como
# hipervínculos reales dentro del PDF, así que se puede navegar dando clic.
import html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar import construir, BLOQUES

# El enlace "ver respuesta" va pegado al final del enunciado. Solo ahorra donde el
# enunciado termina en texto (117 de los 184): si termina en fórmula centrada o en
# figura, ésas ya son bloques y el enlace baja de renglón igual. Medido: 5 páginas
# menos de 96. Con VER_INLINE=0 vuelve a su propio renglón.
INLINE = os.environ.get('VER_INLINE', '1') != '0'

RAIZ = '/Users/giledvz/Documents/ECOEMS'
KATEX = f'file://{RAIZ}/node_modules/katex/dist'

CSS = """
:root{
  --crema-50:#faf7f0; --crema-100:#f2ece0; --ink-900:#1f1a16; --ink-600:#5b504a;
  --ink-300:#a89c92; --terracota:#c2410c; --linea:#e2d9c9;
}
*{box-sizing:border-box}
body{
  margin:0; background:#fff; color:var(--ink-900);
  font-family:'Latin Modern Roman',Georgia,'Times New Roman',serif;
  font-size:10.5pt; line-height:1.5;
}
.hoja{padding:0}
h1,h2,h3{font-weight:600; line-height:1.2}

/* portada */
.portada{
  height:100vh; display:flex; flex-direction:column; justify-content:center;
  padding:0 14mm; page-break-after:always;
  background:var(--crema-50); border-left:3pt solid var(--terracota);
}
.portada .sello{
  font-size:9pt; letter-spacing:.18em; text-transform:uppercase;
  color:var(--terracota); margin-bottom:10mm;
}
.portada h1{font-size:30pt; margin:0 0 4mm; letter-spacing:-.01em}
.portada .sub{font-size:14pt; color:var(--ink-600); margin:0 0 12mm}
.portada .datos{
  border-top:1.5pt solid var(--ink-900); padding-top:5mm; font-size:10pt;
  color:var(--ink-600); max-width:118mm;
}
.portada .datos b{color:var(--ink-900)}

/* índice */
.indice{page-break-after:always; padding:0 2mm}
.indice ol{list-style:none; padding:0; margin:6mm 0 0}
.indice li{
  display:flex; align-items:baseline; gap:3mm; padding:1.6mm 0;
  border-bottom:.5pt solid var(--linea);
}
.indice .cv{
  font-weight:600; color:var(--terracota); min-width:7mm;
}
.indice .tt{flex:1}
.indice .ct{color:var(--ink-300); font-size:9pt; font-variant-numeric:tabular-nums}
.indice a{color:inherit; text-decoration:none}

/* bloques */
.bloque{page-break-before:always}
.bloque > h2{
  font-size:16pt; margin:0 0 1mm;
  border-bottom:1.5pt solid var(--ink-900); padding-bottom:2mm;
}
.bloque > h2 .cv{color:var(--terracota); margin-right:2mm}
.intro{
  color:var(--ink-600); font-size:9.5pt; margin:2.5mm 0 6mm;
  background:var(--crema-100); border-left:2.5pt solid var(--terracota);
  padding:3mm 4mm; border-radius:0 2pt 2pt 0;
}
.ej{
  page-break-inside:avoid; margin:0 0 5mm; padding-bottom:4mm;
  border-bottom:.5pt solid var(--linea); display:flex; gap:3.5mm;
}
.ej .n{
  font-weight:600; color:var(--terracota); min-width:9mm; font-size:10pt;
  font-variant-numeric:tabular-nums; padding-top:.3mm;
}
.ej .cuerpo{flex:1; min-width:0}
.ej figure{margin:3mm 0 0; text-align:center}
.ej figure svg{max-width:78mm; height:auto}
.ver{
  display:inline-block; margin-top:1.5mm; font-size:8.5pt; color:var(--terracota);
  text-decoration:none;
}
.ver.pegado{margin-top:0; margin-left:2.5mm; white-space:nowrap}

/* respuestas */
.respuestas{page-break-before:always}
.respuestas > h2{
  font-size:20pt; margin:0 0 2mm; border-bottom:2pt solid var(--ink-900);
  padding-bottom:2.5mm;
}
.respuestas h3{
  font-size:12pt; margin:8mm 0 3mm; color:var(--terracota);
  border-bottom:.5pt solid var(--linea); padding-bottom:1.5mm;
}
.resp{page-break-inside:avoid; margin:0 0 4.5mm; display:flex; gap:3.5mm}
.resp .n{
  font-weight:600; min-width:9mm; font-size:10pt; font-variant-numeric:tabular-nums;
}
.resp .cuerpo{flex:1; min-width:0}
.resp .paso{margin:0 0 1.4mm}
.resp .final{
  margin-top:2mm; padding:2mm 3mm; background:var(--crema-100);
  border-left:2.5pt solid var(--ink-900); border-radius:0 2pt 2pt 0;
}
.resp .final b{font-size:8.5pt; letter-spacing:.08em; text-transform:uppercase;
  color:var(--ink-600); display:block; margin-bottom:.8mm}
.volver{
  display:inline-block; margin-top:1.5mm; font-size:8.5pt; color:var(--terracota);
  text-decoration:none; border-bottom:.5pt dotted var(--terracota);
}
/* encabezado de cada sección de respuestas, con su regreso al bloque */
.respuestas h3{display:flex; align-items:baseline; justify-content:space-between; gap:4mm}
.alBloque{
  font-size:8.5pt; font-weight:400; color:var(--ink-600); text-decoration:none;
  white-space:nowrap; border-bottom:.5pt dotted var(--ink-300);
}
/* barra discreta bajo el título de cada bloque */
.migas{
  display:flex; gap:4mm; font-size:8.5pt; color:var(--ink-300); margin:3mm 0 4.5mm;
}
.migas a{color:var(--ink-600); text-decoration:none;
  border-bottom:.5pt dotted var(--ink-300);}
.katex{font-size:1.02em}
.katex-display{margin:2mm 0}
strong{font-weight:600}
"""

def md(t):
    """Negritas de markdown a HTML. El resto del texto ya viene listo."""
    partes = t.split('**')
    return ''.join(p if i % 2 == 0 else f'<strong>{p}</strong>' for i, p in enumerate(partes))

def main():
    datos = construir()
    total = sum(len(b['ejercicios']) for b in datos)

    o = ['<!doctype html><html lang="es"><head><meta charset="utf-8">',
         f'<link rel="stylesheet" href="{KATEX}/katex.min.css">',
         f'<script defer src="{KATEX}/katex.min.js"></script>',
         f'<script defer src="{KATEX}/contrib/auto-render.min.js"></script>',
         f'<style>{CSS}</style></head><body>']

    # ── portada ──
    o.append(f'''<section class="portada">
      <div class="sello">IPN · CECyT 1 "Lic. Gonzalo Vázquez Vela"</div>
      <h1>Geometría y Trigonometría</h1>
      <p class="sub">Cuadernillo de práctica para el ETS</p>
      <div class="datos">
        <p><b>{total} ejercicios</b> repartidos en <b>{len(datos)} bloques</b>, uno por
        cada tipo de problema que aparece en el examen.</p>
        <p>Los tipos salen de los ocho ETS de esta materia que tenemos a la mano
        (2009, 2010, 2017, 2018, 2019, 2023, 2025 y enero de 2026). Los números
        cambian año con año, pero los <b>tipos de problema son casi los mismos</b>:
        por eso conviene practicar por tipo y no examen por examen.</p>
        <p>Cada ejercicio tiene un enlace a su respuesta, con el procedimiento
        completo. Da clic en <i>ver respuesta</i> para saltar al final, y en la flecha
        de la respuesta para regresar.</p>
        <p style="margin-top:6mm;color:var(--ink-300)">Resuelve primero. La respuesta
        solo sirve si ya lo intentaste.</p>
      </div>
    </section>''')

    # ── índice ──
    o.append('<section class="indice" id="contenido"><h2 style="font-size:18pt;margin:0 0 1mm;'
             'border-bottom:2pt solid var(--ink-900);padding-bottom:2.5mm">Contenido</h2>')
    o.append('<ol>')
    for b in datos:
        o.append(f'<li><span class="cv">{b["clave"]}</span>'
                 f'<span class="tt"><a href="#b-{b["clave"]}">{html.escape(b["titulo"])}</a></span>'
                 f'<span class="ct">{len(b["ejercicios"])} ej.</span></li>')
    o.append(f'<li style="margin-top:4mm;border:none"><span class="cv">✓</span>'
             f'<span class="tt"><a href="#respuestas"><b>Respuestas y procedimientos</b></a>'
             f'</span><span class="ct">{total}</span></li>')
    o.append('</ol></section>')

    # ── bloques ──
    for b in datos:
        o.append(f'<section class="bloque" id="b-{b["clave"]}">')
        o.append(f'<h2><span class="cv">{b["clave"]}</span>{html.escape(b["titulo"])}</h2>')
        o.append(f'<div class="migas"><a href="#contenido">↑ Contenido</a>'
                 f'<a href="#respuestas">Respuestas del cuadernillo →</a>'
                 f'<a href="#rb-{b["clave"]}">Respuestas de este bloque →</a></div>')
        o.append(f'<p class="intro">{md(html.escape(b["intro"]))}</p>')
        for i, e in enumerate(b['ejercicios'], 1):
            eid = f'{b["clave"]}{i}'
            enlace = f'<a class="ver{" pegado" if INLINE else ""}" href="#r-{eid}">' \
                     f'ver respuesta →</a>'
            o.append(f'<div class="ej" id="e-{eid}"><div class="n">{eid}</div>'
                     f'<div class="cuerpo">')
            if INLINE and not e['figura']:
                o.append(f'<div>{md(e["enunciado"])}{enlace}</div>')
            else:
                o.append(f'<div>{md(e["enunciado"])}</div>')
                if e['figura']:
                    o.append(f'<figure>{e["figura"]}</figure>')
                o.append(enlace)
            o.append('</div></div>')
        o.append('</section>')

    # ── respuestas ──
    o.append('<section class="respuestas" id="respuestas"><h2>Respuestas y procedimientos</h2>')
    o.append('<p class="intro">Cada respuesta trae el procedimiento, no nada más el '
             'resultado: en el ETS te califican el desarrollo, así que acostúmbrate a '
             'escribirlo completo.</p>')
    for b in datos:
        o.append(f'<h3 id="rb-{b["clave"]}"><span>{b["clave"]}. '
                 f'{html.escape(b["titulo"])}</span>'
                 f'<a class="alBloque" href="#b-{b["clave"]}">← volver a las preguntas '
                 f'del bloque {b["clave"]}</a></h3>')
        for i, e in enumerate(b['ejercicios'], 1):
            eid = f'{b["clave"]}{i}'
            o.append(f'<div class="resp" id="r-{eid}"><div class="n">{eid}</div>'
                     f'<div class="cuerpo">')
            for p in e['pasos']:
                o.append(f'<div class="paso">{md(p)}</div>')
            if e['respuesta'] != 'Ver el desarrollo.':
                o.append(f'<div class="final"><b>Respuesta</b>{md(e["respuesta"])}</div>')
            o.append(f'<a class="volver" href="#e-{eid}">← volver a la pregunta {eid}</a>')
            o.append('</div></div>')
    o.append('</section>')

    o.append('''<script>
      window.addEventListener('DOMContentLoaded', () => {
        renderMathInElement(document.body, {
          delimiters: [{left:'$$',right:'$$',display:true},
                       {left:'$',right:'$',display:false}],
          throwOnError: false,
        });
        document.body.dataset.listo = '1';
      });
    </script></body></html>''')

    salida = os.path.join(RAIZ, 'fuentes/ets/cuadernillo.html')
    open(salida, 'w', encoding='utf-8').write('\n'.join(o))
    print(f'  {salida}  ·  {total} ejercicios en {len(datos)} bloques')

if __name__ == '__main__':
    main()
