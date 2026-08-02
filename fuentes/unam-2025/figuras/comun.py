# Piezas compartidas por los generadores de figuras de las guías UNAM 2025.
#
# Convenciones (las mismas de public/imagenes_ecoems-6/q37_circuito_paralelo.svg):
#   · todo el trazo en currentColor, para que la figura se adapte al tema
#   · rellenos tintados con fill-opacity baja, nunca macizos si compiten con el trazo
#   · en los circuitos, trazo de 1.8 dentro de un <g> y el cable INTERRUMPIDO
#     donde va la pila o un resistor, en vez de pasar por detrás
FONT = "'Latin Modern Roman', Georgia, serif"


def svg(w, h, cuerpo, comentario=''):
    return (f'<svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">\n'
            + (f'<!-- {comentario} -->\n' if comentario else '')
            + '\n'.join(cuerpo) + '\n</svg>\n')


def zig(x, y, largo=46, alto=10, n=6, vertical=False):
    """Resistor en zigzag centrado en (x, y). Devuelve solo la 'd' del path,
    para dibujarse dentro del <g> del circuito."""
    p = []
    paso = largo / n
    if vertical:
        p.append(f'M {x},{y-largo/2:.0f}')
        for i in range(n):
            p.append(f'L {x+(alto if i % 2 == 0 else -alto)},{y-largo/2+paso*(i+0.5):.0f}')
        p.append(f'L {x},{y+largo/2:.0f}')
    else:
        p.append(f'M {x-largo/2:.0f},{y}')
        for i in range(n):
            p.append(f'L {x-largo/2+paso*(i+0.5):.0f},{y+(alto if i % 2 == 0 else -alto)}')
        p.append(f'L {x+largo/2:.0f},{y}')
    return ' '.join(p)


def flecha(x1, y1, x2, y2, grosor=2.2, punta=9):
    """Segmento con punta de flecha en (x2, y2). La punta se dibuja como
    triángulo lleno y el trazo se acorta para no asomar por debajo."""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - punta * math.cos(a), y2 - punta * math.sin(a)
    px, py = -math.sin(a) * punta * 0.42, math.cos(a) * punta * 0.42
    return [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
            f'stroke="currentColor" stroke-width="{grosor}"/>',
            f'<path d="M {x2:.1f} {y2:.1f} L {bx+px:.1f} {by+py:.1f} '
            f'L {bx-px:.1f} {by-py:.1f} Z" fill="currentColor"/>']


def fuerza(x, y, sub, ancla='middle', tam=17):
    """Rótulo tipo F con subíndice de cociente: F_{B/P}. En SVG no hay KaTeX,
    así que el subíndice va como tspan más pequeño y desplazado."""
    return (f'<text x="{x}" y="{y}" font-size="{tam}" text-anchor="{ancla}" font-style="italic">'
            f'F<tspan font-size="{tam*0.62:.0f}" dy="{tam*0.26:.0f}" font-style="normal">'
            f'{sub}</tspan></text>')
