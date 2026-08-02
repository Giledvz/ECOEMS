# unam-a1-5 id 38 — mapa de coordenadas para ubicar Caracas.
#
# El reactivo evalúa LEER la retícula, no reconocer costas, así que el contorno
# va esquemático a propósito: pocos puntos, trazo limpio. Lo que sí está a
# escala exacta es la cuadrícula, y ahí es donde se resuelve la pregunta.
# Caracas queda en 10.5° N, 66.9° W → la única opción compatible es 11° N, 67° W.
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
from comun import svg

OUT = '/Users/giledvz/Documents/ECOEMS/public/imagenes_unam-a1-5'

U = 8.6                                  # píxeles por grado
LON0, LON1 = 82.0, 28.0                  # marco, en grados de longitud oeste
LAT0, LAT1 = 22.0, -22.0
MARGEN_X, MARGEN_Y = 52, 44

def P(lon, lat):
    """(longitud oeste, latitud con signo) → píxeles."""
    return (MARGEN_X + (LON0 - lon) * U, MARGEN_Y + (LAT0 - lat) * U)

# Contorno esquemático: istmo, costa caribeña, saliente atlántico y costa
# pacífica. El corte de abajo es el borde del mapa, no el fin del continente.
COSTA = [
    (82.5, 9.6), (81.0, 9.4), (79.6, 9.6), (78.5, 9.3), (77.4, 8.7),
    (76.0, 9.5), (74.2, 11.1), (71.7, 12.4), (72.2, 11.0), (71.5, 9.5),
    (70.2, 11.5), (68.2, 10.6), (67.0, 10.6), (65.2, 10.2), (62.9, 10.7),
    (62.0, 9.8), (60.0, 8.6),
    (58.2, 6.8), (55.2, 5.9), (52.3, 4.9), (51.0, 3.5), (50.0, 0.0),
    (48.5, -1.5), (44.3, -2.5), (41.0, -2.9), (38.5, -3.7), (35.2, -5.8),
    (34.8, -8.0), (35.5, -10.0), (37.0, -11.5), (38.5, -13.0), (39.0, -16.0),
    (39.5, -18.0), (40.5, -24.0),
    (70.0, -24.0),
    (70.3, -18.3), (71.4, -16.5), (73.0, -16.2), (75.2, -14.9), (77.0, -12.1),
    (78.6, -8.6), (79.9, -6.8), (81.3, -5.0), (80.9, -3.4), (80.9, -2.2),
    (80.5, -0.9), (80.0, 0.5), (78.8, 1.4), (77.9, 3.0), (77.4, 4.0),
    (77.5, 6.0), (77.6, 7.5), (78.5, 8.0), (79.5, 7.9), (81.0, 8.2), (83.5, 8.3),
]
ISLAS = [
    [(74.5, 19.9), (71.7, 19.9), (68.3, 18.6), (68.7, 18.2), (71.0, 18.2),
     (72.4, 18.0), (74.5, 18.2)],                                  # La Española
    [(67.3, 18.5), (65.6, 18.5), (65.6, 17.9), (67.3, 17.9)],      # Puerto Rico
    [(61.9, 10.8), (60.9, 10.8), (60.9, 10.0), (61.9, 10.1)],      # Trinidad
]
ANTILLAS = [(63.1, 18.0), (62.2, 16.7), (61.4, 15.4), (61.1, 14.6),
            (61.0, 13.2), (61.3, 12.2)]                            # Antillas Menores

def poly(pts, **kw):
    d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in (P(*p) for p in pts)) + ' Z'
    return (f'<path d="{d}" fill="currentColor" fill-opacity="0.13" '
            f'stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>')

def fig38():
    x0, y0 = P(LON0, LAT0)
    x1, y1 = P(LON1, LAT1)
    W, H = x1 + MARGEN_X, y1 + 26
    c = ['<defs>', f'<clipPath id="marco"><rect x="{x0:.0f}" y="{y0:.0f}" '
         f'width="{x1-x0:.0f}" height="{y1-y0:.0f}"/></clipPath>', '</defs>',
         f'<g clip-path="url(#marco)">', poly(COSTA)]
    c += [poly(i) for i in ISLAS]
    c += [f'<circle cx="{P(l, a)[0]:.1f}" cy="{P(l, a)[1]:.1f}" r="2.6" '
          f'fill="currentColor" fill-opacity="0.55"/>' for l, a in ANTILLAS]
    # la retícula va encima del contorno, que es donde se lee la respuesta
    for lon in range(30, 90, 10):
        x = P(lon, 0)[0]
        c.append(f'<line x1="{x:.1f}" y1="{y0:.0f}" x2="{x:.1f}" y2="{y1:.0f}" '
                 f'stroke="currentColor" stroke-width="0.9" stroke-opacity="0.45"/>')
    for lat in (20, 10, 0, -10, -20):
        y = P(0, lat)[1]
        c.append(f'<line x1="{x0:.0f}" y1="{y:.1f}" x2="{x1:.0f}" y2="{y:.1f}" '
                 f'stroke="currentColor" stroke-width="{1.6 if lat == 0 else 0.9}" '
                 f'stroke-opacity="{0.8 if lat == 0 else 0.45}"/>')
    c.append('</g>')
    c.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1-x0:.0f}" height="{y1-y0:.0f}" '
             f'fill="none" stroke="currentColor" stroke-width="1.8"/>')
    # Rótulos: longitudes arriba, latitudes a la izquierda
    for lon in range(30, 90, 10):
        c.append(f'<text x="{P(lon, 0)[0]:.1f}" y="{y0-10:.0f}" font-size="13" '
                 f'text-anchor="middle">{lon}°</text>')
    for lat in (20, 10, 0, -10, -20):
        c.append(f'<text x="{x0-9:.0f}" y="{P(0, lat)[1]+5:.1f}" font-size="13" '
                 f'text-anchor="end">{abs(lat)}°</text>')
    # Caracas: 10.5° N, 66.9° W
    cx, cy = P(66.9, 10.5)
    c += [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.4" fill="currentColor"/>',
          # el rótulo va debajo, tierra adentro: arriba chocaba con las Antillas
          f'<text x="{cx:.1f}" y="{cy+20:.1f}" font-size="14" font-weight="600" '
          f'text-anchor="middle">Caracas</text>']
    return svg(int(W), int(H), c,
               'Mapa con retícula de coordenadas; Caracas marcada en 10.5° N, 66.9° W')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'q38_mapa.svg'), 'w').write(fig38())
    print('escrito q38_mapa.svg')
