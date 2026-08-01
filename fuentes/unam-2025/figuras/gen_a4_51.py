# unam-a4-5 id 51 — triángulo rectángulo 3-4-5 para el seno del ángulo P.
# Q = ángulo recto (abajo-izq), R = arriba, P = abajo-der.
import os, math

E = 62                      # píxeles por unidad
IZQ, ARR = 62, 46           # margen para la acotación del 3 y la etiqueta R
Q = (IZQ, ARR + 3 * E)      # (0,0) del triángulo
R = (IZQ, ARR)              # cateto vertical 3
P = (IZQ + 4 * E, ARR + 3 * E)   # cateto horizontal 4
W, H = P[0] + 46, Q[1] + 62

s = [f'<svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
     f'width="{W}" height="{H}" font-family="\'Latin Modern Roman\', Georgia, serif">',
     '<!-- Triángulo rectángulo 3-4-5: Q ángulo recto, R arriba, P abajo-derecha -->']

# el triángulo, con un tinte que se adapta al tema
s.append(f'<path d="M {Q[0]} {Q[1]} L {R[0]} {R[1]} L {P[0]} {P[1]} Z" '
         f'fill="currentColor" fill-opacity="0.09" stroke="currentColor" stroke-width="2.2"/>')

# ángulo recto en Q
m = 18
s.append(f'<path d="M {Q[0]+m} {Q[1]} L {Q[0]+m} {Q[1]-m} L {Q[0]} {Q[1]-m}" '
         f'fill="none" stroke="currentColor" stroke-width="1.6"/>')

# arco del ángulo P, entre el cateto horizontal y la hipotenusa
r = 40
ang = math.atan2(R[1] - P[1], R[0] - P[0])          # dirección P->R
x2, y2 = P[0] + r * math.cos(ang), P[1] + r * math.sin(ang)
s.append(f'<path d="M {P[0]-r} {P[1]} A {r} {r} 0 0 1 {x2:.1f} {y2:.1f}" '
         f'fill="none" stroke="currentColor" stroke-width="1.6"/>')

# vértices
s.append(f'<text x="{Q[0]-14}" y="{Q[1]+20}" font-size="19" font-style="italic" text-anchor="middle">Q</text>')
s.append(f'<text x="{R[0]}" y="{R[1]-12}" font-size="19" font-style="italic" '
         f'text-anchor="middle">R</text>')
s.append(f'<text x="{P[0]+16}" y="{P[1]+7}" font-size="19" font-style="italic">P</text>')

# acotación del cateto vertical (3), a la izquierda
ax = IZQ - 26
s.append(f'<line x1="{ax}" y1="{R[1]}" x2="{ax}" y2="{Q[1]}" stroke="currentColor" stroke-width="1.3"/>')
for y in (R[1], Q[1]):
    s.append(f'<line x1="{ax-6}" y1="{y}" x2="{ax+6}" y2="{y}" stroke="currentColor" stroke-width="1.3"/>')
s.append(f'<text x="{ax-11}" y="{(R[1]+Q[1])//2+6}" font-size="18" text-anchor="middle">3</text>')

# acotación del cateto horizontal (4), abajo
ay = Q[1] + 28
s.append(f'<line x1="{Q[0]}" y1="{ay}" x2="{P[0]}" y2="{ay}" stroke="currentColor" stroke-width="1.3"/>')
for x in (Q[0], P[0]):
    s.append(f'<line x1="{x}" y1="{ay-6}" x2="{x}" y2="{ay+6}" stroke="currentColor" stroke-width="1.3"/>')
s.append(f'<text x="{(Q[0]+P[0])//2}" y="{ay+22}" font-size="18" text-anchor="middle">4</text>')

# el 5 sobre la hipotenusa, girado con ella y desplazado hacia afuera
mx, my = (R[0] + P[0]) / 2, (R[1] + P[1]) / 2
gr = math.degrees(math.atan2(P[1] - R[1], P[0] - R[0]))
s.append(f'<text x="{mx:.0f}" y="{my-12:.0f}" font-size="18" text-anchor="middle" '
         f'transform="rotate({gr:.1f} {mx:.0f} {my-12:.0f})">5</text>')
s.append('</svg>')

out = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a4-5'
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'q51_triangulo.svg'), 'w').write('\n'.join(s) + '\n')
print('escrito q51_triangulo.svg')
