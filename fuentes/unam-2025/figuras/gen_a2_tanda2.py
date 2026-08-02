# unam-a2-5 — segunda tanda: id 35 (una fórmula por opción) y id 8 (difracción
# en la esquina de un edificio). Cierra las figuras del Área 2.
import os, math, sys

sys.path.insert(0, os.path.dirname(__file__))
from comun import svg, flecha

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a2-5'

# ── id 35: fórmulas semidesarrolladas, una por opción ───────────────────────
# Las cuatro figuras se dibujan del mismo tamaño para que las opciones queden
# parejas en pantalla; la fórmula va centrada dentro de ese lienzo.
W35, H35, FILA = 400, 150, 60
ANCHO = {'CH3': 38, 'CH2': 38, 'C': 13, 'O': 15, 'OH': 30,
         'NH2': 38, 'OCH2CH3': 92}
HUECO = 26

def quim(x, y, etq, tam=21):
    """Rótulo químico: los dígitos bajan como subíndice."""
    partes, i = [], 0
    while i < len(etq):
        if etq[i].isdigit():
            partes.append(f'<tspan font-size="{tam*0.68:.0f}" dy="{tam*0.24:.0f}">{etq[i]}</tspan>'
                          f'<tspan dy="{-tam*0.24:.0f}"></tspan>')
        else:
            partes.append(etq[i])
        i += 1
    return (f'<text x="{x}" y="{y}" font-size="{tam}" text-anchor="middle">'
            + ''.join(partes) + '</text>')

def fig35(cadena, doble=None):
    """cadena: lista de rótulos unidos por enlace simple.
    doble: índice del rótulo del que cuelga un doble enlace vertical hacia un O."""
    total = sum(ANCHO[e] for e in cadena) + HUECO * (len(cadena) - 1)
    x = (W35 - total) / 2
    c, centros = [], []
    for k, e in enumerate(cadena):
        cx = x + ANCHO[e] / 2
        centros.append(cx)
        c.append(quim(cx, FILA + 7, e))
        if k:                                   # enlace simple con el anterior
            c.append(f'<line x1="{x-HUECO+4}" y1="{FILA}" x2="{x-4}" y2="{FILA}" '
                     f'stroke="currentColor" stroke-width="2"/>')
        x += ANCHO[e] + HUECO
    if doble is not None:
        cx = centros[doble]
        for dx in (-4, 4):                      # doble enlace: dos trazos paralelos
            c.append(f'<line x1="{cx+dx}" y1="{FILA+14}" x2="{cx+dx}" y2="{FILA+46}" '
                     f'stroke="currentColor" stroke-width="2"/>')
        c.append(quim(cx, FILA + 70, 'O'))
    return svg(W35, H35, c, 'Fórmula semidesarrollada: ' + '-'.join(cadena))

OPCIONES35 = {
    'A': (['CH3', 'C', 'OH'], 1),          # ácido carboxílico
    'B': (['CH3', 'C', 'NH2'], 1),         # amida
    'C': (['CH3', 'CH2', 'CH3'], None),    # alcano
    'D': (['CH3', 'C', 'OCH2CH3'], 1),     # éster
}

# ── id 8: difracción del sonido en la esquina de un edificio ────────────────
# La guía la dibuja en perspectiva, pero así las ondas se montan sobre el muro y
# no se distingue qué queda a la sombra. En vista superior el recorte contra el
# muro es exacto y la esquina se lee de inmediato.
def persona(x, ypie, h=46):
    """Silueta sencilla: cabeza y torso. Basta para leer 'persona' sin
    convertir la figura en una ilustración."""
    r = h * 0.155
    cy = ypie - h + r
    return [f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="currentColor"/>',
            f'<path d="M {x-h*0.20:.0f} {ypie:.0f} L {x-h*0.20:.0f} {cy+r*1.9:.0f} '
            f'Q {x:.0f} {cy+r*0.85:.0f} {x+h*0.20:.0f} {cy+r*1.9:.0f} '
            f'L {x+h*0.20:.0f} {ypie:.0f} Z" fill="currentColor"/>']

def _arco(cx, cy, r, a1, a2, extra):
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    p2 = (cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2)))
    grande = 1 if abs(a2 - a1) > 180 else 0
    return (f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {r} {r} 0 {grande} 1 '
            f'{p2[0]:.1f} {p2[1]:.1f}" fill="none" {extra}/>')

def fig8():
    W, H = 520, 350
    # El muro en planta, en forma de L. La punta exterior es la esquina.
    xi, xd, yt, gr = 56, 316, 152, 16
    T = (xd, yt)                       # arista de la esquina
    S = (170, 92)                      # de dónde sale la voz
    # El límite entre lo iluminado y la sombra es el rayo que sale de S y pasa
    # rozando la arista T: más allá de esa recta, el muro tapa el sonido directo.
    m = (T[1] - S[1]) / (T[0] - S[0])
    yb = S[1] + (W - S[0]) * m               # dónde corta ese rayo el borde derecho
    c = ['<defs>',
         # iluminado: delante del muro hasta la arista, y de ahí arriba del rayo
         f'<clipPath id="libre"><polygon points="0,0 {W},0 {W},{yb:.0f} '
         f'{xd},{yt} 0,{yt}"/></clipPath>',
         # sombra acústica: sólo se llega ahí doblando la esquina
         f'<clipPath id="sombra"><polygon points="{xd},{yt} {W},{yb:.0f} {W},{H} '
         f'{xd},{H}"/></clipPath>',
         '</defs>',
         f'<path d="M {xi} {yt} L {xd} {yt} L {xd} {H-30} L {xd-gr} {H-30} '
         f'L {xd-gr} {yt+gr} L {xi} {yt+gr} Z" fill="currentColor" fill-opacity="0.30" '
         f'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>']

    # Frentes de onda directos: se recortan solos contra el muro.
    c.append('<g clip-path="url(#libre)">')
    for k in range(1, 8):
        c.append(_arco(S[0], S[1], 34 + 30 * k, -105, 58,
                       'stroke="currentColor" stroke-width="1.5" stroke-opacity="0.7"'))
    c.append('</g>')

    # Al llegar a la arista, ésta actúa como fuente nueva: la onda dobla la
    # esquina y entra en la sombra. Eso es la difracción.
    c.append('<g clip-path="url(#sombra)">')
    for k in range(1, 7):
        c.append(_arco(T[0], T[1], 24 + 30 * k, 0, 90,
                       'stroke="currentColor" stroke-width="1.5" stroke-dasharray="7 4" '
                       'stroke-opacity="0.85"'))
    c.append('</g>')

    # Dos rayos rectos que salen del mismo punto y se abren en ángulo. El de
    # abajo pasa rozando la arista: marca hasta dónde llega el sonido directo.
    for destino in ((W - 34, 44), (W - 34, S[1] + (W - 34 - S[0]) * m)):
        c += flecha(S[0], S[1], destino[0], destino[1], grosor=1.6, punta=9)

    c += persona(S[0] - 26, 128) + persona(S[0] + 26, 128)   # los que conversan
    c += persona(404, 268) + persona(452, 268)               # los que escuchan
    return svg(W, H, c, 'Vista superior: dos personas conversan de un lado de la esquina; '
                        'el sonido dobla la arista y llega a quienes están a la vuelta')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k, (cad, dob) in OPCIONES35.items():
        open(os.path.join(OUT, f'q35_op{k}.svg'), 'w').write(fig35(cad, dob))
        print(f'escrito q35_op{k}.svg')
    open(os.path.join(OUT, 'q8_esquina.svg'), 'w').write(fig8())
    print('escrito q8_esquina.svg')
