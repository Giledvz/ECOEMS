# Figuras de la lectura sobre la proporción áurea (ipn-iycfm-1).
#
# La lectura viene ilustrada en la guía y sin esas figuras no se entiende: se
# redibujan como SVG para que se adapten al tema claro/oscuro de la plataforma.
#
#   python3 fuentes/ipn/scripts/generar-figuras-aurea.py
#
# Escribe en public/imagenes_ipn-iycfm-1/.
import math, os

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_ipn-iycfm-1'
FONT = "'Latin Modern Roman', Georgia, 'Times New Roman', serif"

def head(w, h, vb):
    return (f'<svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{w}" height="{h}" font-family="{FONT}">\n')

# ---------------------------------------------------------------- 1. construcción
# A(60,200) B(190,200) C(190,70)  AB = BC = 1 (130 px)
A = (60, 200); B = (190, 200); C = (190, 70)
O = (190, 135); r = 65
dx, dy = O[0]-A[0], O[1]-A[1]
L = math.hypot(dx, dy)
P = (O[0] + r*dx/L, O[1] + r*dy/L)
# la recta se prolonga un poco más allá de P
E = (O[0] + (r+26)*dx/L, O[1] + (r+26)*dy/L)

s = ['<!-- Razón áurea: AB=BC=1, circunferencia de radio 1/2 con centro en O; AP/AB = phi -->']
s.append(f'<line x1="{A[0]}" y1="{A[1]}" x2="{E[0]:.2f}" y2="{E[1]:.2f}" stroke="currentColor" stroke-width="1.4"/>')
s.append(f'<line x1="{A[0]}" y1="{A[1]}" x2="{B[0]}" y2="{B[1]}" stroke="currentColor" stroke-width="1.6"/>')
s.append(f'<line x1="{B[0]}" y1="{B[1]}" x2="{C[0]}" y2="{C[1]}" stroke="currentColor" stroke-width="1.6"/>')
s.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="{r}" fill="none" stroke="currentColor" stroke-width="1.1"/>')
for (px, py) in (A, B, C, O, P):
    s.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.6" fill="currentColor"/>')
lab = [(A[0]-4, A[1]+18, 'A'), (B[0]+2, B[1]+18, 'B'), (C[0]+2, C[1]-9, 'C'),
       (O[0]-16, O[1]+5, 'O'), (P[0]-2, P[1]-11, 'P')]
for x, y, t in lab:
    s.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="15" font-style="italic" fill="currentColor">{t}</text>')
s.append(f'<text x="{(A[0]+B[0])/2-4}" y="{A[1]+18}" font-size="14" fill="currentColor">1</text>')
s.append(f'<text x="{O[0]-30}" y="{(O[1]+B[1])/2+5}" font-size="14" fill="currentColor">½</text>')
open(os.path.join(OUT, 'lectura1_construccion.svg'), 'w').write(
    head(300, 250, '20 40 280 200') + '\n'.join(s) + '\n</svg>\n')

# ---------------------------------------------------------------- 2. rectángulo dorado
a = 140.0
b = a / ((1 + 5 ** 0.5) / 2)          # 86.52
x0, y0 = 40, 40
s = ['<!-- Rectángulo dorado: cuadrado de lado a + rectángulo semejante de base b -->']
s.append(f'<rect x="{x0}" y="{y0}" width="{a}" height="{a}" fill="currentColor" fill-opacity="0.10" stroke="currentColor" stroke-width="1.6"/>')
s.append(f'<rect x="{x0+a}" y="{y0}" width="{b:.2f}" height="{a}" fill="currentColor" fill-opacity="0.22" stroke="currentColor" stroke-width="1.6"/>')
s.append(f'<text x="{x0+a/2-5}" y="{y0-12}" font-size="17" font-style="italic" fill="currentColor">a</text>')
s.append(f'<text x="{x0+a+b/2-5:.2f}" y="{y0-12}" font-size="17" font-style="italic" fill="currentColor">b</text>')
s.append(f'<text x="{x0-20}" y="{y0+a/2+6}" font-size="17" font-style="italic" fill="currentColor">a</text>')
# llave inferior
by = y0 + a + 14
s.append(f'<path d="M {x0} {by} v 8 H {x0+a+b:.2f} v -8" fill="none" stroke="currentColor" stroke-width="1.2"/>')
s.append(f'<path d="M {x0+(a+b)/2:.2f} {by+8} v 8" fill="none" stroke="currentColor" stroke-width="1.2"/>')
s.append(f'<text x="{x0+(a+b)/2-22:.2f}" y="{by+32}" font-size="17" font-style="italic" fill="currentColor">a+b</text>')
open(os.path.join(OUT, 'lectura1_rectangulo.svg'), 'w').write(
    head(320, 250, '10 10 290 225') + '\n'.join(s) + '\n</svg>\n')

# ---------------------------------------------------------------- 3. espiral áurea
x, y, w, h = 10.0, 10.0, 233.0, 144.0
order = ['left', 'top', 'right', 'bottom']
squares, arcs = [], []
i = 0
while min(w, h) > 4:
    sd = min(w, h)
    d = order[i % 4]
    if d == 'left':
        sq = (x, y, sd); c = (x+sd, y+sd); p0 = (x, y+sd); p1 = (x+sd, y); x += sd; w -= sd
    elif d == 'top':
        sq = (x, y, sd); c = (x, y+sd); p0 = (x, y); p1 = (x+sd, y+sd); y += sd; h -= sd
    elif d == 'right':
        sq = (x+w-sd, y, sd); c = (sq[0], y); p0 = (sq[0]+sd, y); p1 = (sq[0], y+sd); w -= sd
    else:
        sq = (x, y+h-sd, sd); c = (x+sd, sq[1]); p0 = (x+sd, sq[1]+sd); p1 = (x, sq[1]); h -= sd
    squares.append(sq); arcs.append((p0, p1, sd, c))
    i += 1

s = ['<!-- Espiral áurea sobre cuadrados anidados (233x144) -->']
for (sx, sy, sd) in squares:
    s.append(f'<rect x="{sx:.2f}" y="{sy:.2f}" width="{sd:.2f}" height="{sd:.2f}" fill="none" stroke="currentColor" stroke-width="0.9" stroke-opacity="0.45"/>')
# la espiral se dibuja del cuadrado mayor al menor; los arcos ya empatan extremo con extremo
d = f'M {arcs[0][0][0]:.2f} {arcs[0][0][1]:.2f}'
for (p0, p1, rad, c) in arcs:
    z = (p0[0]-c[0])*(p1[1]-c[1]) - (p0[1]-c[1])*(p1[0]-c[0])
    sweep = 1 if z > 0 else 0
    d += f' A {rad:.2f} {rad:.2f} 0 0 {sweep} {p1[0]:.2f} {p1[1]:.2f}'
s.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2"/>')
open(os.path.join(OUT, 'lectura1_espiral.svg'), 'w').write(
    head(340, 220, '0 0 253 164') + '\n'.join(s) + '\n</svg>\n')

print('escritos 3 SVG en', OUT)
