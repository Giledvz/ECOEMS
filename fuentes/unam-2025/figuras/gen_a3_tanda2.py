# unam-a3-5 — segunda tanda: ids 5, 8, 10 y 51. Cierra las figuras del Área 3.
import os, math

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a3-5'
FONT = "'Latin Modern Roman', Georgia, serif"

def svg(w, h, c, com=''):
    return (f'<svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">\n'
            + (f'<!-- {com} -->\n' if com else '') + '\n'.join(c) + '\n</svg>\n')

def hachura(x1, x2, y, alto=10, paso=11, arriba=False):
    """Rayado de superficie fija: la línea más los trazos inclinados."""
    o = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="currentColor" stroke-width="2.2"/>']
    d = -alto if arriba else alto
    x = x1
    while x < x2:
        o.append(f'<line x1="{x}" y1="{y}" x2="{x-8}" y2="{y+d}" stroke="currentColor" stroke-width="1.1"/>')
        x += paso
    return o

# ── id 5: bola A choca contra bola B en reposo ──────────────────────────────
def fig5():
    W, H, sy = 400, 190, 132
    c = hachura(20, W-20, sy)
    c += [f'<circle cx="118" cy="{sy-17}" r="17" fill="currentColor"/>',
          f'<text x="118" y="{sy+26}" font-size="18" font-weight="600" text-anchor="middle">A</text>',
          f'<circle cx="272" cy="{sy-25}" r="25" fill="currentColor"/>',
          f'<text x="272" y="{sy+26}" font-size="18" font-weight="600" text-anchor="middle">B</text>',
          # flecha de velocidad sobre A
          f'<line x1="145" y1="{sy-52}" x2="205" y2="{sy-52}" stroke="currentColor" stroke-width="2.4"/>',
          f'<path d="M 209 {sy-52} l -9 -5 l 0 10 z" fill="currentColor"/>',
          f'<text x="175" y="{sy-62}" font-size="17" font-style="italic" text-anchor="middle">V</text>',
          f'<text x="187" y="{sy-58}" font-size="12" font-style="italic">A</text>']
    return svg(W, H, c, 'Bola A (pequeña) con velocidad V_A choca contra B (mayor) en reposo')

# ── id 8: cuerda con 5 ciclos entre vibrador y pared, 90 cm ─────────────────
def fig8():
    W, H = 470, 210
    x1, x2, ejeY = 78, 400, 92
    # vibrador: cono esbelto y picudo, del que sale la cuerda
    c = [f'<path d="M {x1-22} {ejeY} L {x1} {ejeY-11} L {x1} {ejeY+11} Z" fill="currentColor"/>']
    # pared fija a la derecha
    c.append(f'<line x1="{x2}" y1="{ejeY-46}" x2="{x2}" y2="{ejeY+46}" stroke="currentColor" stroke-width="2.6"/>')
    y = ejeY - 46
    while y < ejeY + 46:
        c.append(f'<line x1="{x2}" y1="{y}" x2="{x2+11}" y2="{y+9}" stroke="currentColor" stroke-width="1.1"/>')
        y += 11
    # onda: 5 ciclos completos
    pts = []
    for i in range(0, 401):
        t = i / 400
        x = x1 + t * (x2 - x1)
        yy = ejeY - 32 * math.sin(2 * math.pi * 5 * t)
        pts.append(f'{x:.1f},{yy:.1f}')
    c.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="2.4"/>')
    # acotación de 90 cm
    ay = ejeY + 68
    c.append(f'<line x1="{x1}" y1="{ay}" x2="{x2}" y2="{ay}" stroke="currentColor" stroke-width="1.2" '
             f'stroke-dasharray="5 4"/>')
    for x in (x1, x2):
        c.append(f'<line x1="{x}" y1="{ay-6}" x2="{x}" y2="{ay+6}" stroke="currentColor" stroke-width="1.2"/>')
    c.append(f'<text x="{(x1+x2)//2}" y="{ay+24}" font-size="17" font-weight="600" text-anchor="middle">90 cm</text>')
    return svg(W, H, c, 'Cuerda con 5 ciclos completos en 90 cm entre el vibrador y la pared fija')

# ── id 10: circuito con dos mallas; 2R queda en rama sin fuente ─────────────
def fig10():
    """Misma convención que public/imagenes_ecoems-6/q37_circuito_paralelo.svg:
    trazo de 1.8, todo dentro de un <g>, y el cable INTERRUMPIDO en las placas de la
    pila y en los zigzag, en vez de pasar por detrás."""
    W, H = 400, 230
    xi, xd, xm = 62, 340, 200
    ya, yb = 52, 178
    py1, py2 = 106, 118          # placas de la pila
    rA, rB, anc = (xi + xm) / 2, (xm + xd) / 2, 46

    def zig(x, y, ancho=anc, alto=10, n=6):
        p = [f'M {x-ancho/2},{y}']
        paso = ancho / n
        for i in range(n):
            p.append(f'L {x-ancho/2+paso*(i+0.5):.0f},{y+(alto if i%2==0 else -alto)}')
        p.append(f'L {x+ancho/2},{y}')
        return f'    <path d="{" ".join(p)}"/>'

    c = ['  <g stroke="currentColor" stroke-width="1.8" fill="none">',
         '    <!-- Pila: placa larga arriba (+), corta abajo (−); el cable se corta aquí -->',
         f'    <line x1="{xi-15}" y1="{py1}" x2="{xi+15}" y2="{py1}"/>',
         f'    <line x1="{xi-8}" y1="{py2}" x2="{xi+8}" y2="{py2}"/>',
         '    <!-- Lado izquierdo, en dos tramos para no atravesar la pila -->',
         f'    <line x1="{xi}" y1="{ya}" x2="{xi}" y2="{py1}"/>',
         f'    <line x1="{xi}" y1="{py2}" x2="{xi}" y2="{yb}"/>',
         '    <!-- Rail superior, interrumpido donde va cada resistor -->',
         f'    <line x1="{xi}" y1="{ya}" x2="{rA-anc/2:.0f}" y2="{ya}"/>',
         f'    <line x1="{rA+anc/2:.0f}" y1="{ya}" x2="{rB-anc/2:.0f}" y2="{ya}"/>',
         f'    <line x1="{rB+anc/2:.0f}" y1="{ya}" x2="{xd}" y2="{ya}"/>',
         f'    <line x1="{xi}" y1="{yb}" x2="{xd}" y2="{yb}"/>',
         f'    <line x1="{xd}" y1="{ya}" x2="{xd}" y2="{yb}"/>',
         '    <!-- Rama central: deja 2R en una malla sin fuente -->',
         f'    <line x1="{xm}" y1="{ya}" x2="{xm}" y2="{yb}"/>',
         zig(rA, ya), zig(rB, ya),
         '  </g>',
         f'  <text x="{xi-24}" y="{py1+9}" font-size="18" font-style="italic" text-anchor="end">V</text>',
         f'  <text x="{rA:.0f}" y="{ya-20}" font-size="18" font-style="italic" text-anchor="middle">R</text>',
         f'  <text x="{rB:.0f}" y="{ya-20}" font-size="18" font-style="italic" text-anchor="middle">2R</text>',
         '  <!-- Corriente: bajo el rail inferior, que es el retorno hacia la pila -->',
         f'  <path d="M {xi+96} {yb+15} l -26 0" stroke="currentColor" stroke-width="1.4" fill="none"/>',
         f'  <path d="M {xi+66} {yb+15} l 6 -4 l 0 8 z" fill="currentColor"/>',
         f'  <text x="{xi+104}" y="{yb+20}" font-size="16" font-style="italic">3I</text>']
    return svg(W, H, c, 'Circuito: R en la malla de la pila, 2R en una malla sin fuente')

# ── id 51: cuatro gráficas I-IV ────────────────────────────────────────────
def fig51():
    cw, ch = 176, 150
    W, H = cw*4 + 30, ch + 46
    c = []
    curvas = {
      'I':   lambda t: 0.06*math.exp(3.1*t),                      # exponencial creciente
      'II':  lambda t: -(t**3)*1.15,                              # cúbica invertida, decreciente
      'III': lambda t: 2.2*t - 0.55,                              # recta de pendiente positiva
      'IV':  lambda t: 0.9 - 0.95*math.exp(2.2*(t-0.55)),         # decreciente, cae a la derecha
    }
    for k, (nom, f) in enumerate(curvas.items()):
        ox = 14 + k*cw + cw/2
        oy = 24 + ch/2
        ex, ey = cw*0.30, ch*0.30
        c += [f'<line x1="{ox-cw*0.42}" y1="{oy}" x2="{ox+cw*0.42}" y2="{oy}" stroke="currentColor" stroke-width="1.5"/>',
              f'<line x1="{ox}" y1="{oy+ch*0.42}" x2="{ox}" y2="{oy-ch*0.42}" stroke="currentColor" stroke-width="1.5"/>',
              f'<text x="{ox-11}" y="{oy+15}" font-size="12">0</text>',
              f'<text x="{ox}" y="{24+ch+22}" font-size="17" font-weight="600" text-anchor="middle">{nom}</text>']
        for i in (-1, 1):     # un par de marcas por eje
            c.append(f'<line x1="{ox+i*ex}" y1="{oy-4}" x2="{ox+i*ex}" y2="{oy+4}" stroke="currentColor" stroke-width="1.2"/>')
            c.append(f'<line x1="{ox-4}" y1="{oy+i*ey}" x2="{ox+4}" y2="{oy+i*ey}" stroke="currentColor" stroke-width="1.2"/>')
        pts=[]
        for i in range(121):
            t = -1.15 + 2.3*i/120
            v = f(t)
            if abs(v) > 1.45: continue
            pts.append(f'{ox+t*ex:.1f},{oy-v*ey:.1f}')
        c.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="2.4"/>')
    return svg(W, H, c, 'Cuatro gráficas: I exponencial creciente, II cúbica decreciente, '
                        'III recta creciente, IV decreciente')

os.makedirs(OUT, exist_ok=True)
for n, f in (('q5_choque', fig5), ('q8_onda', fig8), ('q10_circuito', fig10), ('q51_graficas', fig51)):
    open(os.path.join(OUT, n + '.svg'), 'w').write(f())
    print('escrito', n + '.svg')
