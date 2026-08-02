# unam-a1-5 — figuras de los ids 3, 9, 11, 12, 13, 60 y 69.
# Quedan fuera el id 2 (la figura de la guía se contradice con su propia clave)
# y el id 38 (mapa de Caracas), que necesitan decisión aparte.
import os, math, sys

sys.path.insert(0, os.path.dirname(__file__))
from comun import svg, zig, flecha, fuerza

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a1-5'

# ── id 3: bate y pelota vistos desde arriba, más las 4 opciones ──────────────
# El bate se dibuja numéricamente: un eje del barril al mango y un medio ancho que
# disminuye a lo largo de él. El contorno se cierra recorriendo un lado, dando la
# vuelta por el casquete del mango, volviendo por el otro lado y cerrando por el
# casquete del barril. Los casquetes se generan como puntos, no como arcos: con
# arcos hay que acertarle a la bandera de barrido y un error deja un pico.
W3, H3 = 360, 260
BARRIL, MANGO = (196, 46), (232, 232)
T_GOLPE = 0.17                    # dónde toca la pelota, a lo largo del bate
R_PELOTA = 27

def _eje():
    (x0, y0), (x1, y1) = BARRIL, MANGO
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L      # a lo largo del bate
    return (x0, y0), L, (ux, uy), (-uy, ux)    # el último es el normal izquierdo

def _ancho(t):                                 # barril grueso, mango fino
    return 19.0 - 12.5 * t ** 0.62

def bate():
    (x0, y0), L, (ux, uy), (nx, ny) = _eje()
    izq, der = [], []
    for i in range(41):
        t = i / 40
        cx, cy = x0 + ux * L * t, y0 + uy * L * t
        izq.append((cx + nx * _ancho(t), cy + ny * _ancho(t)))
        der.append((cx - nx * _ancho(t), cy - ny * _ancho(t)))
    th = math.atan2(ny, nx)
    def casquete(c, r, desde):
        # El medio giro va en sentido DECRECIENTE: es el único que abomba el
        # casquete hacia afuera del bate. Al revés, se mete y deja un cuerno.
        return [(c[0] + r * math.cos(desde - math.pi * k / 12),
                 c[1] + r * math.sin(desde - math.pi * k / 12)) for k in range(1, 12)]
    knob = (x0 + ux * L, y0 + uy * L)
    pts = izq + casquete(knob, _ancho(1), th) + list(reversed(der)) \
        + casquete((x0, y0), _ancho(0), th + math.pi)
    d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'
    return (f'<path d="{d}" fill="currentColor" fill-opacity="0.14" '
            f'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>')

# La pelota se apoya sobre el costado izquierdo del bate, en el punto de golpe.
def _centro_pelota():
    (x0, y0), L, (ux, uy), (nx, ny) = _eje()
    cx, cy = x0 + ux * L * T_GOLPE, y0 + uy * L * T_GOLPE
    d = _ancho(T_GOLPE) + R_PELOTA - 2        # −2 para que se vean en contacto
    return cx + nx * d, cy + ny * d
C_PELOTA = _centro_pelota()

def escena3(extra=()):
    px, py = C_PELOTA
    c = [bate(),
         f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{R_PELOTA}" fill="currentColor" '
         f'fill-opacity="0.14" stroke="currentColor" stroke-width="2"/>',
         # costuras, para que se lea como pelota y no como disco
         f'<path d="M {px-19:.1f} {py-18:.1f} Q {px-5:.1f} {py:.1f} {px-19:.1f} {py+18:.1f}" '
         f'fill="none" stroke="currentColor" stroke-width="1.4"/>',
         f'<path d="M {px+19:.1f} {py-18:.1f} Q {px+5:.1f} {py:.1f} {px+19:.1f} {py+18:.1f}" '
         f'fill="none" stroke="currentColor" stroke-width="1.4"/>']
    return c + list(extra)

def fig3_enunciado():
    return svg(W3, H3, escena3(), 'Bate golpeando una pelota, visto desde arriba (sin vectores)')

# (largo sobre la pelota, largo sobre el bate, ¿apuntan hacia adentro?)
OPCIONES3 = {
    'A': (58, 58, False),    # iguales y opuestas: la Tercera Ley
    'B': (98, 46, False),    # opuestas pero desiguales
    'C': (58, 58, True),     # apuntan una hacia la otra
    'D': (46, 98, False),    # opuestas y desiguales, al revés que B
}

def fig3_opcion(k):
    lp, lb, adentro = OPCIONES3[k]
    y = C_PELOTA[1]
    # Las flechas arrancan en el borde de cada cuerpo y salen hacia afuera, para
    # que nunca se encimen con el bate, con la pelota ni entre ellas.
    bpel = C_PELOTA[0] - R_PELOTA - 4          # borde izquierdo de la pelota
    (x0, y0), L, (ux, uy), (nx, ny) = _eje()
    t = (y - y0) / (uy * L)
    bbat = x0 + ux * L * t - nx * _ancho(t) + 6   # borde derecho del bate a esa altura

    c = escena3()
    for x_borde, largo, sub, hacia_afuera in ((bpel, lp, 'B/P', -1), (bbat, lb, 'P/B', +1)):
        x_lejos = x_borde + hacia_afuera * largo
        if adentro:
            c += flecha(x_lejos, y, x_borde, y)
        else:
            c += flecha(x_borde, y, x_lejos, y)
        c.append(fuerza((x_borde + x_lejos) / 2, y - 13, sub))
    return svg(W3, H3, c, f'Opción {k}: fuerzas sobre la pelota y sobre el bate')

# ── id 9: carga +Q al centro y 12 cargas +q sobre la circunferencia ──────────
def fig9():
    W = H = 330
    cx = cy = W / 2
    R = 108
    c = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="currentColor" '
         f'stroke-width="1.6" stroke-opacity="0.55"/>',
         f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="currentColor"/>',
         f'<text x="{cx+13}" y="{cy-9}" font-size="17">+<tspan font-style="italic">Q</tspan></text>']
    for k in range(12):
        a = math.radians(90 - 30 * k)          # arranca arriba y gira cada 30°
        x, y = cx + R * math.cos(a), cy - R * math.sin(a)
        c.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="currentColor"/>')
        # el rótulo se empuja hacia afuera siguiendo el propio radio
        lx, ly = cx + (R + 22) * math.cos(a), cy - (R + 22) * math.sin(a)
        c.append(f'<text x="{lx:.1f}" y="{ly+5:.1f}" font-size="14" text-anchor="middle">'
                 f'+<tspan font-style="italic">q</tspan></text>')
    # el radio R, hacia abajo y a la izquierda
    a = math.radians(210)
    fx, fy = cx + R * math.cos(a), cy - R * math.sin(a)
    c += flecha(cx, cy, fx, fy, grosor=1.8, punta=8)
    # la etiqueta se corre perpendicular al radio para no montarse sobre el trazo
    mx, my = (cx + fx) / 2, (cy + fy) / 2
    c.append(f'<text x="{mx-math.sin(a)*17:.0f}" y="{my-math.cos(a)*17+6:.0f}" font-size="17" '
             f'font-style="italic" text-anchor="middle">R</text>')
    return svg(W, H, c, 'Carga +Q en el centro y 12 cargas +q equidistantes sobre el círculo')

# ── id 11: un solo lazo, pila V y resistor R/2 ──────────────────────────────
def fig11():
    W, H = 330, 210
    xi, xd, ya, yb = 66, 268, 52, 168
    py1, py2 = 100, 112
    c = ['  <g stroke="currentColor" stroke-width="1.8" fill="none">',
         '    <!-- Pila: placa larga (+) arriba, corta abajo; el cable se corta aquí -->',
         f'    <line x1="{xi-15}" y1="{py1}" x2="{xi+15}" y2="{py1}"/>',
         f'    <line x1="{xi-8}" y1="{py2}" x2="{xi+8}" y2="{py2}"/>',
         f'    <line x1="{xi}" y1="{ya}" x2="{xi}" y2="{py1}"/>',
         f'    <line x1="{xi}" y1="{py2}" x2="{xi}" y2="{yb}"/>',
         f'    <line x1="{xi}" y1="{ya}" x2="{xd}" y2="{ya}"/>',
         f'    <line x1="{xi}" y1="{yb}" x2="{xd}" y2="{yb}"/>',
         '    <!-- Lado derecho, interrumpido donde va el resistor -->',
         f'    <line x1="{xd}" y1="{ya}" x2="{xd}" y2="{(ya+yb)//2-23}"/>',
         f'    <line x1="{xd}" y1="{(ya+yb)//2+23}" x2="{xd}" y2="{yb}"/>',
         f'    <path d="{zig(xd, (ya+yb)//2, largo=46, vertical=True)}"/>',
         '  </g>',
         f'  <text x="{xi-24}" y="{py1+9}" font-size="18" font-style="italic" text-anchor="end">V</text>',
         f'  <text x="{xi+21}" y="{py1-6}" font-size="16">+</text>',
         f'  <text x="{xd+26}" y="{(ya+yb)//2+2}" font-size="17" font-style="italic">R</text>',
         f'  <line x1="{xd+22}" y1="{(ya+yb)//2+8}" x2="{xd+38}" y2="{(ya+yb)//2+8}" '
         f'stroke="currentColor" stroke-width="1.4"/>',
         f'  <text x="{xd+30}" y="{(ya+yb)//2+26}" font-size="17" text-anchor="middle">2</text>']
    return svg(W, H, c, 'Circuito serie de un lazo: pila V y resistor R/2')

# ── id 12: R1 en serie con R2 ∥ R3 ──────────────────────────────────────────
def fig12():
    W, H = 474, 230
    xi, xa, xb = 62, 258, 348
    ya, yb = 54, 186
    py1, py2 = 112, 124
    ym = (ya + yb) // 2
    c = ['  <g stroke="currentColor" stroke-width="1.8" fill="none">',
         '    <!-- Fuente de 6 V -->',
         f'    <line x1="{xi-15}" y1="{py1}" x2="{xi+15}" y2="{py1}"/>',
         f'    <line x1="{xi-8}" y1="{py2}" x2="{xi+8}" y2="{py2}"/>',
         f'    <line x1="{xi}" y1="{ya}" x2="{xi}" y2="{py1}"/>',
         f'    <line x1="{xi}" y1="{py2}" x2="{xi}" y2="{yb}"/>',
         '    <!-- Rail superior con R1 en serie -->',
         f'    <line x1="{xi}" y1="{ya}" x2="{(xi+xa)//2-25}" y2="{ya}"/>',
         f'    <line x1="{(xi+xa)//2+25}" y1="{ya}" x2="{xb}" y2="{ya}"/>',
         f'    <path d="{zig((xi+xa)//2, ya)}"/>',
         f'    <line x1="{xi}" y1="{yb}" x2="{xb}" y2="{yb}"/>',
         '    <!-- Las dos ramas en paralelo: R2 y R3 -->']
    for x in (xa, xb):
        c += [f'    <line x1="{x}" y1="{ya}" x2="{x}" y2="{ym-23}"/>',
              f'    <line x1="{x}" y1="{ym+23}" x2="{x}" y2="{yb}"/>',
              f'    <path d="{zig(x, ym, largo=46, vertical=True)}"/>']
    c += ['  </g>',
          f'  <text x="{xi-24}" y="{py1+9}" font-size="18" text-anchor="end">6 V</text>',
          f'  <text x="{xi+21}" y="{py1-6}" font-size="16">+</text>',
          f'  <text x="{(xi+xa)//2}" y="{ya-20}" font-size="17" text-anchor="middle">'
          f'<tspan font-style="italic">R</tspan><tspan font-size="12" dy="4">1</tspan>'
          f'<tspan dy="-4"> = 2 Ω</tspan></text>',
          f'  <text x="{xa-30}" y="{ym+6}" font-size="17" text-anchor="end">'
          f'<tspan font-style="italic">R</tspan><tspan font-size="12" dy="4">2</tspan>'
          f'<tspan dy="-4"> = 4 Ω</tspan></text>',
          f'  <text x="{xb+30}" y="{ym+6}" font-size="17">'
          f'<tspan font-style="italic">R</tspan><tspan font-size="12" dy="4">3</tspan>'
          f'<tspan dy="-4"> = 6 Ω</tspan></text>']
    return svg(W, H, c, 'R1 en serie con la combinación paralelo de R2 y R3')

# ── id 13: tres recipientes cúbicos idénticos ───────────────────────────────
def fig13():
    lado, p = 84, 30                 # arista y desplazamiento de la perspectiva
    W, H = 3 * (lado + p) + 110, lado + p + 78
    c = []
    for k, nom in enumerate('ABC'):
        x = 40 + k * (lado + p + 26)
        y = 30 + p
        # cara frontal
        c.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" fill="currentColor" '
                 f'fill-opacity="0.09" stroke="currentColor" stroke-width="2"/>')
        # cara superior y lateral, en perspectiva
        c.append(f'<path d="M {x} {y} L {x+p} {y-p} L {x+lado+p} {y-p} L {x+lado} {y} Z" '
                 f'fill="currentColor" fill-opacity="0.05" stroke="currentColor" stroke-width="2"/>')
        c.append(f'<path d="M {x+lado} {y} L {x+lado+p} {y-p} L {x+lado+p} {y+lado-p} '
                 f'L {x+lado} {y+lado} Z" fill="currentColor" fill-opacity="0.14" '
                 f'stroke="currentColor" stroke-width="2"/>')
        # aristas ocultas
        for d in (f'M {x} {y+lado} L {x+p} {y+lado-p} L {x+lado+p} {y+lado-p}',
                  f'M {x+p} {y+lado-p} L {x+p} {y-p}'):
            c.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.2" '
                     f'stroke-dasharray="5 4" stroke-opacity="0.6"/>')
        c.append(f'<text x="{x+(lado+p)//2}" y="{y+lado+30}" font-size="20" font-weight="600" '
                 f'text-anchor="middle">{nom}</text>')
    return svg(W, H, c, 'Tres recipientes cúbicos idénticos rotulados A, B y C')

# ── id 60: segmento de P(-4,-7) a P(4, 9) ──────────────────────────────────
def fig60():
    u = 21
    ox, oy = 30 + 8 * u, 30 + 10 * u
    W, H = ox + 8 * u + 46, oy + 8 * u + 40
    def px(x, y): return ox + x * u, oy - y * u
    c = []
    for i in range(-8, 9):           # cuadrícula suave
        c.append(f'<line x1="{ox+i*u}" y1="{oy-10*u}" x2="{ox+i*u}" y2="{oy+8*u}" '
                 f'stroke="currentColor" stroke-width="0.6" stroke-opacity="0.12"/>')
    for j in range(-8, 11):
        c.append(f'<line x1="{ox-8*u}" y1="{oy-j*u}" x2="{ox+8*u}" y2="{oy-j*u}" '
                 f'stroke="currentColor" stroke-width="0.6" stroke-opacity="0.12"/>')
    c += [f'<line x1="{ox-8*u-14}" y1="{oy}" x2="{ox+8*u+14}" y2="{oy}" stroke="currentColor" stroke-width="1.8"/>',
          f'<line x1="{ox}" y1="{oy+8*u+14}" x2="{ox}" y2="{oy-10*u-14}" stroke="currentColor" stroke-width="1.8"/>',
          f'<text x="{ox+8*u+22}" y="{oy+18}" font-size="15" font-style="italic">x</text>',
          f'<text x="{ox+12}" y="{oy-10*u-16}" font-size="15" font-style="italic">y</text>',
          f'<text x="{ox-10}" y="{oy+17}" font-size="12" text-anchor="end">0</text>']
    for i in (-8, -6, -4, -2, 2, 4, 6, 8):
        c.append(f'<line x1="{ox+i*u}" y1="{oy-4}" x2="{ox+i*u}" y2="{oy+4}" stroke="currentColor" stroke-width="1.2"/>')
        c.append(f'<text x="{ox+i*u}" y="{oy+18}" font-size="12" text-anchor="middle">{i}</text>')
    for j in (-8, -6, -4, -2, 2, 4, 6, 8, 10):
        c.append(f'<line x1="{ox-4}" y1="{oy-j*u}" x2="{ox+4}" y2="{oy-j*u}" stroke="currentColor" stroke-width="1.2"/>')
        c.append(f'<text x="{ox-8}" y="{oy-j*u+5}" font-size="12" text-anchor="end">{j}</text>')
    a, b = px(-4, -7), px(4, 9)
    c.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="currentColor" stroke-width="2.8"/>')
    for (p, t, dx, dy, an) in ((a, 'P (−4, −7)', -10, 18, 'end'), (b, 'P (4, 9)', 12, -8, 'start')):
        c.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="4.2" fill="currentColor"/>')
        c.append(f'<text x="{p[0]+dx}" y="{p[1]+dy}" font-size="14" text-anchor="{an}">{t}</text>')
    return svg(W, H, c, 'Segmento de P(−4,−7) a P(4,9): pendiente 2')

# ── id 69: f(x) con máximo en x=2 y mínimo en x=4 ───────────────────────────
def fig69():
    W, H = 380, 290
    ox, oy = 56, 236
    ux, uy = 44, 15.5
    f = lambda x: x**3 / 3 - 3 * x**2 + 8 * x      # f'(x) = (x−2)(x−4)
    c = [f'<line x1="{ox-16}" y1="{oy}" x2="{ox+6.9*ux:.0f}" y2="{oy}" stroke="currentColor" stroke-width="1.8"/>',
         f'<line x1="{ox}" y1="{oy+18}" x2="{ox}" y2="26" stroke="currentColor" stroke-width="1.8"/>',
         f'<path d="M {ox+6.9*ux:.0f} {oy} l -8 -4 l 0 8 z" fill="currentColor"/>',
         f'<path d="M {ox} 26 l -4 8 l 8 0 z" fill="currentColor"/>',
         f'<text x="{ox+6.9*ux+10:.0f}" y="{oy+18}" font-size="15" font-style="italic">x</text>',
         f'<text x="{ox+12}" y="34" font-size="15" font-style="italic">y</text>']
    for v in (0, 2, 4, 6):
        x = ox + v * ux
        if v:
            c.append(f'<line x1="{x}" y1="{oy-4}" x2="{x}" y2="{oy+4}" stroke="currentColor" stroke-width="1.3"/>')
        c.append(f'<text x="{x if v else ox-10}" y="{oy+20}" font-size="14" '
                 f'text-anchor="{"middle" if v else "end"}">{v}</text>')
    pts = [f'{ox+x*ux:.1f},{oy-f(x)*uy:.1f}' for x in [i / 40 for i in range(0, 261)]]
    c.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="2.6"/>')
    for v in (2, 6):           # guías punteadas de la curva al eje
        x, y = ox + v * ux, oy - f(v) * uy
        c.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{oy}" stroke="currentColor" '
                 f'stroke-width="1.1" stroke-dasharray="4 3" stroke-opacity="0.6"/>')
    return svg(W, H, c, 'f(x) con máximo local en x=2 y mínimo local en x=4')

os.makedirs(OUT, exist_ok=True)
figs = [('q3_bate_pelota', fig3_enunciado), ('q9_cargas', fig9), ('q11_circuito', fig11),
        ('q12_circuito', fig12), ('q13_recipientes', fig13), ('q60_recta', fig60),
        ('q69_grafica', fig69)]
figs += [(f'q3_op{k}', (lambda k=k: fig3_opcion(k))) for k in 'ABCD']
for nombre, fn in figs:
    open(os.path.join(OUT, nombre + '.svg'), 'w').write(fn())
    print('escrito', nombre + '.svg')
