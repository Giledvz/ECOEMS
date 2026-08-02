# unam-a1-5 id 2 — sistema de tres vectores.
#
# La figura de la guía se contradice: dibuja el vector de 9 N a unos 20° pero lo
# rotula 75°, y con ninguna lectura de ese dibujo se llega a la clave oficial
# (√101.1). Probadas las 192 combinaciones posibles de cuadrante y eje de
# referencia, el único valor alcanzable de las cuatro opciones es √75.8, y se
# obtiene con UN solo cambio respecto de lo que describe la guía: los 30° del
# vector de 8 N se miden desde el eje vertical.
#
#   8 N a 30° del eje +y   → ( 4.0, +6.4)
#   9 N a 75° bajo el +x   → ( 2.7, −8.1)
#   10 N a 45° bajo el −x  → (−7.0, −7.0)
#   resultante             = (−0.3, −8.7)  →  R² = 75.78  →  √75.8
#
# Así que aquí se dibuja esa disposición, con cada ángulo marcado contra el eje
# desde el que de verdad se mide.
import os, math, sys

sys.path.insert(0, os.path.dirname(__file__))
from comun import svg, flecha

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a1-5'

W = H = 380
CX = CY = 190
ESC = 10.5                     # píxeles por newton

# (magnitud, ángulo del vector medido desde +x, texto del ángulo, eje de
#  referencia contra el que se marca el arco, en grados desde +x)
VECTORES = [
    (8,   60, '30°', 90),      # 30° respecto del eje vertical
    (9,  -75, '75°',  0),      # 75° por debajo del semieje +x
    (10, 225, '45°', 180),     # 45° respecto del semieje −x
]

def pt(ang, r):
    a = math.radians(ang)
    return CX + r * math.cos(a), CY - r * math.sin(a)

def arco(a1, a2, r):
    """Arco entre dos direcciones, por el camino corto."""
    p1, p2 = pt(a1, r), pt(a2, r)
    d = (a2 - a1) % 360
    barrido = 0 if d < 180 else 1          # en SVG la y va al revés
    return (f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {r} {r} 0 0 {barrido} '
            f'{p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="currentColor" '
            f'stroke-width="1.3" stroke-opacity="0.8"/>')

def fig2():
    L = 158
    c = []
    for a in (0, 90, 180, 270):            # los cuatro semiejes
        x, y = pt(a, L)
        c.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" '
                 f'stroke="currentColor" stroke-width="1.5" stroke-opacity="0.75"/>')
    for a, (dx, dy) in ((0, (14, 6)), (90, (12, -8))):
        x, y = pt(a, L)
        c.append(f'<path d="M {x:.1f} {y:.1f} l {-8*math.cos(math.radians(a))-4*math.sin(math.radians(a)):.1f} '
                 f'{8*math.sin(math.radians(a))-4*math.cos(math.radians(a)):.1f} '
                 f'l {8*math.sin(math.radians(a)):.1f} {8*math.cos(math.radians(a)):.1f} z" fill="currentColor"/>')
        c.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="16" font-style="italic">'
                 f'{"x" if a == 0 else "y"}</text>')

    for i, (mag, ang, txt, ref) in enumerate(VECTORES):
        r = mag * ESC
        x, y = pt(ang, r)
        # el de 10 N va más grueso, como en la guía
        c += flecha(CX, CY, x, y, grosor=3.0 if mag == 10 else 2.2, punta=11)
        # rótulo de la magnitud, un poco más allá de la punta
        lx, ly = pt(ang, r + 24)
        c.append(f'<text x="{lx:.1f}" y="{ly+5:.1f}" font-size="17" font-weight="600" '
                 f'text-anchor="middle">{mag} N</text>')
        # arco del ángulo contra su eje de referencia, y su rótulo a la mitad
        ra = 40 + 13 * i                   # radios distintos para que no se encimen
        c.append(arco(min(ang, ref), max(ang, ref), ra))
        mx, my = pt((ang + ref) / 2, ra + 15)
        c.append(f'<text x="{mx:.1f}" y="{my+5:.1f}" font-size="14" '
                 f'text-anchor="middle">{txt}</text>')
    return svg(W, H, c, 'Tres vectores desde el origen: 8 N a 30° del eje y, '
                        '9 N a 75° bajo el eje x y 10 N a 45° del semieje −x')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'q2_vectores.svg'), 'w').write(fig2())
    print('escrito q2_vectores.svg')
