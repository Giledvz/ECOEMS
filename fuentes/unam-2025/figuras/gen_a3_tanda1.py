# unam-a3-5 — primera tanda de figuras: ids 1, 3, 54 y 58.
# Todas tema-adaptables: trazos en currentColor, rellenos con opacidad baja.
import os, math

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a3-5'
FONT = "'Latin Modern Roman', Georgia, serif"

def svg(w, h, cuerpo, comentario=''):
    return (f'<svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">\n'
            + (f'<!-- {comentario} -->\n' if comentario else '')
            + '\n'.join(cuerpo) + '\n</svg>\n')

def ejes(x0, y0, ancho, alto, rx, ry):
    """Ejes con punta de flecha. (x0,y0) es el origen en píxeles."""
    return [
        f'<line x1="{x0}" y1="{y0}" x2="{x0+ancho}" y2="{y0}" stroke="currentColor" stroke-width="1.8"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-alto}" stroke="currentColor" stroke-width="1.8"/>',
        f'<path d="M {x0+ancho} {y0} l -8 -4 l 0 8 z" fill="currentColor"/>',
        f'<path d="M {x0} {y0-alto} l -4 8 l 8 0 z" fill="currentColor"/>',
        f'<text x="{x0+ancho+6}" y="{y0+18}" font-size="15">{rx}</text>',
        f'<text x="{x0-10}" y="{y0-alto-8}" font-size="15" text-anchor="middle">{ry}</text>',
    ]

# ── id 1: v-t con pendiente negativa, sin valores ────────────────────────────
def fig1():
    x0, y0, W, Hh = 56, 210, 250, 165
    c = ejes(x0, y0, W, Hh, '', '')
    # los rótulos van separados de las puntas de flecha para que no se encimen
    c += [f'<text x="{x0+W+8}" y="{y0+6}" font-size="15" font-style="italic">t</text>',
          f'<text x="{x0+W+8}" y="{y0+22}" font-size="12">(s)</text>',
          f'<text x="{x0-30}" y="{y0-Hh+4}" font-size="15" font-style="italic">V</text>',
          f'<text x="{x0-30}" y="{y0-Hh+20}" font-size="12" text-anchor="middle">(m/s)</text>']
    # recta de (0, v0) a (t1, 0)
    c.append(f'<line x1="{x0}" y1="{y0-135}" x2="{x0+205}" y2="{y0}" '
             f'stroke="currentColor" stroke-width="3"/>')
    return svg(x0+W+52, y0+40, c, 'Velocidad contra tiempo: recta descendente, aceleración negativa')

# ── id 3: Fuerza contra aceleración, recta por el origen ─────────────────────
def fig3():
    x0, y0 = 74, 226
    ex, ey = 118, 44          # px por unidad: 0.50 en x, 1.00 en y
    W, Hh = int(2.15*ex), int(4.6*ey)
    c = ejes(x0, y0, W, Hh, '', '')
    c += [f'<text x="{x0+W+14}" y="{y0+6}" font-size="13">Aceleración</text>',
          f'<text x="{x0+W+14}" y="{y0+22}" font-size="12">(m/s²)</text>',
          f'<text x="{x0-16}" y="{y0-Hh-6}" font-size="13">Fuerza (N)</text>',
          f'<text x="{x0-9}" y="{y0+17}" font-size="13" text-anchor="middle">0</text>']
    for i, v in enumerate(('0.50','1.00','1.50','2.00'), 1):
        x = x0 + i*ex/2*1.0
        x = x0 + (i*0.5)*(ex/0.5)/2   # 0.50,1.00,1.50,2.00 -> ex por 0.50
        x = x0 + i*ex/1.0*0.5
        c.append(f'<line x1="{x:.0f}" y1="{y0}" x2="{x:.0f}" y2="{y0+5}" stroke="currentColor" stroke-width="1.3"/>')
        c.append(f'<text x="{x:.0f}" y="{y0+19}" font-size="12" text-anchor="middle">{v}</text>')
    for i, v in enumerate(('1.00','2.00','3.00','4.00'), 1):
        y = y0 - i*ey
        c.append(f'<line x1="{x0-5}" y1="{y}" x2="{x0}" y2="{y}" stroke="currentColor" stroke-width="1.3"/>')
        c.append(f'<text x="{x0-9}" y="{y+5}" font-size="12" text-anchor="end">{v}</text>')
    # recta por el origen hasta (1.60, 4.00); pendiente = masa = 2.5 kg
    xf, yf = x0 + 1.60*(ex/0.5)/2, y0 - 4*ey
    xf = x0 + (1.60/0.5)*(ex/2)
    c.append(f'<line x1="{x0}" y1="{y0}" x2="{xf:.0f}" y2="{yf}" stroke="currentColor" stroke-width="2.6"/>')
    for a, F in ((0.40,1.00),(0.80,2.00),(1.20,3.00),(1.60,4.00)):
        px, py = x0 + (a/0.5)*(ex/2), y0 - F*ey
        # auxiliares en cruz: del eje vertical al punto, y del punto al eje horizontal
        c.append(f'<line x1="{x0}" y1="{py:.0f}" x2="{px:.0f}" y2="{py:.0f}" stroke="currentColor" '
                 f'stroke-width="1" stroke-dasharray="4 3" stroke-opacity="0.55"/>')
        c.append(f'<line x1="{px:.0f}" y1="{py:.0f}" x2="{px:.0f}" y2="{y0}" stroke="currentColor" '
                 f'stroke-width="1" stroke-dasharray="4 3" stroke-opacity="0.55"/>')
        c.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.4" fill="currentColor"/>')
    return svg(x0+W+110, y0+40, c, 'Fuerza contra aceleración: recta por el origen, pendiente = masa')

# ── id 54: triángulo para la ley de senos ───────────────────────────────────
def fig54():
    B, A, C = (60, 210), (300, 210), (168, 56)
    c = [f'<path d="M {B[0]} {B[1]} L {A[0]} {A[1]} L {C[0]} {C[1]} Z" fill="currentColor" '
         f'fill-opacity="0.09" stroke="currentColor" stroke-width="2.2"/>']
    for (p, t, dx, dy) in ((B,'B',-16,16), (A,'A',14,16), (C,'C',0,-14)):
        c.append(f'<text x="{p[0]+dx}" y="{p[1]+dy}" font-size="19" font-style="italic" '
                 f'text-anchor="middle">{t}</text>')
    # lados: a = BC (izquierdo), b = CA (derecho), c = BA (inferior)
    for (p1, p2, t, dx, dy) in ((B,C,'a',-16,4), (C,A,'b',16,4), (B,A,'c',0,24)):
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        c.append(f'<text x="{mx+dx:.0f}" y="{my+dy:.0f}" font-size="18" font-style="italic" '
                 f'text-anchor="middle">{t}</text>')
    return svg(360, 250, c, 'Triángulo ABC: lado a opuesto a A, b opuesto a B, c opuesto a C')

# ── id 58: recta y = x/2 - 1 ────────────────────────────────────────────────
def fig58():
    ux = uy = 34
    ox, oy = 150, 150          # origen
    W, H = 320, 280
    c = []
    for i in range(-4, 6):     # cuadrícula suave
        c.append(f'<line x1="{ox+i*ux}" y1="10" x2="{ox+i*ux}" y2="{H-10}" stroke="currentColor" '
                 f'stroke-width="0.6" stroke-opacity="0.14"/>')
        c.append(f'<line x1="10" y1="{oy+i*uy}" x2="{W-10}" y2="{oy+i*uy}" stroke="currentColor" '
                 f'stroke-width="0.6" stroke-opacity="0.14"/>')
    c += [f'<line x1="10" y1="{oy}" x2="{W-10}" y2="{oy}" stroke="currentColor" stroke-width="1.8"/>',
          f'<line x1="{ox}" y1="{H-10}" x2="{ox}" y2="10" stroke="currentColor" stroke-width="1.8"/>',
          f'<path d="M {W-10} {oy} l -8 -4 l 0 8 z" fill="currentColor"/>',
          f'<path d="M {ox} 10 l -4 8 l 8 0 z" fill="currentColor"/>',
          f'<text x="{W-16}" y="{oy+20}" font-size="15" font-style="italic">x</text>',
          f'<text x="{ox+12}" y="20" font-size="15" font-style="italic">y</text>',
          f'<text x="{ox-11}" y="{oy+17}" font-size="13">0</text>']
    for i in list(range(-4,0))+list(range(1,5)):
        c.append(f'<line x1="{ox+i*ux}" y1="{oy-4}" x2="{ox+i*ux}" y2="{oy+4}" stroke="currentColor" stroke-width="1.2"/>')
        c.append(f'<line x1="{ox-4}" y1="{oy+i*uy}" x2="{ox+4}" y2="{oy+i*uy}" stroke="currentColor" stroke-width="1.2"/>')
    # y = x/2 - 1 : corta el eje y en -1 y el eje x en 2
    def pt(x): return (ox + x*ux, oy - (x/2 - 1)*uy)
    p1, p2 = pt(-3.6), pt(4.2)
    c.append(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
             f'stroke="currentColor" stroke-width="2.6"/>')
    return svg(W, H, c, 'Recta y = x/2 - 1: corta el eje y en -1 y el eje x en 2')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for nombre, fn in (('q1_grafica_vt', fig1), ('q3_fuerza_aceleracion', fig3),
                       ('q54_triangulo', fig54), ('q58_recta', fig58)):
        open(os.path.join(OUT, nombre + '.svg'), 'w').write(fn())
        print('escrito', nombre + '.svg')
