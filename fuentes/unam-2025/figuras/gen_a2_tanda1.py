# unam-a2-5 — figuras de los ids 2, 3, 4, 34, 52, 58 y 68.
# Faltan el id 8 (esquina con difracción) y el id 35 (fórmulas por opción),
# que van en una segunda tanda.
import os, math, sys

sys.path.insert(0, os.path.dirname(__file__))
from comun import svg, flecha
import gen_a3_tanda1                      # el id 2 es el mismo reactivo que el id 3 del Área 3

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a2-5'

def hachura(x1, x2, y, alto=10, paso=11, arriba=False):
    """Superficie fija: la línea más el rayado inclinado."""
    o = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="currentColor" stroke-width="2.2"/>']
    d = -alto if arriba else alto
    x = x1
    while x < x2:
        o.append(f'<line x1="{x}" y1="{y}" x2="{x-8}" y2="{y+d}" stroke="currentColor" stroke-width="1.1"/>')
        x += paso
    return o

def malla(ox, oy, u, xmin, xmax, ymin, ymax, punteada=True):
    """Cuadrícula suave más los dos ejes con punta de flecha."""
    g = 'stroke="currentColor" stroke-width="0.7" stroke-opacity="0.25"' + \
        (' stroke-dasharray="2 4"' if punteada else '')
    c = []
    for i in range(xmin, xmax + 1):
        c.append(f'<line x1="{ox+i*u}" y1="{oy-ymax*u}" x2="{ox+i*u}" y2="{oy-ymin*u}" {g}/>')
    for j in range(ymin, ymax + 1):
        c.append(f'<line x1="{ox+xmin*u}" y1="{oy-j*u}" x2="{ox+xmax*u}" y2="{oy-j*u}" {g}/>')
    c += [f'<line x1="{ox+xmin*u-14}" y1="{oy}" x2="{ox+xmax*u+16}" y2="{oy}" stroke="currentColor" stroke-width="1.7"/>',
          f'<line x1="{ox}" y1="{oy-ymin*u+14}" x2="{ox}" y2="{oy-ymax*u-16}" stroke="currentColor" stroke-width="1.7"/>',
          f'<path d="M {ox+xmax*u+16} {oy} l -8 -4 l 0 8 z" fill="currentColor"/>',
          f'<path d="M {ox} {oy-ymax*u-16} l -4 8 l 8 0 z" fill="currentColor"/>']
    return c

# ── id 2: Fuerza contra aceleración (mismo reactivo que el id 3 del Área 3) ──
def fig2():
    return gen_a3_tanda1.fig3()

# ── id 3: resorte libre y resorte estirado por una fuerza F ─────────────────
def resorte(cx, y0, y1, vueltas=7, r=15):
    """Hélice proyectada: gira en x mientras baja en y. Es lo que se ve al
    dibujar un resorte de lado."""
    pts = []
    n = vueltas * 36
    for i in range(n + 1):
        t = 2 * math.pi * vueltas * i / n
        pts.append(f'{cx + r*math.cos(t):.1f},{y0 + (y1-y0)*i/n:.1f}')
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round"/>')

def fig3():
    W, H = 430, 300
    techo, xa, xb = 44, 118, 300
    c = hachura(xa - 52, xa + 52, techo) + hachura(xb - 52, xb + 52, techo)
    # izquierda: en reposo. derecha: estirado, con la fuerza F colgando
    c += [f'<line x1="{xa}" y1="{techo}" x2="{xa}" y2="{techo+14}" stroke="currentColor" stroke-width="2"/>',
          resorte(xa, techo + 14, techo + 96),
          f'<line x1="{xb}" y1="{techo}" x2="{xb}" y2="{techo+14}" stroke="currentColor" stroke-width="2"/>',
          resorte(xb, techo + 14, techo + 176, vueltas=7)]
    # la fuerza, colgando del extremo del resorte estirado
    c += flecha(xb, techo + 176, xb, techo + 226, grosor=2.4)
    c.append(f'<text x="{xb+14}" y="{techo+216}" font-size="19" font-weight="600" '
             f'font-style="italic">F</text>')
    # acotación del alargamiento x, entre las dos longitudes
    ax = xb - 62
    y1, y2 = techo + 96, techo + 176
    c += flecha(ax, (y1+y2)/2 - 4, ax, y1, grosor=1.6, punta=8)
    c += flecha(ax, (y1+y2)/2 + 4, ax, y2, grosor=1.6, punta=8)
    for y in (y1, y2):
        c.append(f'<line x1="{ax-9}" y1="{y}" x2="{ax+9}" y2="{y}" stroke="currentColor" '
                 f'stroke-width="1.2" stroke-opacity="0.7"/>')
    c.append(f'<text x="{ax-13}" y="{(y1+y2)//2+6}" font-size="19" font-style="italic" '
             f'text-anchor="end">x</text>')
    return svg(W, H, c, 'Resorte libre y resorte estirado una distancia x por la fuerza F')

# ── id 4: balines X y Y sobre un riel, en sentidos opuestos ─────────────────
def fig4():
    W, H = 460, 220
    riel, xx, xy = 148, 128, 320
    c = [f'<text x="{W//2}" y="26" font-size="15" font-weight="600" text-anchor="middle">'
         f'Dirección de desplazamiento</text>']
    # riel: línea doble
    for dy in (0, 7):
        c.append(f'<line x1="34" y1="{riel+dy}" x2="{W-34}" y2="{riel+dy}" '
                 f'stroke="currentColor" stroke-width="2"/>')
    for cx, r, nom, sentido in ((xx, 20, 'X', +1), (xy, 28, 'Y', -1)):
        c.append(f'<circle cx="{cx}" cy="{riel-r}" r="{r}" fill="currentColor" '
                 f'fill-opacity="0.14" stroke="currentColor" stroke-width="2"/>')
        c.append(f'<text x="{cx}" y="{riel-r+7}" font-size="19" font-weight="600" '
                 f'text-anchor="middle">{nom}</text>')
        y = riel - 2 * r - 26
        c += flecha(cx - sentido * 34, y, cx + sentido * 34, y)
    return svg(W, H, c, 'Balines X (200 g) y Y (400 g) sobre un riel, con velocidades opuestas')

# ── id 34: esqueleto de un alqueno ramificado ──────────────────────────────
def fig34():
    W, H = 400, 200
    paso, alto, x0, y0 = 54, 40, 46, 76      # y0 es el nivel alto del zigzag
    # 6 carbonos en zigzag; metilo sobre C2; doble enlace entre C4 y C5.
    # El zigzag arranca ABAJO para que C2 quede arriba y el metilo suba limpio.
    v = [(x0 + i * paso, y0 + alto if i % 2 == 0 else y0) for i in range(6)]
    c = []
    for i in range(5):
        (ax, ay), (bx, by) = v[i], v[i + 1]
        if i == 3:                            # doble enlace C4=C5: dos trazos paralelos
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy)
            nx, ny = -dy / L * 4.5, dx / L * 4.5
            for s in (+1, -1):
                c.append(f'<line x1="{ax+nx*s:.1f}" y1="{ay+ny*s:.1f}" x2="{bx+nx*s:.1f}" '
                         f'y2="{by+ny*s:.1f}" stroke="currentColor" stroke-width="2.4"/>')
        else:
            c.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="currentColor" '
                     f'stroke-width="2.4"/>')
    # ramificación metilo, hacia arriba desde C2
    bx, by = v[1]
    c.append(f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by-46}" stroke="currentColor" stroke-width="2.4"/>')
    return svg(W, H, c, 'Esqueleto de un alqueno de seis carbonos con una ramificación metilo')

# ── id 52: f(x) = −√(8x − 16) ───────────────────────────────────────────────
def fig52():
    u, ox, oy = 62, 62, 74
    W, H = 340, 300
    c = malla(ox, oy, u, 0, 4, -3, 1, punteada=False)
    c += [f'<text x="{ox+4*u+22}" y="{oy+18}" font-size="15" font-style="italic">x</text>',
          f'<text x="{ox+10}" y="{oy-1*u-22}" font-size="15" font-style="italic">f(x)</text>',
          f'<text x="{ox-10}" y="{oy+18}" font-size="13" text-anchor="end">0</text>']
    for i in (1, 2, 3):
        c.append(f'<line x1="{ox+i*u}" y1="{oy-4}" x2="{ox+i*u}" y2="{oy+4}" stroke="currentColor" stroke-width="1.3"/>')
        # el 2 se corre a la izquierda: es donde arranca la curva y la tapaba
        c.append(f'<text x="{ox+i*u-(12 if i == 2 else 0)}" y="{oy+19}" font-size="13" '
                 f'text-anchor="middle">{i}</text>')
    for j in (1, -1, -2, -3):
        c.append(f'<line x1="{ox-4}" y1="{oy-j*u}" x2="{ox+4}" y2="{oy-j*u}" stroke="currentColor" stroke-width="1.3"/>')
        c.append(f'<text x="{ox-9}" y="{oy-j*u+5}" font-size="13" text-anchor="end">{j}</text>')
    pts = []
    x = 2.0
    while x <= 3.15:
        y = -math.sqrt(8 * x - 16)
        if y < -3.1:
            break
        pts.append(f'{ox+x*u:.1f},{oy-y*u:.1f}')
        x += 0.01
    c.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="2.8"/>')
    return svg(W, H, c, 'f(x) = −√(8x − 16): arranca en (2, 0) y baja hacia la derecha')

# ── id 58: triángulo A(0,0), (1,4), B(4,2) ─────────────────────────────────
def fig58():
    u, ox, oy = 46, 68, 268
    W, H = 380, 330
    c = malla(ox, oy, u, -1, 5, -1, 5)
    c += [f'<text x="{ox+5*u+22}" y="{oy+18}" font-size="15" font-style="italic">x</text>',
          f'<text x="{ox+12}" y="{oy-5*u-22}" font-size="15" font-style="italic">y</text>',
          ]   # el 0 del origen se omite: ahí va el rótulo del vértice A
    for i in (1, 2, 3, 4, 5):
        c.append(f'<text x="{ox+i*u}" y="{oy+19}" font-size="13" text-anchor="middle">{i}</text>')
        c.append(f'<text x="{ox-9}" y="{oy-i*u+5}" font-size="13" text-anchor="end">{i}</text>')
    P = {'A': (0, 0), 'T': (1, 4), 'B': (4, 2)}
    px = {k: (ox + x * u, oy - y * u) for k, (x, y) in P.items()}
    c.append(f'<path d="M {px["A"][0]} {px["A"][1]} L {px["T"][0]} {px["T"][1]} '
             f'L {px["B"][0]} {px["B"][1]} Z" fill="currentColor" fill-opacity="0.08" '
             f'stroke="currentColor" stroke-width="2.4"/>')
    for k, dx, dy, an in (('A', -11, 20, 'end'), ('B', 14, 6, 'start')):
        c.append(f'<circle cx="{px[k][0]}" cy="{px[k][1]}" r="4" fill="currentColor"/>')
        c.append(f'<text x="{px[k][0]+dx}" y="{px[k][1]+dy}" font-size="18" font-style="italic" '
                 f'text-anchor="{an}">{k}</text>')
    c.append(f'<circle cx="{px["T"][0]}" cy="{px["T"][1]}" r="4" fill="currentColor"/>')
    return svg(W, H, c, 'Triángulo con A(0,0), vértice superior (1,4) y B(4,2)')

# ── id 68: función acotada con un solo tramo, discontinuidades finitas ─────
def fig68():
    u, ox, oy = 38, 230, 192
    W, H = 460, 376
    c = malla(ox, oy, u, -5, 5, -4, 4)
    c += [f'<text x="{ox+5*u+22}" y="{oy+18}" font-size="15" font-style="italic">x</text>',
          f'<text x="{ox+12}" y="{oy-4*u-22}" font-size="15" font-style="italic">y</text>',
          f'<text x="{ox-10}" y="{oy+18}" font-size="13" text-anchor="end">0</text>']
    for i in range(-5, 6):
        if i:
            c.append(f'<line x1="{ox+i*u}" y1="{oy-4}" x2="{ox+i*u}" y2="{oy+4}" stroke="currentColor" stroke-width="1.2"/>')
    for j in range(-4, 5):
        if j:
            c.append(f'<line x1="{ox-4}" y1="{oy-j*u}" x2="{ox+4}" y2="{oy-j*u}" stroke="currentColor" stroke-width="1.2"/>')
    y = oy + u                                # el tramo vive en y = −1
    c.append(f'<line x1="{ox-3*u}" y1="{y}" x2="{ox}" y2="{y}" stroke="currentColor" stroke-width="3.4"/>')
    for x in (ox - 3 * u, ox):
        c.append(f'<circle cx="{x}" cy="{y}" r="5" fill="currentColor"/>')
    return svg(W, H, c, 'Función acotada: un solo segmento cerrado en y = −1, de x = −3 a x = 0')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for nombre, fn in (('q2_fuerza_aceleracion', fig2), ('q3_resortes', fig3),
                       ('q4_balines', fig4), ('q34_alqueno', fig34),
                       ('q52_raiz', fig52), ('q58_triangulo', fig58),
                       ('q68_acotada', fig68)):
        open(os.path.join(OUT, nombre + '.svg'), 'w').write(fn())
        print('escrito', nombre + '.svg')
